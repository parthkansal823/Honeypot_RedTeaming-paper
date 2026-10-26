"""
Descriptive statistics for the project report (not used by the paper).

Reads the normalized corpora and the results/ files, and writes
report/data/report_stats.json so every number quoted in the report that is
not already in results/ comes from one file.

Run from the repository root:
    python report/src/compute_stats.py
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from session_features import load_jsonl, session_verbs, template_key  # noqa: E402

OUT = ROOT / "report" / "data" / "report_stats.json"


def real_stats(path):
    proto, country, users, pwds = Counter(), Counter(), Counter(), Counter()
    n = login_success = with_dl = attempts = 0
    durations, interactive = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = json.loads(line)
            n += 1
            proto[s.get("protocol") or "unknown"] += 1
            country[s.get("country") or "unknown"] += 1
            login_success += bool(s.get("login_success"))
            with_dl += bool(s.get("downloads"))
            for a in s.get("login_attempts") or []:
                attempts += 1
                users[a.get("username")] += 1
                pwds[a.get("password")] += 1
            if s.get("duration_s") is not None:
                durations.append(float(s["duration_s"]))
            if s.get("commands"):
                interactive.append(s)
    tpl = Counter(template_key(s) for s in interactive)
    sizes = sorted(tpl.values(), reverse=True)
    top = []
    for k, c in tpl.most_common(6):
        top.append({"sessions": c, "n_commands": len(k), "first_commands": [x[:90] for x in k[:5]]})
    return {
        "sessions": n,
        "protocol": dict(proto),
        "login_success_sessions": login_success,
        "sessions_with_downloads": with_dl,
        "login_attempts": attempts,
        "duration_median_s": statistics.median(durations),
        "duration_mean_s": statistics.mean(durations),
        "interactive_sessions": len(interactive),
        "interactive_share": len(interactive) / n,
        "distinct_source_hashes_interactive": len({s.get("src_ip") for s in interactive}),
        "top_countries_all": country.most_common(10),
        "top_countries_interactive": Counter(s.get("country") or "unknown" for s in interactive).most_common(10),
        "top_usernames": users.most_common(10),
        "top_passwords": pwds.most_common(10),
        "template_sizes": sizes,
        "top_templates": top,
        "commands_per_session_interactive": {
            "median": statistics.median(len(s["commands"]) for s in interactive),
            "max": max(len(s["commands"]) for s in interactive),
        },
    }


def synthetic_stats(path):
    syn = load_jsonl(path)
    cells = Counter((s["attacker_model"], s["honeypot_backend"]) for s in syn)
    first = Counter(s["commands"][0].strip() for s in syn if s.get("commands"))
    verbs = Counter(v for s in syn for v in session_verbs(s))
    return {
        "sessions": len(syn),
        "cells": {f"{a} | {b}": n for (a, b), n in sorted(cells.items())},
        "top_first_commands": first.most_common(8),
        "distinct_verbs": len(verbs),
        "total_commands": sum(len(s.get("commands") or []) for s in syn),
    }


def main():
    stats = {
        "real": real_stats(ROOT / "normalized" / "real_organic.jsonl"),
        "synthetic": synthetic_stats(ROOT / "normalized" / "all_synthetic_120.jsonl"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
