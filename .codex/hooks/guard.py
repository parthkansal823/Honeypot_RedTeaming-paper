"""
Claude Code hooks for this repo. One script, three modes:

  pre     PreToolUse (Read|Bash): block whole-file reads/cats of big data files,
          which would dump megabytes of JSON into context.
  post    PostToolUse (Write|Edit): py_compile edited .py files so syntax errors
          surface immediately instead of on the next run.
  status  SessionStart: print a short pipeline-status summary so Claude does not
          have to re-explore the repo to learn what has already been produced.
"""

import json
import os
import py_compile
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
MAX_READ_BYTES = 1_000_000
MAX_READ_LIMIT = 200
BIG_FILES = r"(cowrie_2019-11-15\.json|real_organic\.jsonl|\.json\.gz)"
DUMP_CMD = re.compile(r"(^|[;&|(]\s*)(cat|type|less|more|Get-Content)\s+[^|;&]*" + BIG_FILES)
SAFE_PIPE = re.compile(r"\|\s*(head|tail|wc|grep|cut|sort|uniq|python|Select-Object)\b")

STATUS_FILES = [
    ("normalized/all_synthetic_120.jsonl", "synthetic sessions (120)"),
    ("normalized/real_organic.jsonl", "real CyberLab sessions"),
    ("results/table3_transfer.md", "Table 3 transfer matrix"),
    ("results/domain_shift.md", "label-free domain-shift analysis"),
    ("annotation/labels_final.csv", "dual-LLM labels"),
    ("paper/main.tex", "IEEE paper source"),
    ("paper/main.pdf", "compiled paper"),
]


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def pre(payload):
    tool, inp = payload.get("tool_name"), payload.get("tool_input") or {}
    if tool == "Read":
        path = inp.get("file_path") or ""
        try:
            size = os.path.getsize(path)
        except OSError:
            return
        limit = inp.get("limit")
        if size > MAX_READ_BYTES and (limit is None or limit > MAX_READ_LIMIT):
            deny(f"{os.path.basename(path)} is {size / 1e6:.0f} MB. Read at most "
                 f"{MAX_READ_LIMIT} lines (set limit), or summarize it with a python "
                 f"one-liner / the data-explorer agent instead.")
    elif tool == "Bash":
        cmd = inp.get("command") or ""
        if DUMP_CMD.search(cmd) and not SAFE_PIPE.search(cmd):
            deny("That would print a multi-MB data file into context. Pipe through "
                 "head/wc/grep, or summarize with python.")


def post(payload):
    inp = payload.get("tool_input") or {}
    path = inp.get("file_path") or (payload.get("tool_response") or {}).get("filePath") or ""
    if not path.endswith(".py") or not os.path.exists(path):
        return
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"Syntax error in {path}:\n{e.msg}", file=sys.stderr)
        sys.exit(2)


def status():
    lines = ["Pipeline status (from .claude/hooks/guard.py):"]
    for rel, label in STATUS_FILES:
        p = os.path.join(ROOT, rel)
        mark = f"{os.path.getsize(p) / 1e6:.1f} MB" if os.path.exists(p) else "MISSING"
        lines.append(f"  [{mark:>9}] {rel} - {label}")
    print("\n".join(lines))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "status":
        return status()
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    {"pre": pre, "post": post}.get(mode, lambda _: None)(payload)


if __name__ == "__main__":
    main()
