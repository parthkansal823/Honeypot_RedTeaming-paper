"""
Parse Cowrie's cowrie.json log into per-session records for
attack-classification / trend-prediction pipelines.

Usage:
    python cowrie_session_parser.py /path/to/cowrie.json --out sessions.jsonl [--csv sessions.csv]

Each line of cowrie.json is one JSON event. This groups events by the
`session` field into one row per session and adds a few cheap,
rule-based "findings" flags -- a transparent baseline to sanity-check
your trained classifier against, and a direct answer to "note what
happened / how far it got" without needing to re-instrument Cowrie,
since Cowrie already logs this.
"""

import json
import argparse
import csv
from collections import defaultdict
from pathlib import Path

RECON_CMDS = ("uname", "whoami", " id", "ps ", "netstat", "ifconfig", " ip a",
              "/proc/cpuinfo", "lscpu", "df -h", "free -")
PERSISTENCE_HINTS = ("crontab", "authorized_keys", "systemctl enable", "/etc/rc.local", "chattr +i")
DOWNLOAD_CMDS = ("wget", "curl", "tftp", "scp ")
DEFENSE_EVASION_HINTS = ("history -c", ".bash_history", "unset histfile", "iptables -f")


def load_events(path):
    with open(path, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def new_session():
    return {
        "session_id": None, "src_ip": None, "protocol": None,
        "start": None, "end": None, "duration_s": None,
        "login_attempts": [], "login_success": False,
        "commands": [], "downloads": [], "client_version": None,
    }


def summarize_sessions(events):
    sessions = defaultdict(new_session)
    for ev in events:
        sid = ev.get("session")
        if not sid:
            continue
        s = sessions[sid]
        s["session_id"] = sid
        s["src_ip"] = s["src_ip"] or ev.get("src_ip")
        ts = ev.get("timestamp")
        if ts:
            if s["start"] is None or ts < s["start"]:
                s["start"] = ts
            if s["end"] is None or ts > s["end"]:
                s["end"] = ts

        eid = ev.get("eventid", "")
        if eid == "cowrie.session.connect":
            s["protocol"] = ev.get("protocol")
        elif eid in ("cowrie.login.success", "cowrie.login.failed"):
            success = eid.endswith("success")
            s["login_attempts"].append({"username": ev.get("username"),
                                         "password": ev.get("password"),
                                         "success": success})
            s["login_success"] = s["login_success"] or success
        elif eid == "cowrie.command.input":
            s["commands"].append(ev.get("input", ""))
        elif eid in ("cowrie.session.file_download", "cowrie.session.file_upload"):
            s["downloads"].append({"url": ev.get("url"), "shasum": ev.get("shasum"),
                                    "outfile": ev.get("outfile")})
        elif eid == "cowrie.client.version":
            s["client_version"] = ev.get("version")
        elif eid == "cowrie.session.closed":
            s["duration_s"] = ev.get("duration")
    return sessions


def flag_findings(session):
    cmds_joined = " ".join(session["commands"]).lower()
    findings = []

    if session["login_success"] and not session["commands"]:
        findings.append("login_only_no_activity")
    if any(rc in cmds_joined for rc in RECON_CMDS):
        findings.append("reconnaissance")
    if any(d in cmds_joined for d in DOWNLOAD_CMDS):
        findings.append("payload_download_attempt")
    if any(p in cmds_joined for p in PERSISTENCE_HINTS):
        findings.append("persistence_attempt")
    if any(d in cmds_joined for d in DEFENSE_EVASION_HINTS):
        findings.append("defense_evasion")
    if len(session["login_attempts"]) > 5:
        findings.append("credential_bruteforce")
    if session["downloads"]:
        findings.append(f"downloaded_{len(session['downloads'])}_file(s)")

    # the literal "broke after this much code" marker
    findings.append(f"session_ended_after_{len(session['commands'])}_commands")
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logfile")
    ap.add_argument("--out", default="sessions.jsonl")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    sessions = summarize_sessions(load_events(args.logfile))

    if not sessions and Path(args.logfile).stat().st_size > 0:
        with open(args.logfile, errors="replace") as f:
            first_line = f.readline().strip()
        print(f"WARNING: 0 sessions parsed from a non-empty file. This usually means the file "
              f"isn't in Cowrie's native JSON-lines format (one JSON object per line with a "
              f"'session' and 'eventid' field) - e.g. it's CSV, or pre-aggregated some other way. "
              f"First line of the file for comparison:\n  {first_line[:300]}\n"
              f"If that doesn't look like a JSON object, this dataset needs its own reader before "
              f"this script can use it.")

    with open(args.out, "w") as out:
        for s in sessions.values():
            s["findings"] = flag_findings(s)
            s["command_count"] = len(s["commands"])
            s["login_attempt_count"] = len(s["login_attempts"])
            out.write(json.dumps(s) + "\n")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["session_id", "src_ip", "protocol", "duration_s", "login_success",
                        "login_attempt_count", "command_count", "download_count", "findings"])
            for s in sessions.values():
                w.writerow([s["session_id"], s["src_ip"], s["protocol"], s["duration_s"],
                            s["login_success"], s["login_attempt_count"], s["command_count"],
                            len(s["downloads"]), ";".join(s["findings"])])

    print(f"Parsed {len(sessions)} sessions -> {args.out}" + (f", {args.csv}" if args.csv else ""))


if __name__ == "__main__":
    main()
