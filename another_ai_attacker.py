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

SUPPORTED BACKENDS
    - anthropic   (requires ANTHROPIC_API_KEY)
    - openai      (requires OPENAI_API_KEY)
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
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import paramiko

ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Matches a trailing "user@host:cwd# " or "...$ " shell prompt. Used to detect
# that a command's response is truly finished, rather than guessing from a
# quiet period - see the comment in HoneypotSession._drain for why the idle
# timeout alone isn't reliable.
PROMPT_RE = re.compile(r"[^\s@]+@[^\s:]+:\S*[#$]\s*$")

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
BEDROCK_MANTLE_ANTHROPIC_URL = "https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages"


def call_bedrock_mantle_anthropic(model: str, system_prompt: str, messages: list[dict], api_key: str,
                                   region: str = "us-east-1", max_tokens: int = 300) -> str:
    """Claude models on Mantle are NOT served over chat completions - that 400
    validation_error ("does not support the '/v1/chat/completions' API") was
    telling you the truth. They're on Mantle's own native Anthropic Messages
    route instead: a different path, a required anthropic-version header, and
    the Anthropic wire format (system as a top-level field, not a system-role
    message in the list). Model IDs on Mantle are sent verbatim - no "us."
    cross-region prefix and no "-v1:0" version suffix, unlike Converse IDs."""
    import requests

    url = BEDROCK_MANTLE_ANTHROPIC_URL.format(region=region)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"].strip()


def call_bedrock_openai(model: str, system_prompt: str, messages: list[dict], api_key: str,
                         region: str = "us-east-1", max_tokens: int = 300) -> str:
    """AWS Bedrock's Mantle endpoint. Auth here is a Bedrock API key - a bearer
    token, distinct from full AWS SigV4 credentials used by call_bedrock above.

    Mantle serves two different wire formats depending on model family: Claude
    (anthropic.*) uses its native Messages route (call_bedrock_mantle_anthropic),
    everything else (OpenAI open-weight, Gemma, Qwen, DeepSeek, ...) uses
    OpenAI-compatible chat completions. This dispatches on the model ID prefix
    so callers don't have to care which family they're pointed at."""
    if model.startswith("anthropic."):
        return call_bedrock_mantle_anthropic(model, system_prompt, messages, api_key, region, max_tokens)
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

    def _drain(self, marker: str | None = None, idle_timeout: float = 6.0, max_wait: float = 30.0,
               poll_interval: float = 0.15) -> str:
        """Read from the shell until a completion signal is seen, or `max_wait`
        total seconds pass."""
        buf = ""
        start = time.monotonic()
        last_data_at = None
        marker_re = re.compile(rf"(?m)^{re.escape(marker)}\s*$") if marker else None
        while True:
            got_data = False
            while self.shell.recv_ready():
                buf += self.shell.recv(65535).decode(errors="replace")
                got_data = True
            now = time.monotonic()
            if got_data:
                last_data_at = now
                if marker_re is not None:
                    if marker_re.search(buf):
                        break
                elif PROMPT_RE.search(buf[-200:]):
                    break
            if last_data_at is not None and (now - last_data_at) >= idle_timeout:
                break
            if (now - start) >= max_wait:
                break
            time.sleep(poll_interval)
        return clean_output(buf)

    def send_command(self, cmd: str, idle_timeout: float = 6.0, max_wait: float = 30.0) -> tuple[str, float]:
        """Sends `cmd` and a unique completion marker as ONE combined line
        (`cmd ; echo MARKER`), not two separate .send() calls.

        This matters more than it looks. Cowrie's LLM backend treats each
        newline-terminated line as its own independent turn to generate a
        response for. Sending the marker as a second, separate line meant the
        backend had two unrelated things to answer: the real command (which
        can take 1.5-3+ seconds to generate) and a trivial `echo MARKER`
        (answered almost instantly, since echoing literal text needs no real
        reasoning). The instant one would win the race, _drain() would see
        the marker and return immediately, and the real command's output -
        still being generated - would arrive AFTER this function had already
        returned, landing in whatever the NEXT command's read window happened
        to be instead. That's what was corrupting sessions: turn N showing
        just the command echoed back with no real content, and turn N+1
        showing a garbled mix of turn N's late output, turn N+1's own output,
        and stray marker lines.

        Chaining them into one line with `;` means the backend has exactly
        ONE thing to generate a response for - the real command's output
        followed by the marker - so there's nothing left to race. `;` (not
        `&&`) is deliberate: the marker must appear whether the command
        "succeeds" or not, or a failing command silently hangs the read until
        max_wait."""
        start = time.monotonic()
        marker = f"__CMDDONE_{uuid.uuid4().hex[:8]}__"
        self.shell.send(f"{cmd} ; echo {marker}\n")
        output = self._drain(marker, idle_timeout=idle_timeout, max_wait=max_wait)
        latency = time.monotonic() - start
        output = re.sub(rf"(?m)^{re.escape(cmd)} ; echo {re.escape(marker)}\s*$", "", output)
        output = re.sub(rf"(?m)^{re.escape(marker)}\s*$", "", output)
        return output, latency

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:  # noqa: BLE001
            pass


@dataclass
class RunConfig:
    host: str
    port: int
    username: str
    password: str
    provider: str
    model: str
    api_key: str | None = None
    llm_host: str | None = None
    llm_path: str = "/v1/chat/completions"
    region: str = "us-east-1"
    max_turns: int = 20
    max_session_seconds: float = 600.0
    response_wait: float = 6.0
    max_response_wait: float = 30.0
    command_delay_range: tuple[float, float] = (0.8, 2.2)
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    output_dir: str = "logs"
    honeypot_backend_label: str | None = None


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
        except Exception as e:  # noqa: BLE001 - the honeypot side can drop the connection
            # mid-session (observed as paramiko's "Socket is closed") for reasons outside
            # this script's control - an internal timeout on the honeypot's own call to
            # its backend model, resource limits after many consecutive sessions, etc.
            # Without this, that one dropped connection took the whole batch process down
            # with it, silently losing every session still queued behind it.
            log["turns"].append({
                "turn": turn, "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": command, "output": None, "latency_sec": None,
                "note": "connection_lost_mid_command",
            })
            log["status"] = "connection_lost"
            log["error"] = str(e)
            break

        log["turns"].append({
            "turn": turn,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "output": output,
            "latency_sec": round(latency, 3),
        })
        context = f"Command output:\n{output}\n\nWhat is your next command?"

        time.sleep(random.uniform(*config.command_delay_range))
    else:
        log["status"] = "max_turns_reached"

    hp.close()
    log["ended_at"] = datetime.now(timezone.utc).isoformat()
    log["total_turns"] = len(log["turns"])
    return log


def _safe_filename(session_id: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", session_id)


def save_log(log: dict[str, Any], output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{_safe_filename(log['session_id'])}.json"
    path.write_text(json.dumps(log, indent=2))
    return path


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
            response_wait=cfg.get("response_wait", 6.0),
            max_response_wait=cfg.get("max_response_wait", 30.0),
            command_delay_range=tuple(cfg.get("command_delay_range", [0.8, 2.2])),
            output_dir=cfg.get("output_dir", "logs"),
            honeypot_backend_label=run.get("honeypot_backend_label", cfg.get("honeypot_backend_label")),
        )

        for i in range(sessions):
            print(f"[{provider}/{model}] session {i + 1}/{sessions}...", file=sys.stderr)
            log = run_session(run_config, i)
            saved_path = save_log(log, run_config.output_dir)
            print(f"  -> {log['status']} ({log['total_turns']} turns) saved to {saved_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-driven attacker agent for honeypot research.")
    parser.add_argument("--config", help="Path to a batch config JSON file (see README).")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--username", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--provider", choices=["anthropic", "openai", "gemini", "bedrock", "bedrock_openai", "local"])
    parser.add_argument("--region", default="us-east-1", help="AWS region for --provider bedrock")
    parser.add_argument("--model")
    parser.add_argument("--llm-host", help="Base URL for --provider local, e.g. http://localhost:11434")
    parser.add_argument("--sessions", type=int, default=1)
    parser.add_argument("--max-turns", type=int, default=25)
    parser.add_argument("--response-wait", type=float, default=6.0)
    parser.add_argument("--max-response-wait", type=float, default=30.0)
    parser.add_argument("--output", default="logs")
    parser.add_argument("--honeypot-backend")
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

    run_config = RunConfig(
        host=args.host, port=args.port, username=args.username, password=args.password,
        provider=args.provider, model=args.model, api_key=api_key, region=args.region,
        llm_host=args.llm_host, max_turns=args.max_turns, response_wait=args.response_wait,
        max_response_wait=args.max_response_wait,
        output_dir=args.output, honeypot_backend_label=args.honeypot_backend,
    )

    for i in range(args.sessions):
        print(f"session {i + 1}/{args.sessions}...", file=sys.stderr)
        log = run_session(run_config, i)
        saved_path = save_log(log, run_config.output_dir)
        print(f"  -> {log['status']} ({log['total_turns']} turns) saved to {saved_path}", file=sys.stderr)


if __name__ == "__main__":
    main()