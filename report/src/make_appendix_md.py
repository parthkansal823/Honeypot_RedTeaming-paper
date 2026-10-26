"""
Generates report/md/96_appendix_data.md (Appendices 6-10) from the project's
own files, so nothing in these appendices is typed by hand:
  6  catalogue of the 22 real behaviour templates (size, share, label, tactics)
  7  the 12 adjudicated annotation disagreements
  8  per-session summary of all 120 synthetic sessions
  9  configuration files (secrets removed)
  10 source code of the analysis scripts

Run from the repository root:
    python report/src/make_appendix_md.py
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from session_features import load_jsonl, session_tactics, template_key  # noqa: E402

OUT = ROOT / "report" / "md" / "96_appendix_data.md"
FENCE = "`" * 3


def pretty(label):
    return label.replace("_", " ").capitalize()


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def templates_section(L):
    real = [s for s in load_jsonl(ROOT / "normalized" / "real_organic.jsonl") if s.get("commands")]
    labels = {r["session_id"]: r["label"] for r in read_csv(ROOT / "annotation" / "labels_final.csv")}
    groups = defaultdict(list)
    for s in real:
        groups[template_key(s)].append(s)
    ranked = sorted(groups.values(), key=len, reverse=True)
    total = len(real)
    L += ["## Appendix 6: Catalogue of the Real Behaviour Templates", "",
          f"The {total:,} interactive real sessions collapse to {len(ranked)} behaviour templates after "
          "normalisation (Section 3.7.8). The table lists every template with its size, its share of the "
          "interactive sessions, the running total, its length, its final intent label and the descriptive "
          "tactics its commands touch.", "",
          "Table: The real behaviour templates, largest first. {#tab:templates widths=1,2,2,2,2,3,6}", "",
          "| # | Sessions | Share | Cumulative | Commands | Final label | Tactics touched |",
          "|---|---|---|---|---|---|---|"]
    cum = 0
    for i, ss in enumerate(ranked, 1):
        cum += len(ss)
        lab = Counter(labels.get(s["session_id"], "") for s in ss).most_common(1)[0][0]
        tac = ", ".join(sorted(t.replace("_", " ") for t in session_tactics(ss[0]))) or "none"
        L.append(f"| {i} | {len(ss):,} | {len(ss) / total:.1%} | {cum / total:.1%} | "
                 f"{len(ss[0]['commands'])} | {pretty(lab)} | {tac} |")
    L += ["", f"The two largest templates alone contain {len(ranked[0]) + len(ranked[1]):,} of {total:,} "
          "sessions. Both begin with the same CPU fingerprinting and differ mainly in whether a payload kit "
          "is unpacked afterwards, which is why one is labelled resource hijacking and the other persistence.", ""]


def disagreements_section(L):
    key = {r["item_id"]: r for r in read_csv(ROOT / "annotation" / "key.csv")}
    adj = {r["item_id"]: r for r in read_csv(ROOT / "annotation" / "adjudicated.csv")}
    dis = read_csv(ROOT / "annotation" / "disagreements.csv")
    L += ["## Appendix 7: Adjudicated Annotation Disagreements", "",
          f"The two blind annotators disagreed on {len(dis)} of 184 items. A separate blind adjudicator chose the "
          "final label using the rubric and wrote a one-line reason. The source column comes from the hidden key "
          "file and was not visible to anyone during labelling or adjudication.", "",
          "Table: Every disagreement, the final label and the adjudicator's reason. "
          "{#tab:disagreements widths=2,4,3,3,3,7}", "",
          "| Item | Source | Annotator A | Annotator B | Final | Adjudicator's reason |",
          "|---|---|---|---|---|---|"]
    for r in dis:
        i = r["item_id"]
        k = key.get(i, {})
        if k.get("source") == "synthetic":
            src = f"{k.get('attacker_model', '')} / {k.get('honeypot_backend', '')}"
        else:
            src = f"real template ({k.get('template_size', '?')} sessions)"
        final = adj.get(i, {}).get("label", "")
        reason = adj.get(i, {}).get("rationale", "").replace("|", "/")
        L.append(f"| {i} | {src} | {pretty(r['label_annotator1'])} | {pretty(r['label_annotator2'])} | "
                 f"{pretty(final)} | {reason} |")
    L.append("")


def synthetic_section(L):
    syn = load_jsonl(ROOT / "normalized" / "all_synthetic_120.jsonl")
    labels = {r["session_id"]: r["label"] for r in read_csv(ROOT / "annotation" / "labels_final.csv")}
    syn.sort(key=lambda s: (s["attacker_model"], s["honeypot_backend"], s["started_at"]))
    L += ["## Appendix 8: Summary of All Synthetic Sessions", "",
          "This appendix lists every one of the 120 synthetic sessions with its cell, start time (UTC), how it "
          "ended, how many commands it issued and the final intent label it received. Sessions are numbered "
          "within each cell in the order they were run.", ""]
    cells = []
    for s in syn:
        c = (s["attacker_model"], s["honeypot_backend"])
        if c not in cells:
            cells.append(c)
    for model, backend in cells:
        rows = [s for s in syn if (s["attacker_model"], s["honeypot_backend"]) == (model, backend)]
        L += [f"### {model} against {backend}", "",
              f"Table: Synthetic sessions of {model} against {backend}. "
              f"{{#tab:syn-{model.split('-')[0].lower()}-{'static' if 'Static' in backend else 'dynamic'} widths=1,5,4,2,4}}", "",
              "| # | Started (UTC) | Status | Commands | Final label |", "|---|---|---|---|---|"]
        for k, s in enumerate(rows, 1):
            started = s["started_at"][:19].replace("T", " ")
            L.append(f"| {k} | {started} | {s['status'].replace('_', ' ')} | {s.get('command_count', len(s['commands']))} | "
                     f"{pretty(labels.get(s['session_id'], ''))} |")
        L.append("")


def config_section(L):
    L += ["## Appendix 9: Configuration Files", "",
          "These are the configuration files used to run the testbed. API keys and other secrets are never stored "
          "in them; where a key field exists it is shown as `<redacted>`.", ""]
    for rel, title in (("cowrie_etc/cowrie.cfg", "Cowrie honeypot configuration (cowrie_etc/cowrie.cfg)"),
                       ("docker-compose.yml", "Docker Compose file (docker-compose.yml)"),
                       ("Dockerfile.attacker", "Analysis container (Dockerfile.attacker)"),
                       ("requirements.txt", "Python dependencies (requirements.txt)")):
        text = (ROOT / rel).read_text(encoding="utf-8")
        lines = []
        for line in text.splitlines():
            if line.split("=")[0].strip().lower() in ("api_key", "password", "token", "secret"):
                line = line.split("=")[0] + "= <redacted>"
            lines.append(line)
        L += [f"### {title}", "", FENCE, *lines, FENCE, ""]


def code_section(L):
    L += ["## Appendix 10: Source Code of the Analysis Scripts", "",
          "This appendix reproduces the analysis code that produced the reported results, so that every method "
          "described in Chapter 3 can be checked line by line. The full repository, including the testbed "
          "scripts, is available on GitHub.", ""]
    for rel, title in (("session_features.py", "Normalisation, verbs, tactic tags and templates (session_features.py)"),
                       ("parse_cyberlab.py", "CyberLab parser (parse_cyberlab.py)"),
                       ("domain_shift.py", "Label-free comparison (domain_shift.py)"),
                       ("make_annotation_sheet.py", "Blind annotation sheets (make_annotation_sheet.py)"),
                       ("agreement.py", "Agreement and final labels (agreement.py)"),
                       ("train_eval_classifier.py", "Four-quadrant transfer experiment (train_eval_classifier.py)")):
        text = (ROOT / rel).read_text(encoding="utf-8").rstrip("\n")
        L += [f"### {title}", "", FENCE, *text.splitlines(), FENCE, ""]


def main():
    L = []
    templates_section(L)
    disagreements_section(L)
    synthetic_section(L)
    config_section(L)
    code_section(L)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(L)} lines)")


if __name__ == "__main__":
    main()
