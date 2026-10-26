"""
Generates the data-driven appendix sections of the report as Markdown
(report/md/generated/*.md), straight from the project files, so nothing in
them is typed by hand.

Run from the repository root:
    python report/src/make_appendix_data.py
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from session_features import load_jsonl, normalize_cmd, session_tactics, strip_chat_leak, template_key  # noqa: E402

GEN = ROOT / "report" / "md" / "generated"
GEN.mkdir(parents=True, exist_ok=True)


def cell(text, limit=None):
    t = str(text).replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(t) > limit:
        t = t[:limit - 1] + "…"
    return t


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def labels_by_session():
    return {r["session_id"]: r["label"] for r in read_csv(ROOT / "annotation" / "labels_final.csv")}


def templates_md():
    labels = labels_by_session()
    groups = defaultdict(list)
    for s in load_jsonl(ROOT / "normalized" / "real_organic.jsonl"):
        if s.get("commands"):
            groups[template_key(s)].append(s)
    rows = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    out = ["Table: All 22 real behaviour templates, largest first. Commands are normalised (values mas