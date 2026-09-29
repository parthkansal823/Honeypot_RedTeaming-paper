"""
Converts ai_attacker.py's live agentic session logs (and, optionally,
normalize_cowrie_logs.py's organic-session output) into the exact schema
cowrie_session_parser.py produces for real Cowrie traffic, so
train_eval_classifier.py can consume live synthetic data without
modification to its feature extraction.

IMPORTANT - READ THIS BEFORE RUNNING THE CLASSIFIER:
    The old synthetic_session_generator.py fabricated a transcript FROM a
    named archetype, so it got a free, clean ground-truth label. A live
    agentic session has no such thing - the attacker just does whatever it
    does, and nobody told it in advance which of the 6 categories to act
    out. That means live-agentic sessions need labeling exactly the same
    way real sessions do: hand-label a sample, or fall back to the same
    rule-based weak_label() everything else uses. train_eval_classifier.py
    has been patched to expect this (see --synthetic-labels) - if you're
    looking at an older copy of that file, get the current one, or it will
    crash on `s["archetype"]` for every session this script produces.

The `findings` flags below are copied VERBATIM from cowrie_session_parser.py
so real and live-synthetic sessions get identical rule-based labels. If you
edit the flagging logic in one file, mirror the edit in the other, or the
comparison quietly stops being apples-to-apples.

USAGE
    # ai_attacker.py output (one *.json file per session)
    python convert_live_sessions.py --synthetic-dir logs/synthetic --out live_synthetic.jsonl

    # normalize_cowrie_logs.py output (one JSONL of real organic traffic)
    python convert_live_sessions.py --organic-jsonl normalized/organic_sessions.jsonl --out live_organic.jsonl

    # both at once, one output file with a "source" column distinguishing them
    python convert_live_sessions.py --synthetic-dir logs/synthetic \
        --organic-jsonl normalized/organic_sessions.jsonl --out all_sessions.jsonl
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

# ---- copied verbatim from cowrie_session_parser.py - keep both in sync ----
RECON_CMDS = ("uname", "whoami", " id", "ps ", "netstat", "ifconfig", " ip a",
              "/proc/cpuinfo", "lscpu", "df -h", "free -")
PERSISTENCE_HINTS = ("crontab", "authorized_keys", "systemctl enable", "/etc/rc.local", "chattr +i")
DOWNLOAD_CMDS = ("wget", "curl", "tftp", "scp ")
DEFENSE_EVASION_HINTS = ("history -c", ".bash_history", "unset histfile", "iptables -f")


def flag_findings(commands, login_success, downloads, login_attempt_count):
    cmds_joined = " ".join(commands).lower()
    findings = []
    if login_success and not commands:
        findings.append("login_only_no_activity")
    if any(rc in cmds_joined for rc in RECON_CMDS):
        findings.append("reconnaissance")
    if any(d in cmds_joined for d in DOWNLOAD_CMDS):
        findings.append("payload_download_attempt")
    if any(p in cmds_joined for p in PERSISTENCE_HINTS):
        findings.append("persistence_attempt")
    if any(d in cmds_joined for d in DEFENSE_EVASION_HINTS):
        findings.append("defense_evasion")
    if login_attempt_count > 5:
        findings.append("credential_bruteforce")
    if downloads:
        findings.append(f"downloaded_{len(downloads)}_file(s)")
    findings.append(f"session_ended_after_{len(commands)}_commands")
    return findings
# ---- end verbatim copy ----


def _parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def convert_ai_attacker_session(session: dict) -> dict:
    """ai_attacker.py's per-session schema -> cowrie_session_parser.py's schema."""
    commands = [t.get("command") for t in session.get("turns", []) if t.get("command")]

    # The LLM honeypot backend doesn't actually fetch anything, so there's no
    # real file_download event to observe here the way there is for real
    # traffic. This infers "attempted a download" from command text instead -
    # a weaker signal than a real transfer, and worth saying so in your
    # limitations section.
    downloads = [{"url": None, "note": "inferred from command text - no real transfer occurs "
                                        "against an LLM-backed honeypot"}
                 for c in commands if any(d in c.lower() for d in DOWNLOAD_CMDS)]

    login_success = session.get("status") != "connection_failed"
    start_dt, end_dt = _parse_ts(session.get("started_at")), _parse_ts(session.get("ended_at"))
    duration_s = (end_dt - start_dt).total_seconds() if start_dt and end_dt else None

    return {
        "session_id": session.get("session_id"),
        "src_ip": None,               # synthetic - no real network source
        "protocol": "ssh",            # ai_attacker.py currently drives SSH only
        "start": session.get("started_at"), "end": session.get("ended_at"),
        "duration_s": duration_s,
        "login_attempts": [], "login_success": login_success,
        "commands": commands, "downloads": downloads, "client_version": None,
        "command_count": len(commands), "login_attempt_count": 0,
        "findings": flag_findings(commands, login_success, downloads, 0),
        "source": "synthetic_agentic",   # distinct from the old fabricated-transcript "synthetic" tag
        "attacker_model": session.get("model"),
        "attacker_provider": session.get("provider"),
        "honeypot_backend_label": session.get("honeypot_backend_label"),
        "outcome_status": session.get("status"),  # keep this - it's your refusal/error signal, don't lose it
    }


def convert_organic_session(session: dict) -> dict:
    """normalize_cowrie_logs.py's schema -> cowrie_session_parser.py's schema.
    You'll rarely need this path - cowrie_session_parser.py reads raw
    cowrie.json directly - but it's here for when you only have the
    already-normalized file (e.g. it came from someone else's deployment)."""
    commands = [t.get("command") for t in session.get("turns", []) if t.get("command")]
    downloads = session.get("file_events", [])
    login_attempts = session.get("login_attempts", [])
    login_success = any(a.get("success") for a in login_attempts)
    return {
        "session_id": session.get("session_id"),
        "src_ip": session.get("src_ip"), "protocol": session.get("protocol"),
        "start": session.get("started_at"), "end": session.get("ended_at"),
        "duration_s": session.get("duration_sec"),
        "login_attempts": login_attempts, "login_success": login_success,
        "commands": commands, "downloads": downloads, "client_version": None,
        "command_count": len(commands), "login_attempt_count": len(login_attempts),
        "findings": flag_findings(commands, login_success, downloads, len(login_attempts)),
        "source": "real",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--synthetic-dir", help="Directory of ai_attacker.py's *.json session files")
    ap.add_argument("--organic-jsonl", help="normalize_cowrie_logs.py output file")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not args.synthetic_dir and not args.organic_jsonl:
        ap.error("pass --synthetic-dir and/or --organic-jsonl")

    rows = []
    skipped = 0
    if args.synthetic_dir:
        files = sorted(Path(args.synthetic_dir).glob("*.json"))
        for f in files:
            try:
                rows.append(convert_ai_attacker_session(json.loads(f.read_text())))
            except (json.JSONDecodeError, KeyError):
                skipped += 1
        print(f"{len(files)} file(s) in {args.synthetic_dir} -> {len(files) - skipped} converted, {skipped} skipped")

    if args.organic_jsonl:
        n_before = len(rows)
        with open(args.organic_jsonl) as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(convert_organic_session(json.loads(line)))
                except json.JSONDecodeError:
                    print(f"  skipping malformed line {line_no}")
        print(f"{args.organic_jsonl} -> {len(rows) - n_before} converted")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for r in rows:
            out.write(json.dumps(r) + "\n")

    print(f"Total: {len(rows)} session(s) -> {out_path}")


if __name__ == "__main__":
    main()
