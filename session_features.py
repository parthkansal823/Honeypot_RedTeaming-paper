"""
Shared command normalization and descriptive ATT&CK-tactic tagging, used by
domain_shift.py, train_eval_classifier.py and make_annotation_sheet.py so all
three see sessions the same way.

The tactic tagger is DESCRIPTIVE (what share of sessions touch each tactic).
It is deliberately not used as a training label for the reported numbers -
that would be the circular weak-labeling problem described in
honeypot_research_paper_plan.md.
"""

import json
import re

_URL = re.compile(r"\b(?:https?|ftp|tftp)://\S+", re.I)
_IP = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")
_QUOTED = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'")
_HEX = re.compile(r"\b[0-9a-f]{16,}\b", re.I)
_RANDTOK = re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{8,}\b")
_NUM = re.compile(r"\b\d+\b")
# Mirai-family bots echo a random 5-letter tag via `/bin/busybox ABCDE` to fingerprint
# the shell; mask it (but keep real applet names) so variants collapse to one template.
_BUSYBOX_APPLETS = {"wget", "tftp", "ftpget", "chmod", "cat", "echo", "ps", "rm", "cp", "mv",
                    "mkdir", "sh", "ls", "nc", "dd", "kill", "killall", "mount", "uname", "sleep",
                    "touch", "ln", "grep", "head", "tail", "ifconfig", "ip", "id", "telnetd",
                    "httpd", "chown", "find", "top", "free", "df", "ping", "route", "netstat",
                    "hostname", "awk", "sed", "tar", "gzip", "unzip", "whoami", "passwd"}
_BUSYBOX_TAG = re.compile(r"\bbusybox ([a-z]{3,12})\b")
_SPLIT = re.compile(r"\|\||&&|[;|&\n]|\$\(|`")

# Command-level tactic patterns, matched against a normalized segment.
TACTIC_PATTERNS = {
    "discovery": r"^(uname|whoami|id|hostname|ifconfig|ip|ps|netstat|ss|ls|pwd|w|who|uptime|df|free|"
                 r"lscpu|nproc|top|env|which|lsb_release|dmesg|mount|arp|route|last)\b|/proc/(cpuinfo|meminfo|version)"
                 r"|^cat /etc/(os-release|issue|hostname)|^crontab -l|^find\b(?!.*-perm)|^(wget|tftp|curl|ftpget)$",
    "credential_access": r"/etc/shadow|/etc/passwd\b(?!.*chpasswd)|\.ssh|id_rsa|\.bash_history|^history\b|"
                         r"password|passwd\.|secret|credential|\.aws|\.my\.cnf|wp-config",
    "account_manipulation": r"chpasswd|^passwd\b|\|\s*passwd|useradd|adduser|usermod|authorized_keys",
    "persistence": r"^crontab (?!-l)|/etc/cron|systemctl enable|rc\.local|>>?\s*\S*\.(bashrc|profile)|/etc/init\.d",
    "privilege_escalation": r"^sudo\b|^su\b|-perm -[42]000|getcap|pkexec|/etc/sudoers",
    "defense_evasion": r"history -c|unset hist|histfile|rm .*(\.bash_history|/var/log)|chattr|^iptables|"
                       r"^pkill|^kill(all)?\b|ufw disable|setenforce",
    # Bare `wget`/`tftp` with no argument is Mirai's capability probe, not a download.
    "ingress_tool_transfer": r"^(wget|curl|tftp|ftpget|scp|nc|ncat)\s+\S|busybox (wget|tftp)\s+\S",
    "execution": r"chmod \+?[0-7]*x|^\./|^(sh|bash)\b|base64 (-d|--decode)|^nohup\b|^perl\b|^python",
    "resource_hijacking": r"xmrig|minerd|stratum|cryptonight|\bminer\b|\.rsync/|dota",
}
_TACTIC_RE = {t: re.compile(p, re.I) for t, p in TACTIC_PATTERNS.items()}
TACTICS = list(TACTIC_PATTERNS)


def load_jsonl(path):
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def has_chat_leak(cmd):
    """GPT-OSS sometimes emitted harmony-format tokens plus its own reasoning
    ("<|channel|>analysis<|message|>...") into the shell command."""
    return "<|" in cmd


def strip_chat_leak(cmd):
    return cmd.split("<|", 1)[0]


def normalize_cmd(cmd):
    """Mask session-specific values (URLs, IPs, quoted args, random passwords) so
    the same bot script run from different IPs normalizes to one template."""
    c = strip_chat_leak(cmd).strip().lower()
    c = _URL.sub("<url>", c)
    c = _IP.sub("<ip>", c)
    c = _QUOTED.sub("<str>", c)
    c = _HEX.sub("<hex>", c)
    c = _RANDTOK.sub("<tok>", c)
    c = _NUM.sub("<n>", c)
    c = _BUSYBOX_TAG.sub(lambda m: m.group(0) if m.group(1) in _BUSYBOX_APPLETS else "busybox <tag>", c)
    return re.sub(r"\s+", " ", c)


def segments(cmd):
    """Split a normalized command line into its chained/piped sub-commands."""
    return [s.strip() for s in _SPLIT.split(normalize_cmd(cmd)) if s.strip()]


def verb(segment):
    toks = [t for t in segment.split() if "=" not in t]  # drop VAR=x prefixes
    return toks[0].rsplit("/", 1)[-1] if toks else None


def session_verbs(session):
    return [v for c in session.get("commands") or [] for v in map(verb, segments(c)) if v]


def session_tactics(session):
    found = set()
    for c in session.get("commands") or []:
        for seg in segments(c):
            found.update(t for t, rx in _TACTIC_RE.items() if rx.search(seg))
    return found


def template_key(session):
    return tuple(normalize_cmd(c) for c in session.get("commands") or [])
