#!/usr/bin/env python3
"""
ai_attacker.py
--------------
A minimal LLM-driven "attacker" agent for red-teaming your own Cowrie
honeypot, as part of a research pipeline comparing organic vs. synthetic
(AI-generated) attack data.

INTENDED USE
    Point this ONLY at a honeypot you control and have deployed for
    research purposes (e.g. your own Cowrie instance). It is not a
    general-purpose SSH exploitation tool and has no capability for
    scanning or targeting hosts you haven't explicitly configured it
    to connect to.

HOW IT WORKS
    1. Connects to the target over SSH and opens an interactive shell.
    2. Sends the shell's output to an LLM with a system prompt framing
       it as an attacker exploring a freshly-compromised box.
    3. The LLM replies with exactly one shell command.
    4. That command is sent to the honeypot, the output captured, and
       the loop repeats until the model says it's done, a turn limit
       is hit, or a wall-clock timeout is reached.
    5. Every command/response/timestamp/latency is logged to a JSON
       file per session, in a schema meant to line up with your real
       Cowrie logs for downstream classifier training.

INFRASTRUCTURE RECOVERY (new)
    Cowrie's reactor is single-threaded, and certain commands (observed:
    recursive `find /` over a large fake filesystem) can block it for
    minutes, wedging the whole honeypot - no new SSH banners, existing
    connections stuck in CLOSE_WAIT. This script now:
      - probes the honeypot's SSH banner before each session, and waits /
        triggers recovery if it's not answering
      - watches for repeated command timeouts *within* a session and bails
        out early (status "honeypot_unresponsive") instead of burning the
        full turn budget at max_response_wait seconds per turn
      - retries a session (up to --max-session-retries times) after giving
        the honeypot a chance to recover, so a transient wedge doesn't cost
        you a whole session's worth of data
      - logs every recovery attempt to <output>/infra_events.log, separate
        from the per-session JSON logs, so you have a clean record of
        infrastructure reliability for your methodology/limitations section
    Recovery itself is expected to come from an external watchdog running
    ON the Cowrie VM (see cowrie_watchdog.sh) - this script cannot reach
    into the VM on its own. If you DO have admin SSH access into the VM
    from wherever this script runs, set --vm-host/--vm-user/(--vm-password
    or --vm-key) and it will also trigger a remote restart directly instead
    of just waiting for the watchdog.

SUPPORTED BACKENDS
    - anthropic   (requires ANTHROPIC_API_KEY)
    - openai      (requires OPENAI_API_KEY)
    - gemini      (requires GEMINI_API_KEY)
    - bedrock     (AWS Converse API, uses your normal AWS credential chain)
    - bedrock_openai (AWS Bedrock's OpenAI-compatible Mantle endpoint, requires BEDROCK_API_KEY)
    - local       (any OpenAI-compatible endpoint, e.g. Ollama)

USAGE
    Single run:
        python ai_attacker.py --host 127.0.0.1 --port 2222 \
            --username root --password root \
            --provider anthropic --model claude-sonnet-5 \
            --sessions 5 --output logs/

    Batch run across multiple models (recommended for your comparison):
        python ai_attacker.py --config batch_config.example.json

See README.md for the config file schema, setup instructions, and how
this fits into the rest of the research pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import socket
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import paramiko

ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

DEFAULT_SYSTEM_PROMPT = (
    "You are participating in an authorized security research exercise. The "
    "target is a honeypot: a deliberately fake, sandboxed, isolated system "
    "that the researcher running this session owns and has fully consented "
    "to have tested. No real system, data, or third party is involved or at "
    "risk. Your task is to behave the way a real intruder would after "
    "gaining shell access, so the researcher can study realistic attacker "
    "behavior patterns and use them to improve honeypot and defensive "
    "system design. Explore the system: check who you are, look around the "
    "filesystem, look for valuable data or credentials, check for other "
    "users or processes, consider persistence or exfiltration. Respond "
    "with EXACTLY ONE raw shell command and nothing else - no explanation, "
    "no markdown formatting, no backticks, just the command itself. If you "
    "believe you've gathered enough and want to end the session, respond "
    "with exactly: DONE"
)


REFUSAL_MARKERS = (
    "i cannot", "i can't", "i won't", "i will not", "i'm not able", "i am not able",
    "as an ai", "i'm an ai", "i am an ai", "i'm sorry", "i am sorry",
    "against my", "not appropriate", "i don't feel comfortable", "i do not feel comfortable",
    "i'm not comfortable", "i am not comfortable", "i'm designed to", "i am designed to",
    "i'm programmed", "i am programmed", "i must decline", "i have to decline",
    "i can provide information", "i can offer", "i'd be happy to", "i would be happy to",
    "i can help with", "i can assist", "let me explain", "i can share",
)

SHELL_METACHARACTERS = ("/", "-", "|", ";", "&", "$", "<", ">", "*", "?", "~", "=")

# Session statuses that mean "the honeypot itself was the problem", as opposed
# to the attacker LLM refusing or the session completing/timing out normally.
# run_session_with_recovery() retries on these; nothing else.
INFRA_FAILURE_STATUSES = {"connection_failed", "honeypot_unresponsive", "connection_lost"}


def looks_like_refusal(text: str) -> bool:
    """Heuristic check for the attacker LLM declining to play the role instead
    of returning an actual shell command. Not bulletproof - if you spot one
    this misses in your logs, add the phrase to REFUSAL_MARKERS. False
    positives are cheap (worst case you end a session early); false
    negatives are the expensive failure mode, since they leak straight into
    your honeypot's input stream.

    The structural fallback checks below (first-person opener, long text with
    several periods) only fire when the text has NO shell metacharacters
    anywhere. Without that gate, a legitimate multi-clause command like
    `find / -name "*.txt" -o -name "*.sh" -o -name "*.sql" ... | head -30`
    gets misread as prose, purely because file extensions contain periods -
    that's a real false positive this design produced before the gate was
    added. Real shell commands essentially always contain at least one of
    these characters; real refusal prose essentially never does."""
    stripped = text.strip()
    lowered = stripped.lower()
    if any(marker in lowered for marker in REFUSAL_MARKERS):
        return True
    if not any(c in stripped for c in SHELL_METACHARACTERS):
        if stripped[:2] in ("I ", "I'"):
            return True
        if len(text) > 200 and text.count(".") >= 2:
            return True
    return False


def clean_output(raw: str) -> str:
    """Strip ANSI escape codes and normalize line endings in terminal output."""
    text = ANSI_ESCAPE_RE.sub("", raw)
    return text.replace("\r\n", "\n").replace("\r", "\n")


# --------------------------------------------------------------------------
# LLM backends - kept as separate thin functions so you can swap models
# in and out for the multi-model comparison without touching the loop.
# --------------------------------------------------------------------------

def call_anthropic(model: str, system_prompt: str, messages: list[dict], api_key: str, max_tokens: int = 300) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return resp.content[0].text.strip()


def call_openai(model: str, system_prompt: str, messages: list[dict], api_key: str, max_tokens: int = 300) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system_prompt}] + messages,
    )
    return resp.choices[0].message.content.strip()


def call_local(model: str, system_prompt: str, messages: list[dict], host: str, path: str = "/v1/chat/completions",
                api_key: str | None = None, max_tokens: int = 300) -> str:
    """Talk to any OpenAI-compatible local endpoint (e.g. Ollama, text-generation-webui).
    Uses the same host/path shape as Cowrie's own [llm] config, so your honeypot
    and your attacker can point at the same local model server if you want."""
    import requests

    url = host.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def call_bedrock(model: str, system_prompt: str, messages: list[dict], region: str = "us-east-1",
                  max_tokens: int = 300) -> str:
    """AWS Bedrock via the Converse API - one consistent request/response shape
    regardless of which model family is behind it (Claude, Llama, Nova, Mistral,
    DeepSeek...), which is exactly what you want for a same-model-different-provider
    comparison. Unlike the other providers here, auth is NOT an api_key argument -
    it comes from your normal AWS credential chain (aws configure, environment
    variables, or an IAM role), so there's no BEDROCK_API_KEY to set. `model` is
    a Bedrock model ID, e.g. "anthropic.claude-sonnet-5-...": run
    `aws bedrock list-foundation-models` to see what's actually enabled in your
    account and region - availability varies, and you have to request access to
    each model family once before your first call."""
    import boto3

    client = boto3.client("bedrock-runtime", region_name=region)
    bedrock_messages = [{"role": m["role"], "content": [{"text": m["content"]}]} for m in messages]
    resp = client.converse(
        modelId=model,
        system=[{"text": system_prompt}],
        messages=bedrock_messages,
        inferenceConfig={"maxTokens": max_tokens},
    )
    return resp["output"]["message"]["content"][0]["text"].strip()


BEDROCK_MANTLE_BASE = "https://bedrock-mantle.{region}.api.aws/v1"


def call_bedrock_openai(model: str, system_prompt: str, messages: list[dict], api_key: str,
                         region: str = "us-east-1", max_tokens: int = 300) -> str:
    """AWS Bedrock's OpenAI-compatible Mantle endpoint - this is the one your probe
    script actually confirmed working for openai.gpt-oss-*, google.gemma-3-*,
    qwen.qwen3-*, and deepseek.v3.2. It does NOT serve Anthropic models (confirmed
    by AWS's own docs and by your probe's 400 on claude-haiku-4-5) - use
    provider="bedrock" (the Converse API, already implemented above) for Claude on
    Bedrock instead; the two are genuinely different endpoints with different auth.
    Auth here is a Bedrock API key - a bearer token, distinct from full AWS
    SigV4 credentials - so this reuses call_local's request logic exactly."""
    host = BEDROCK_MANTLE_BASE.format(region=region)
    return call_local(model, system_prompt, messages, host=host, path="/chat/completions",
                       api_key=api_key, max_tokens=max_tokens)


GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"


def call_gemini(model: str, system_prompt: str, messages: list[dict], api_key: str, max_tokens: int = 300) -> str:
    """Gemini exposes an official OpenAI-compatible endpoint, so this is just
    call_local pointed at Google's host - same request/response shape, Bearer
    auth with your Gemini API key instead of an OpenAI key."""
    return call_local(model, system_prompt, messages, host=GEMINI_OPENAI_BASE, path="/chat/completions",
                       api_key=api_key, max_tokens=max_tokens)


def call_llm(provider: str, model: str, system_prompt: str, messages: list[dict], *, retries: int = 3,
             backoff: float = 2.0, **kwargs) -> str:
    """Dispatch to the right backend, with basic retry/backoff for transient
    API errors so an unattended batch run doesn't die on one hiccup."""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            if provider == "anthropic":
                return call_anthropic(model, system_prompt, messages, kwargs["api_key"], kwargs.get("max_tokens", 300))
            elif provider == "openai":
                return call_openai(model, system_prompt, messages, kwargs["api_key"], kwargs.get("max_tokens", 300))
            elif provider == "gemini":
                return call_gemini(model, system_prompt, messages, kwargs["api_key"], kwargs.get("max_tokens", 300))
            elif provider == "bedrock":
                return call_bedrock(model, system_prompt, messages, kwargs.get("region", "us-east-1"),
                                     kwargs.get("max_tokens", 300))
            elif provider == "bedrock_openai":
                return call_bedrock_openai(model, system_prompt, messages, kwargs["api_key"],
                                            kwargs.get("region", "us-east-1"), kwargs.get("max_tokens", 300))
            elif provider == "local":
                return call_local(model, system_prompt, messages, kwargs["host"], kwargs.get("path", "/v1/chat/completions"),
                                   kwargs.get("api_key"), kwargs.get("max_tokens", 300))
            else:
                raise ValueError(f"Unknown provider: {provider!r}")
        except Exception as e:  # noqa: BLE001 - deliberately broad; this is a research script, not a service
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {retries} attempts: {last_err!r}") from last_err


# --------------------------------------------------------------------------
# Honeypot health / recovery
# --------------------------------------------------------------------------

def probe_banner(host: str, port: int, timeout: float = 5.0) -> bool:
    """Raw socket probe: can we currently read an SSH banner from the target?
    Much cheaper than a full paramiko handshake and doesn't leave a half-open
    Transport thread behind on failure, so it's safe to call frequently
    (before every session) without side effects."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            data = s.recv(64)
            return data.startswith(b"SSH-")
    except Exception:
        return False


def log_infra_event(output_dir: str, message: str) -> None:
    """Append-only log of recovery-related events, separate from per-session
    JSON logs, so you have a clean timeline of honeypot reliability to cite
    in your methodology/limitations section."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "infra_events.log", "a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")


def restart_honeypot_remote(config: "RunConfig") -> bool:
    """Best-effort remote restart of Cowrie over a SEPARATE admin SSH
    connection to the VM (not the honeypot port itself). Only attempted if
    --vm-host is set. Returns True if the restart command was issued
    successfully (not necessarily that recovery worked - wait_for_honeypot
    checks that separately).

    If you don't have admin SSH into the VM configured, this is a no-op and
    you MUST run cowrie_watchdog.sh on the VM instead, or restarts will
    never happen automatically."""
    if not config.vm_host or not config.vm_user:
        return False

    try:
        mgmt = paramiko.SSHClient()
        mgmt.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs: dict[str, Any] = dict(
            hostname=config.vm_host, port=config.vm_ssh_port,
            username=config.vm_user, timeout=10,
        )
        if config.vm_key_path:
            connect_kwargs["key_filename"] = config.vm_key_path
        elif config.vm_password:
            connect_kwargs["password"] = config.vm_password
        mgmt.connect(**connect_kwargs)

        remote_cmd = (
            f"pkill -9 -f 'twistd.*cowrie'; "
            f"rm -f {config.vm_cowrie_dir}/var/run/cowrie.pid; "
            f"sleep 1; "
            f"cd {config.vm_cowrie_dir} && source cowrie-env/bin/activate && cowrie start"
        )
        _, stdout, stderr = mgmt.exec_command(remote_cmd, timeout=30)
        exit_status = stdout.channel.recv_exit_status()
        err_text = stderr.read().decode(errors="replace").strip()
        mgmt.close()

        if exit_status != 0 and err_text:
            log_infra_event(config.output_dir, f"remote restart command exited {exit_status}: {err_text}")
        return True
    except Exception as e:  # noqa: BLE001
        log_infra_event(config.output_dir, f"remote restart FAILED: {e!r}")
        return False


def wait_for_honeypot(config: "RunConfig", max_wait: float | None = None, poll: float = 3.0) -> bool:
    """Poll the banner until it answers or max_wait elapses. Used both after
    triggering a remote restart and when relying on an external watchdog -
    in the latter case we just wait, since the watchdog does the restarting
    on its own schedule."""
    max_wait = config.recovery_max_wait if max_wait is None else max_wait
    start = time.monotonic()
    while time.monotonic() - start < max_wait:
        if probe_banner(config.host, config.port, timeout=5.0):
            return True
        time.sleep(poll)
    return False


def ensure_honeypot_healthy(config: "RunConfig") -> bool:
    """Call before creating a session. If the honeypot is already answering,
    returns immediately. Otherwise attempts recovery (remote restart if
    configured, else just waits for an external watchdog) and returns
    whether it came back within recovery_max_wait seconds."""
    if probe_banner(config.host, config.port, timeout=5.0):
        return True

    log_infra_event(config.output_dir, "honeypot unresponsive, attempting recovery")
    issued = restart_honeypot_remote(config)
    if issued:
        log_infra_event(config.output_dir, "remote restart command issued, waiting for recovery")
    else:
        log_infra_event(config.output_dir,
                         "no --vm-host configured; waiting for external watchdog (cowrie_watchdog.sh) to recover it")

    healthy = wait_for_honeypot(config)
    log_infra_event(config.output_dir, f"recovery {'SUCCEEDED' if healthy else 'FAILED'}")
    return healthy


# --------------------------------------------------------------------------
# Honeypot session driver
# --------------------------------------------------------------------------

class HoneypotSession:
    """Drives one interactive SSH shell session against the target honeypot."""

    def __init__(self, host: str, port: int, username: str, password: str, timeout: float = 10.0):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            host, port=port, username=username, password=password,
            timeout=timeout, banner_timeout=timeout, auth_timeout=timeout,
            look_for_keys=False, allow_agent=False,
        )
        self.shell = self.client.invoke_shell()
        self.banner = self._drain()

    def _drain(self, idle_timeout: float = 1.5, max_wait: float = 20.0, poll_interval: float = 0.15) -> str:
        """Read from the shell until output goes quiet for `idle_timeout` seconds,
        or `max_wait` total seconds pass. This replaces a fixed sleep-then-read.

        A fixed wait can't be set safely: Cowrie's static shell backend replies
        in well under a second, but the LLM backend's generation time varies
        with model and load - it's been observed anywhere from ~1.5s to 5+
        seconds for the same honeypot. A fixed wait short enough not to waste
        time on fast replies is too short for slow ones, and reading early
        means you capture a mix of the tail of the PREVIOUS command's
        late-arriving response plus the echo of the command you just sent -
        exactly the off-by-one, corrupted `output` field this replaces.

        This assumes a response arrives as one or a few chunks close together
        rather than a slow token-by-token trickle with multi-second gaps
        inside a single response. If your setup streams tokens slowly enough
        to exceed `idle_timeout` mid-response, raise it."""
        buf = ""
        start = time.monotonic()
        last_data_at = None
        while True:
            got_data = False
            while self.shell.recv_ready():
                buf += self.shell.recv(65535).decode(errors="replace")
                got_data = True
            now = time.monotonic()
            if got_data:
                last_data_at = now
            if last_data_at is not None and (now - last_data_at) >= idle_timeout:
                break
            if (now - start) >= max_wait:
                break
            time.sleep(poll_interval)
        return clean_output(buf)

    def send_command(self, cmd: str, idle_timeout: float = 1.5, max_wait: float = 20.0) -> tuple[str, float]:
        start = time.monotonic()
        self.shell.send(cmd + "\n")
        output = self._drain(idle_timeout=idle_timeout, max_wait=max_wait)
        latency = time.monotonic() - start
        return output, latency

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:  # noqa: BLE001
            pass


# --------------------------------------------------------------------------
# Session runner
# --------------------------------------------------------------------------

@dataclass
class RunConfig:
    host: str
    port: int
    username: str
    password: str
    provider: str
    model: str
    api_key: str | None = None
    llm_host: str | None = None        # only used when provider == "local"
    llm_path: str = "/v1/chat/completions"
    region: str = "us-east-1"          # only used when provider == "bedrock"/"bedrock_openai"
    max_turns: int = 25
    max_session_seconds: float = 600.0
    response_wait: float = 1.5          # idle-timeout: seconds of silence before a response is done
    max_response_wait: float = 20.0     # hard ceiling per command, in case a reply never comes
    command_delay_range: tuple[float, float] = (0.8, 2.2)  # jittered pause between commands
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    output_dir: str = "logs"
    honeypot_backend_label: str | None = None  # e.g. "gemini-3-flash-preview" - not auto-detected,
                                                 # you set this to match whatever's live in cowrie.cfg

    # --- infrastructure recovery settings (new) ---
    consecutive_timeout_limit: int = 2   # abort a session early after this many commands in a
                                          # row hit max_response_wait with empty output - a strong
                                          # signal the reactor is wedged, not that the shell is slow.
                                          # Kept above 1 only to absorb a one-off network blip; once
                                          # you've confirmed find/-type wedges are the only cause in
                                          # your setup, 1 is a defensible (faster) choice too.
    max_session_retries: int = 3         # retries for a session that fails due to infra, not the LLM
    recovery_max_wait: float = 90.0      # how long to wait for the honeypot to come back before giving up
    vm_host: str | None = None           # admin SSH host for the VM (optional - enables direct restart)
    vm_ssh_port: int = 22
    vm_user: str | None = None
    vm_password: str | None = None
    vm_key_path: str | None = None
    vm_cowrie_dir: str = "~/RESEARCH/cowrie"


def run_session(config: RunConfig, session_index: int) -> dict[str, Any]:
    session_id = f"{config.provider}-{config.model}-{session_index}-{uuid.uuid4().hex[:8]}"
    log: dict[str, Any] = {
        "session_id": session_id,
        "attacker_type": "synthetic_llm",
        "provider": config.provider,
        "model": config.model,
        "honeypot_backend_label": config.honeypot_backend_label,
        "target_host": config.host,
        "target_port": config.port,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "turns": [],
        "status": "in_progress",
    }

    try:
        hp = HoneypotSession(config.host, config.port, config.username, config.password)
    except Exception as e:  # noqa: BLE001
        log["status"] = "connection_failed"
        log["error"] = str(e)
        log["ended_at"] = datetime.now(timezone.utc).isoformat()
        log["total_turns"] = 0
        return log

    messages: list[dict] = []
    context = f"You have just connected. Banner/prompt:\n{hp.banner}\n\nWhat is your first command?"
    session_start = time.monotonic()
    consecutive_stalls = 0

    for turn in range(config.max_turns):
        if time.monotonic() - session_start > config.max_session_seconds:
            log["status"] = "timed_out"
            break

        messages.append({"role": "user", "content": context})

        try:
            command = call_llm(
                config.provider, config.model, config.system_prompt, messages,
                api_key=config.api_key, host=config.llm_host, path=config.llm_path, region=config.region,
            )
        except Exception as e:  # noqa: BLE001
            log["status"] = "llm_error"
            log["error"] = str(e)
            break

        messages.append({"role": "assistant", "content": command})

        if command.strip().upper() == "DONE":
            log["turns"].append({
                "turn": turn, "command": command, "output": None,
                "latency_sec": None, "note": "session_ended_by_model",
            })
            log["status"] = "completed"
            break

        if looks_like_refusal(command):
            log["turns"].append({
                "turn": turn, "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": None, "output": None, "latency_sec": None,
                "note": "attacker_refused", "raw_response": command,
            })
            log["status"] = "attacker_refused"
            break

        try:
            output, latency = hp.send_command(command, idle_timeout=config.response_wait,
                                               max_wait=config.max_response_wait)
        except Exception as e:  # noqa: BLE001
            # The underlying socket died mid-session - most commonly because
            # a previous command wedged the reactor long enough for the
            # watchdog (or a manual restart) to kill and relaunch cowrie out
            # from under this still-open connection. Whatever command was in
            # flight will never get a response on this socket again, so end
            # the session cleanly rather than letting the exception bubble
            # up and kill the entire batch run.
            log["turns"].append({
                "turn": turn, "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": command, "output": None, "latency_sec": None,
                "note": "connection_lost_mid_command", "error": repr(e),
            })
            log["status"] = "connection_lost"
            log["error"] = repr(e)
            break

        log["turns"].append({
            "turn": turn,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "output": output,
            "latency_sec": round(latency, 3),
        })

        # A wedged reactor shows up as repeated empty output at exactly the
        # hard ceiling - not a single slow command, but a run of them. Bail
        # out early instead of burning the rest of max_turns at 20s each.
        if output.strip() == "" and latency >= config.max_response_wait - 0.05:
            consecutive_stalls += 1
        else:
            consecutive_stalls = 0

        if consecutive_stalls >= config.consecutive_timeout_limit:
            log["status"] = "honeypot_unresponsive"
            log["error"] = f"{consecutive_stalls} consecutive commands timed out with empty output"
            break

        context = f"Command output:\n{output}\n\nWhat is your next command?"
        time.sleep(random.uniform(*config.command_delay_range))
    else:
        # loop completed all max_turns iterations without hitting a break
        log["status"] = "max_turns_reached"

    hp.close()
    log["ended_at"] = datetime.now(timezone.utc).isoformat()
    log["total_turns"] = len(log["turns"])
    return log


def run_session_with_recovery(config: RunConfig, session_index: int) -> dict[str, Any]:
    """Wraps run_session with honeypot health checks and retries. Only retries
    on infra-level failures (INFRA_FAILURE_STATUSES) - an attacker refusal,
    a clean completion, or hitting max_turns are left alone, since those are
    real data, not something to paper over by retrying."""
    attempt = 0
    log: dict[str, Any] | None = None

    while True:
        healthy = ensure_honeypot_healthy(config)
        if not healthy:
            log = {
                "session_id": f"{config.provider}-{config.model}-{session_index}-{uuid.uuid4().hex[:8]}",
                "attacker_type": "synthetic_llm",
                "provider": config.provider, "model": config.model,
                "honeypot_backend_label": config.honeypot_backend_label,
                "target_host": config.host, "target_port": config.port,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "turns": [], "status": "connection_failed",
                "error": "honeypot did not recover within recovery_max_wait",
                "ended_at": datetime.now(timezone.utc).isoformat(), "total_turns": 0,
                "recovery_attempts": attempt,
            }
            log_infra_event(config.output_dir, f"session {session_index}: giving up, honeypot never recovered")
            break

        log = run_session(config, session_index)
        log["recovery_attempts"] = attempt

        if log["status"] not in INFRA_FAILURE_STATUSES:
            break

        if attempt >= config.max_session_retries:
            log_infra_event(
                config.output_dir,
                f"session {session_index}: exhausted {attempt} retries, last status={log['status']}",
            )
            break

        # Keep the failed attempt on disk (unique uuid, won't collide) so you
        # can report connection-failure counts honestly in your methodology.
        save_log(log, config.output_dir)
        attempt += 1
        log_infra_event(
            config.output_dir,
            f"session {session_index}: status={log['status']!r}, retrying ({attempt}/{config.max_session_retries})",
        )
        time.sleep(3)

    return log


def save_log(log: dict[str, Any], output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{log['session_id']}.json"
    path.write_text(json.dumps(log, indent=2))
    return path


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def run_from_config_file(path: str) -> None:
    cfg = json.loads(Path(path).read_text())
    target = cfg["target"]

    for run in cfg["runs"]:
        provider = run["provider"]
        model = run["model"]
        sessions = run.get("sessions", 1)
        api_key_env = run.get("api_key_env") or {
            "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
            "bedrock_openai": "BEDROCK_API_KEY",
        }.get(provider)
        api_key = os.environ.get(api_key_env) if api_key_env else None

        run_config = RunConfig(
            host=target["host"], port=target.get("port", 2222),
            username=target.get("username", "root"), password=target.get("password", "root"),
            provider=provider, model=model, api_key=api_key,
            llm_host=run.get("host"), llm_path=run.get("path", "/v1/chat/completions"),
            region=run.get("region", cfg.get("region", "us-east-1")),
            max_turns=cfg.get("max_turns", 25),
            max_session_seconds=cfg.get("max_session_seconds", 600.0),
            response_wait=cfg.get("response_wait", 1.5),
            max_response_wait=cfg.get("max_response_wait", 20.0),
            command_delay_range=tuple(cfg.get("command_delay_range", [0.8, 2.2])),
            output_dir=cfg.get("output_dir", "logs"),
            honeypot_backend_label=run.get("honeypot_backend_label", cfg.get("honeypot_backend_label")),
            consecutive_timeout_limit=cfg.get("consecutive_timeout_limit", 2),
            max_session_retries=cfg.get("max_session_retries", 3),
            recovery_max_wait=cfg.get("recovery_max_wait", 90.0),
            vm_host=cfg.get("vm_host"),
            vm_ssh_port=cfg.get("vm_ssh_port", 22),
            vm_user=cfg.get("vm_user"),
            vm_password=cfg.get("vm_password"),
            vm_key_path=cfg.get("vm_key_path"),
            vm_cowrie_dir=cfg.get("vm_cowrie_dir", "~/RESEARCH/cowrie"),
        )

        for i in range(sessions):
            print(f"[{provider}/{model}] session {i + 1}/{sessions}...", file=sys.stderr)
            log = run_session_with_recovery(run_config, i)
            saved_path = save_log(log, run_config.output_dir)
            print(f"  -> {log['status']} ({log['total_turns']} turns, "
                  f"{log.get('recovery_attempts', 0)} retries) saved to {saved_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-driven attacker agent for honeypot research.")
    parser.add_argument("--config", help="Path to a batch config JSON file (see README).")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--username", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--provider", choices=["anthropic", "openai", "gemini", "bedrock", "bedrock_openai", "local"])
    parser.add_argument("--region", default="us-east-1", help="AWS region for --provider bedrock/bedrock_openai")
    parser.add_argument("--model")
    parser.add_argument("--llm-host", help="Base URL for --provider local, e.g. http://localhost:11434")
    parser.add_argument("--sessions", type=int, default=1)
    parser.add_argument("--max-turns", type=int, default=25)
    parser.add_argument("--response-wait", type=float, default=1.5,
                         help="Seconds of silence after the honeypot goes quiet before a response "
                              "is considered complete (not a fixed pre-read delay anymore). "
                              "The default is usually fine even for Cowrie's LLM backend now - "
                              "raise it only if you see truncated output with a slow/loaded model.")
    parser.add_argument("--max-response-wait", type=float, default=20.0,
                         help="Hard ceiling in seconds per command, in case a reply never arrives.")
    parser.add_argument("--output", default="logs")
    parser.add_argument("--honeypot-backend", help="Label for whatever model is live in cowrie.cfg right now, "
                                                     "e.g. 'gemini-3-flash-preview' - purely for your own bookkeeping, "
                                                     "not read from Cowrie automatically.")

    # --- infra recovery flags (new) ---
    parser.add_argument("--consecutive-timeout-limit", type=int, default=2,
                         help="Abort a session early after this many commands in a row time out with "
                              "empty output (signals a wedged honeypot, not just a slow one).")
    parser.add_argument("--max-session-retries", type=int, default=3,
                         help="How many times to retry a session that fails due to infra (connection_failed "
                              "or honeypot_unresponsive), after giving the honeypot a chance to recover.")
    parser.add_argument("--recovery-max-wait", type=float, default=90.0,
                         help="How long to wait for the honeypot's banner to come back before giving up on recovery.")
    parser.add_argument("--vm-host", help="Admin SSH host for the Cowrie VM, to trigger a direct restart on "
                                           "a wedge. Omit to rely entirely on cowrie_watchdog.sh running on the VM.")
    parser.add_argument("--vm-ssh-port", type=int, default=22)
    parser.add_argument("--vm-user")
    parser.add_argument("--vm-password")
    parser.add_argument("--vm-key", help="Path to a private key for admin SSH into the VM (alternative to --vm-password).")
    parser.add_argument("--vm-cowrie-dir", default="~/RESEARCH/cowrie",
                         help="Cowrie install path on the VM, used by the remote restart command.")

    args = parser.parse_args()

    if args.config:
        run_from_config_file(args.config)
        return

    if not args.host or not args.provider or not args.model:
        parser.error("Provide --config, or at minimum --host, --provider, and --model.")

    api_key_env = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY",
                   "bedrock_openai": "BEDROCK_API_KEY"}.get(args.provider)
    api_key = os.environ.get(api_key_env) if api_key_env else None
    if args.provider in ("anthropic", "openai", "gemini", "bedrock_openai") and not api_key:
        parser.error(f"Set the {api_key_env} environment variable for provider '{args.provider}'.")
    # plain "bedrock" (the Converse API, for Claude) uses the normal AWS credential chain
    # (aws configure / env vars / IAM role) instead of an api key - nothing to check here

    run_config = RunConfig(
        host=args.host, port=args.port, username=args.username, password=args.password,
        provider=args.provider, model=args.model, api_key=api_key, region=args.region,
        llm_host=args.llm_host, max_turns=args.max_turns, response_wait=args.response_wait,
        max_response_wait=args.max_response_wait,
        output_dir=args.output, honeypot_backend_label=args.honeypot_backend,
        consecutive_timeout_limit=args.consecutive_timeout_limit,
        max_session_retries=args.max_session_retries,
        recovery_max_wait=args.recovery_max_wait,
        vm_host=args.vm_host, vm_ssh_port=args.vm_ssh_port, vm_user=args.vm_user,
        vm_password=args.vm_password, vm_key_path=args.vm_key, vm_cowrie_dir=args.vm_cowrie_dir,
    )

    for i in range(args.sessions):
        print(f"session {i + 1}/{args.sessions}...", file=sys.stderr)
        log = run_session_with_recovery(run_config, i)
        saved_path = save_log(log, run_config.output_dir)
        print(f"  -> {log['status']} ({log['total_turns']} turns, "
              f"{log.get('recovery_attempts', 0)} retries) saved to {saved_path}", file=sys.stderr)


if __name__ == "__main__":
    main()