"""
Parse the CyberLab Cowrie dataset (Zenodo DOI 10.5281/zenodo.3687527) into the
same per-session JSONL schema that train_eval_classifier.py consumes.

The CyberLab export is NOT Cowrie's native JSON-lines log, so
cowrie_session_parser.py silently parses 0 sessions from it:
  - the file is one big JSON array, one `{"<session_id>": [events...]},` per line
  - IPs are replaced by `src_ip_identifier` hashes
  - command text lives in `message` as "CMD: <command>" (there is no `input` field)

Streams line-by-line, so the 600 MB file never has to fit in memory.

Usage:
    python parse_cyberlab.py [--in cyberlab_2019-11-15.json/cowrie_2019-11-15.json]
                             [--out normalized/real_organic.jsonl]
"""

import argparse
import json
from collections import Counter, defaultdict

from cowrie_session_parser import flag_findings

DEFAULT_IN = "cyberlab_2019-11-15.json/cowrie_2019-11-15.json"
DEFAULT_OUT = "normalized/real_organic.jsonl"


def iter_session_blocks(path):
    """Yield (session_id, events) from the array-of-single-key-objects format."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip().lstrip("[").rstrip(",").rstrip("]")
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            for sid, events in obj.items():
                yield sid, events


def new_session(sid):
    return {
        "session_id": sid, "source": "cyberlab_2019-11-15", "src_ip": None,
        "country": None, "protocol": None, "start": None, "end": None,
        "duration_s": None, "login_attempts": [], "login_success": False,
        "commands": [], "downloads": [], "client_version": None,
    }


def apply_event(s, ev):
    s["src_ip"] = s["src_ip"] or ev.get("src_ip_identifier")
    geo = ev.get("geolocation_data") or {}
    s["country"] = s["country"] or geo.get("country_code2")
    ts = ev.get("timestamp")
    if ts:
        s["start"] = ts if s["start"] is None or ts < s["start"] else s["start"]
        s["end"] = ts if s["end"] is None or ts > s["end"] else s["end"]

    eid = ev.get("eventid", "")
    if eid == "cowrie.session.connect":
        s["protocol"] = ev.get("protocol")
    elif eid in ("cowrie.login.success", "cowrie.login.failed"):
        success = eid.endswith("success")
        s["login_attempts"].append({"username": ev.get("username"),
                                    "password": ev.get("password"), "success": success})
        s["login_success"] = s["login_success"] or success
    elif eid == "cowrie.command.input":
        msg = ev.get("input") or ev.get("message") or ""
        s["commands"].append(msg[5:] if msg.startswith("CMD: ") else msg)
    elif eid in ("cowrie.session.file_download", "cowrie.session.file_upload"):
        s["downloads"].append({"url": ev.get("url"), "shasum": ev.get("shasum"),
                               "outfile": ev.get("outfile")})
    elif eid == "cowrie.client.version":
        s["client_version"] = ev.get("ssh_client_version") or ev.get("version")
    elif eid == "cowrie.session.closed":
        s["duration_s"] = ev.get("duration")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", default=DEFAULT_IN)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    # A session can be split across several array entries, so merge by id.
    sessions = {}
    for sid, events in iter_session_blocks(args.inp):
        s = sessions.setdefault(sid, new_session(sid))
        for ev in sorted(events, key=lambda e: e.get("timestamp") or ""):
            apply_event(s, ev)

    stats = Counter()
    with open(args.out, "w", encoding="utf-8") as out:
        for s in sessions.values():
            s["findings"] = flag_findings(s)
            s["command_count"] = len(s["commands"])
            s["login_attempt_count"] = len(s["login_attempts"])
            stats["sessions"] += 1
            stats["with_login_success"] += s["login_success"]
            stats["with_commands"] += s["command_count"] > 0
            stats["with_downloads"] += bool(s["downloads"])
            stats[f"proto_{s['protocol']}"] += 1
            out.write(json.dumps(s) + "\n")

    print(f"Parsed {stats['sessions']} sessions -> {args.out}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
