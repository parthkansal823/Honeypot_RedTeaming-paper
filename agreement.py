"""Inter-annotator agreement + final label table.
Usage: python agreement.py [--dir annotation] [--a1 F] [--a2 F] [--llm F] [--adj F] [--key F]
                           [--real normalized/real_organic.jsonl] [--md results/annotation_agreement.md]
"""
import argparse
import csv
import os
import sys
from collections import Counter

from sklearn.metrics import cohen_kappa_score

from session_features import load_jsonl, template_key

LABELS = ["recon", "credential_access", "privilege_escalation", "persistence",
          "malware_drop", "resource_hijacking", "defense_evasion", "other"]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def labels_of(path, name, bad):
    out = {}
    for r in read_csv(path):
        v = (r.get("label") or "").strip().lower().replace(" ", "_")
        if not v:
            continue
        if v not in LABELS:
            bad.append((name, r["item_id"], v))
            continue
        out[r["item_id"]] = v
    return out


def kappa(x, y, ids):
    ids = sorted(ids)
    if len(ids) < 2:
        return None
    a, b = [x[i] for i in ids], [y[i] for i in ids]
    if len(set(a) | set(b)) < 2:
        return 1.0 if a == b else None
    return cohen_kappa_score(a, b, labels=LABELS)


def fmt(k):
    return "n/a" if k is None else f"{k:.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="annotation")
    ap.add_argument("--a1")
    ap.add_argument("--a2")
    ap.add_argument("--llm")
    ap.add_argument("--adj")
    ap.add_argument("--key")
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--md", default="results/annotation_agreement.md")
    ap.add_argument("--out-labels")
    ap.add_argument("--out-disagree")
    a = ap.parse_args()
    D = a.dir

    def p(v, n):
        return v or os.path.join(D, n)

    a1p, a2p, keyp = p(a.a1, "sheet_annotator1.csv"), p(a.a2, "sheet_annotator2.csv"), p(a.key, "key.csv")
    llmp, adjp = p(a.llm, "labels_llm.csv"), p(a.adj, "adjudicated.csv")
    for f in (a1p, a2p, keyp):
        if not os.path.exists(f):
            sys.exit(f"Missing {f}. Run make_annotation_sheet.py first.")
    bad = []
    l1, l2 = labels_of(a1p, "annotator1", bad), labels_of(a2p, "annotator2", bad)
    if not l1 or not l2:
        sys.exit(f"Sheets are still blank (annotator1 labels: {len(l1)}, annotator2: {len(l2)}). "
                 f"Fill the 'label' column in {a1p} and {a2p} (see annotation/RUBRIC.md), then rerun.")
    key = {r["item_id"]: r for r in read_csv(keyp)}
    both = sorted(set(l1) & set(l2))
    if len(both) < 2:
        sys.exit("Fewer than 2 items labeled by both annotators; finish labeling first.")
    llm = labels_of(llmp, "llm", bad) if os.path.exists(llmp) else {}
    adj = labels_of(adjp, "adjudicated", bad) if os.path.exists(adjp) else {}

    L = ["# Annotation agreement\n",
         f"Items labeled by both annotators: {len(both)} of {len(key)} "
         f"(annotator1 {len(l1)}, annotator2 {len(l2)}).\n"]
    if bad:
        L.append(f"Invalid labels ignored ({len(bad)}): " + ", ".join(f"{n}:{i}={v}" for n, i, v in bad[:20]) + "\n")
    L.append("## Cohen's kappa (annotator1 vs annotator2)\n")
    L.append("| subset | n | raw agreement | kappa |\n|---|---|---|---|")
    for name, f in (("all", lambda i: True), ("real", lambda i: key[i]["source"] == "real"),
                    ("synthetic", lambda i: key[i]["source"] == "synthetic")):
        ids = [i for i in both if f(i)]
        agr = sum(l1[i] == l2[i] for i in ids) / len(ids) if ids else None
        L.append(f"| {name} | {len(ids)} | {fmt(agr)} | {fmt(kappa(l1, l2, ids))} |")
    cm = Counter((l1[i], l2[i]) for i in both)
    used = [lab for lab in LABELS if any(lab in k for k in cm)]
    L.append("\n## Confusion (rows annotator1, columns annotator2)\n")
    L.append("| a1 / a2 | " + " | ".join(used) + " |\n|---|" + "---|" * len(used))
    for r in used:
        L.append(f"| {r} | " + " | ".join(str(cm[(r, c)]) for c in used) + " |")
    if llm:
        L.append("\n## LLM pre-labels vs humans (kappa)\n\n| pair | n | raw agreement | kappa |\n|---|---|---|---|")
        for nm, h in (("LLM vs annotator1", l1), ("LLM vs annotator2", l2)):
            ids = sorted(set(llm) & set(h))
            agr = sum(llm[i] == h[i] for i in ids) / len(ids) if ids else None
            L.append(f"| {nm} | {len(ids)} | {fmt(agr)} | {fmt(kappa(llm, h, ids))} |")

    dis = [i for i in both if l1[i] != l2[i]]
    dpath = a.out_disagree or os.path.join(D, "disagreements.csv")
    rows1, rows2 = read_csv(a1p), read_csv(a2p)
    n1 = {r["item_id"]: (r.get("notes") or "").strip() for r in rows1}
    n2 = {r["item_id"]: (r.get("notes") or "").strip() for r in rows2}
    cmds = {r["item_id"]: r["commands"] for r in rows1}
    with open(dpath, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "label_annotator1", "label_annotator2", "notes1", "notes2", "commands", "label_final"])
        for i in dis:
            w.writerow([i, l1[i], l2[i], n1.get(i, ""), n2.get(i, ""), cmds.get(i, ""), adj.get(i, "")])

    # final per-item labels: agreed, else adjudicated, else excluded
    final, n_agree, n_adj, excluded = {}, 0, 0, []
    for i in key:
        if i in l1 and i in l2 and l1[i] == l2[i]:
            final[i] = l1[i]
            n_agree += 1
        elif i in adj:
            final[i] = adj[i]
            n_adj += 1
        else:
            excluded.append(i)

    # broadcast real item labels to every real session sharing the template
    rows = []
    n_real = 0
    if os.path.exists(a.real):
        real = load_jsonl(a.real)
        by_sid = {s["session_id"]: s for s in real}
        tkey_label = {}
        for i, k in key.items():
            if k["source"] == "real" and i in final and k["session_id"] in by_sid:
                tkey_label[template_key(by_sid[k["session_id"]])] = final[i]
        for s in real:
            if s.get("commands"):
                lab = tkey_label.get(template_key(s))
                if lab:
                    rows.append((s["session_id"], lab, "real"))
                    n_real += 1
    else:
        print(f"WARNING: {a.real} not found; real sessions not broadcast", file=sys.stderr)
    for i, k in key.items():
        if k["source"] == "synthetic" and i in final:
            rows.append((k["session_id"], final[i], "synthetic"))
    lpath = a.out_labels or os.path.join(D, "labels_final.csv")
    with open(lpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["session_id", "label", "source"])
        w.writerows(rows)

    L.append("\n## Final labels\n")
    L.append(f"- Items agreed: {n_agree}; adjudicated: {n_adj}; excluded (disagreement not adjudicated, "
             f"or unlabeled by an annotator): {len(excluded)} of {len(key)} items "
             f"({len(dis)} disagreements).")
    L.append(f"- Real sessions labeled via template broadcast: {n_real}; "
             f"synthetic: {sum(r[2] == 'synthetic' for r in rows)}.")
    for src in ("real", "synthetic"):
        c = Counter(r[1] for r in rows if r[2] == src)
        L.append(f"- {src} label counts: " + ", ".join(f"{lab}={c[lab]}" for lab in LABELS if c[lab]))
    os.makedirs(os.path.dirname(a.md) or ".", exist_ok=True)
    with open(a.md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nWrote {a.md}, {dpath}, {lpath}")


if __name__ == "__main__":
    main()
