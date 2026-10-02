#!/usr/bin/env python3
"""
generate_paper_tables.py
------------------------
Analyzes all 120 session logs across the 6 experimental conditions
and generates Table 1 (Attacker Comparison) and Table 2 (Static vs Dynamic Honeypot)
formatted directly for the research paper.
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter
import argparse
from pathlib import Path

from session_features import has_chat_leak, strip_chat_leak

STATUSES = ["completed", "max_turns_reached", "connection_lost", "llm_error", "attacker_refused", "timed_out"]

CATEGORY_PATTERNS: dict[str, list[str]] = {
    "recon": [
        r"^whoami", r"^id\b", r"^uname", r"^hostname", r"^ifconfig", r"^ip a",
        r"^ps\b", r"^netstat", r"^ls\b", r"^pwd", r"^w\b", r"^who\b", r"^uptime",
        r"^env\b", r"^df\b", r"^free\b", r"^cat /proc"
    ],
    "credential_hunting": [
        r"passwd", r"shadow", r"\.ssh", r"id_rsa", r"authorized_keys",
        r"history", r"secret", r"credential", r"key", r"\.my\.cnf"
    ],
    "privilege_escalation": [
        r"sudo", r"su\b", r"-perm -4000", r"-perm -2000", r"visudo",
        r"capabilities", r"getcap", r"pkexec"
    ],
    "persistence": [
        r"crontab", r"\.bashrc", r"\.profile", r"useradd", r"adduser",
        r"chmod \+s", r"systemctl enable", r"rc\.local", r"ssh-keygen"
    ],
    "exfil_or_download": [
        r"^wget", r"^curl", r"^scp", r"^nc\b", r"^ftp", r"^tftp", r"base64"
    ],
    "destructive": [
        r"rm -rf", r"^dd\b", r"mkfs", r"shutdown", r"^reboot", r"^kill"
    ],
}

CONDITIONS = [
    ("DeepSeek-V3.2", "Static", Path("logs/deepseek")),
    ("DeepSeek-V3.2", "Dynamic (Qwen-32B)", Path("logs/deepseek_vs_qwen.qwen3-32b")),
    ("Gemma-3-4B", "Static", Path("logs/gemma")),
    ("Gemma-3-4B", "Dynamic (Qwen-32B)", Path("logs/gemma_vs_qwen.qwen3-32b")),
    ("GPT-OSS-120B", "Static", Path("logs/gptoss")),
    ("GPT-OSS-120B", "Dynamic (Qwen-32B)", Path("logs/gptoss_vs_qwen.qwen3-32b")),
]


def classify(cmd: str) -> list[str]:
    cmd_lower = cmd.lower()
    hits = [category for category, patterns in CATEGORY_PATTERNS.items()
            if any(re.search(p, cmd_lower) for p in patterns)]
    return hits or ["other"]


def load_sessions(log_dir: Path) -> list[dict]:
    sessions = []
    for p in sorted(log_dir.glob("*.json")):
        try:
            sessions.append(json.loads(p.read_text(encoding="utf-8", errors="replace")))
        except Exception as e:
            print(f"Skipping {p}: {e}")
    return sessions


def analyze_condition(sessions: list[dict]) -> dict:
    n = len(sessions)
    if n == 0:
        return {}

    statuses = Counter(s.get("status", "unknown") for s in sessions)
    turn_counts = [s.get("total_turns", 0) for s in sessions]
    commands = []
    latencies = []
    category_counts = Counter()
    leak_sessions = set()

    for s in sessions:
        for turn in s.get("turns", []):
            cmd = turn.get("command")
            # Rescue false-positive refusal if raw_response had a command
            if not cmd and turn.get("raw_response"):
                raw = turn["raw_response"].strip()
                if any(c in raw for c in ("/", "-", "|", "$", " ")):
                    cmd = raw
            if not cmd:
                continue
            if has_chat_leak(cmd):
                leak_sessions.add(id(s))
                cmd = strip_chat_leak(cmd).strip()
            if not cmd:
                continue

            commands.append(cmd)
            for cat in classify(cmd):
                category_counts[cat] += 1
            if turn.get("latency_sec") is not None:
                latencies.append(turn["latency_sec"])

    return {
        "n_sessions": n,
        "completed": statuses.get("completed", 0) + statuses.get("max_turns_reached", 0),
        "refused": statuses.get("attacker_refused", 0),
        "mean_turns": statistics.mean(turn_counts) if turn_counts else 0,
        "median_turns": statistics.median(turn_counts) if turn_counts else 0,
        "total_commands": len(commands),
        "unique_commands": len(set(commands)),
        "mean_latency": statistics.mean(latencies) if latencies else 0,
        "median_latency": statistics.median(latencies) if latencies else 0,
        "categories": category_counts,
        "leak_sessions": len(leak_sessions),
        "statuses": {k: statuses.get(k, 0) for k in STATUSES},
        "other_statuses": {k: v for k, v in statuses.items() if k not in STATUSES},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/tables_1_2.md')
    args = ap.parse_args()
    print("=" * 80)
    print("EMPIRICAL ANALYSIS OF 120 SYNTHETIC HONEYPOT SESSIONS")
    print("=" * 80)

    results = {}
    for model, backend, path in CONDITIONS:
        key = f"{model} | {backend}"
        sessions = load_sessions(path)
        stats = analyze_condition(sessions)
        results[key] = stats
        print(f"\nCondition: {key} ({stats.get('n_sessions', 0)} sessions)")
        print(f"  Turns/Session: Mean={stats.get('mean_turns', 0):.1f}, Median={stats.get('median_turns', 0)}")
        print(f"  Total Commands: {stats.get('total_commands', 0)} ({stats.get('unique_commands', 0)} unique)")
        print(f"  Latency (sec): Mean={stats.get('mean_latency', 0):.2f}, Median={stats.get('median_latency', 0):.2f}")
        print(f"  Categories: {dict(stats.get('categories', {}))}")

    # Generate Markdown Tables for the Paper
    md_output = []
    md_output.append("# Research Paper Empirical Tables: Synthetic Attack Dataset\n")
    md_output.append("## Table 1: Attacker Model Behavioral Comparison (Static Honeypot Baseline)\n")
    md_output.append("| Attacker Model | Sessions | Mean Turns | Total Cmds | Unique Cmds | Recon (%) | Credential (%) | PrivEsc (%) | Mean Latency (s) | Sessions w/ chat leak |")
    md_output.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for model in ["Gemma-3-4B", "DeepSeek-V3.2", "GPT-OSS-120B"]:
        key = f"{model} | Static"
        st = results.get(key, {})
        tot_cmds = st.get("total_commands", 1) or 1
        cats = st.get("categories", Counter())
        recon_pct = (cats.get("recon", 0) / tot_cmds) * 100
        cred_pct = (cats.get("credential_hunting", 0) / tot_cmds) * 100
        priv_pct = (cats.get("privilege_escalation", 0) / tot_cmds) * 100

        md_output.append(
            f"| **{model}** | {st.get('n_sessions', 0)} | {st.get('mean_turns', 0):.1f} | "
            f"{tot_cmds} | {st.get('unique_commands', 0)} | {recon_pct:.1f}% | "
            f"{cred_pct:.1f}% | {priv_pct:.1f}% | {st.get('mean_latency', 0):.2f}s | {st.get('leak_sessions', 0)} |"
        )

    md_output.append("\n## Table 2: Static vs. Dynamic (LLM Qwen-32B) Honeypot Interaction\n")
    md_output.append("| Attacker Model | Honeypot Backend | Mean Turns | Total Cmds | Recon (%) | Credential (%) | Mean Latency (s) | Latency Overhead | Chat-leak sessions |")
    md_output.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for model in ["DeepSeek-V3.2", "Gemma-3-4B", "GPT-OSS-120B"]:
        st_static = results.get(f"{model} | Static", {})
        st_dyn = results.get(f"{model} | Dynamic (Qwen-32B)", {})
        tot_s = st_static.get("total_commands", 1) or 1
        tot_d = st_dyn.get("total_commands", 1) or 1
        lat_s = st_static.get("mean_latency", 0.001)
        lat_d = st_dyn.get("mean_latency", 0.001)
        overhead = f"{((lat_d - lat_s) / max(0.001, lat_s)) * 100:+.1f}%"

        cats_s = st_static.get("categories", Counter())
        cats_d = st_dyn.get("categories", Counter())

        md_output.append(
            f"| **{model}** | Static Cowrie | {st_static.get('mean_turns', 0):.1f} | {tot_s} | "
            f"{(cats_s.get('recon', 0)/tot_s)*100:.1f}% | {(cats_s.get('credential_hunting', 0)/tot_s)*100:.1f}% | "
            f"{lat_s:.2f}s | Baseline | {st_static.get('leak_sessions', 0)} |"
        )
        md_output.append(
            f"| **{model}** | Dynamic (Qwen-32B) | {st_dyn.get('mean_turns', 0):.1f} | {tot_d} | "
            f"{(cats_d.get('recon', 0)/tot_d)*100:.1f}% | {(cats_d.get('credential_hunting', 0)/tot_d)*100:.1f}% | "
            f"{lat_d:.2f}s | {overhead} | {st_dyn.get('leak_sessions', 0)} |"
        )

    md_output.append("\n## Session status counts\n")
    md_output.append("| Condition | " + " | ".join(STATUSES) + " | other |")
    md_output.append("| :--- |" + " :--- |" * (len(STATUSES) + 1))
    for key, st in results.items():
        md_output.append(f"| {key.replace(' | ', ' / ')} | " + " | ".join(str(st['statuses'][k]) for k in STATUSES)
                         + f" | {sum(st['other_statuses'].values())} |")

    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(md_output), encoding="utf-8")
    jr = {}
    for key, st in results.items():
        tot = st.get("total_commands", 0) or 1
        d = dict(st)
        d["categories"] = dict(st["categories"])
        d["pct"] = {c: 100 * st["categories"].get(c, 0) / tot for c in CATEGORY_PATTERNS}
        jr[key] = d
    out_file.with_suffix(".json").write_text(json.dumps(jr, indent=2), encoding="utf-8")
    print(f"\n[+] Saved Markdown tables to {out_file.resolve()}")

if __name__ == "__main__":
    main()
