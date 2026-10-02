"""
4-quadrant transfer experiment: synthetic vs real training data -> synthetic vs real test data.

Q1 synth->synth (StratifiedKFold), Q2 real->real (GroupKFold by command template),
Q3 synth->real, Q4 real+synth->real (same folds as Q2).

Labels: rule_label() (same function for both domains) unless --real-labels /
--synthetic-labels CSVs (session_id,label) are supplied. Rule labels are built from
the same keywords as the features -> PLUMBING CHECK only, not a paper result.

Usage:
  python train_eval_classifier.py --synthetic normalized/all_synthetic_120.jsonl \
      --real normalized/real_organic.jsonl [--real-labels CSV] [--synthetic-labels CSV]
"""
import argparse
import csv
import json
import os
from collections import Counter

import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold, StratifiedKFold

from session_features import load_jsonl, normalize_cmd, session_tactics, template_key

LABELS = ["recon", "credential_access", "privilege_escalation", "persistence",
          "malware_drop", "resource_hijacking", "defense_evasion", "other"]
SEED = 42


def rule_label(s):
    t = session_tactics(s)
    if "resource_hijacking" in t:
        return "resource_hijacking"
    if "ingress_tool_transfer" in t:
        return "malware_drop"
    if "persistence" in t or "account_manipulation" in t:
        return "persistence"
    if "privilege_escalation" in t:
        return "privilege_escalation"
    if "credential_access" in t:
        return "credential_access"
    if "defense_evasion" in t:
        return "defense_evasion"
    if "discovery" in t:
        return "recon"
    return "other"


def load_labels(path):
    with open(path, encoding="utf-8-sig") as f:
        return {r["session_id"]: r["label"] for r in csv.DictReader(f)}


def text_of(sessions):
    return [" ".join(normalize_cmd(c) for c in s["commands"]) for s in sessions]


def numeric(sessions):
    rows = []
    for s in sessions:
        cmds = s["commands"]
        lens = [len(normalize_cmd(c)) for c in cmds]
        chained = [any(x in c for x in ("&&", ";", "|")) for c in cmds]
        rows.append([len(cmds), float(np.mean(lens)), float(np.mean(chained))])
    return np.array(rows)


def fit_predict(train, test, ytr):
    vec = TfidfVectorizer(token_pattern=r"[^\s]+", max_features=2000)
    Xtr = hstack([vec.fit_transform(text_of(train)), csr_matrix(numeric(train))]).tocsr()
    Xte = hstack([vec.transform(text_of(test)), csr_matrix(numeric(test))]).tocsr()
    clf = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                 random_state=SEED, n_jobs=-1)
    clf.fit(Xtr, ytr)
    return list(clf.predict(Xte))


def majority(ytr, n):
    return [Counter(ytr).most_common(1)[0][0]] * n


def row(qid, train, test, yt, yp, ym, ntr):
    # Average F1 over classes that occur in the test set only; otherwise a predicted
    # class with zero support adds a 0 to the mean and fakes a drop.
    present = sorted(set(yt))
    return {"id": qid, "train": train, "test": test,
            "macro_f1": float(f1_score(yt, yp, labels=present, average="macro", zero_division=0)),
            "accuracy": float(accuracy_score(yt, yp)),
            "predicted": dict(Counter(yp)),
            "majority_macro_f1": float(f1_score(yt, ym, labels=present, average="macro", zero_division=0)),
            "majority_accuracy": float(accuracy_score(yt, ym)),
            "n_train": int(ntr), "n_test": int(len(yt))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", required=True)
    ap.add_argument("--real", required=True)
    ap.add_argument("--real-labels")
    ap.add_argument("--synthetic-labels")
    ap.add_argument("--label-source", default="human",
                    help="Provenance name reported when label CSVs are given, e.g. 'llm-dual'.")
    ap.add_argument("--out-dir", default="results")
    a = ap.parse_args()

    syn = [s for s in load_jsonl(a.synthetic) if s.get("commands")]
    real = [s for s in load_jsonl(a.real) if s.get("commands")]
    for ss, path in ((syn, a.synthetic_labels), (real, a.real_labels)):
        hl = load_labels(path) if path else {}
        for s in ss:
            s["label"] = hl.get(s["session_id"]) or rule_label(s)
    src = a.label_source if (a.real_labels or a.synthetic_labels) else "rule"
    for s in real:
        s["tpl"] = template_key(s)
    ys = [s["label"] for s in syn]
    yr = [s["label"] for s in real]
    tpl_ids = {t: i for i, t in enumerate(dict.fromkeys(s["tpl"] for s in real))}
    groups = [tpl_ids[s["tpl"]] for s in real]
    print(f"synthetic n={len(syn)}, real n={len(real)}, templates={len(tpl_ids)}")

    # Q1
    k = max(2, min(5, min(Counter(ys).values())))
    yp, ym, yt = [], [], []
    for tr, te in StratifiedKFold(k, shuffle=True, random_state=SEED).split(syn, ys):
        ytr = [ys[i] for i in tr]
        yp += fit_predict([syn[i] for i in tr], [syn[i] for i in te], ytr)
        ym += majority(ytr, len(te))
        yt += [ys[i] for i in te]
    q1 = row("Q1", "synthetic", "synthetic", yt, yp, ym, len(syn) * (k - 1) // k)

    # Q2 / Q4 on identical template-grouped folds
    p2, p4, m2, yt2, ntr = [], [], [], [], []
    for tr, te in GroupKFold(5).split(real, yr, groups):
        a_ = [real[i] for i in tr]
        b_ = [real[i] for i in te]
        ytr = [yr[i] for i in tr]
        p2 += fit_predict(a_, b_, ytr)
        m2 += majority(ytr, len(te))
        p4 += fit_predict(a_ + syn, b_, ytr + ys)
        yt2 += [yr[i] for i in te]
        ntr.append(len(tr))
    n2 = int(np.mean(ntr))
    q2 = row("Q2", "real", "real", yt2, p2, m2, n2)
    q4 = row("Q4", "real+synthetic", "real", yt2, p4, m2, n2 + len(syn))

    # Q3
    p3 = fit_predict(syn, real, ys)
    m3 = majority(ys, len(real))
    q3 = row("Q3", "synthetic", "real", yr, p3, m3, len(syn))
    first = {}
    for i, s in enumerate(real):
        first.setdefault(s["tpl"], i)
    idx = list(first.values())
    q3d = row("Q3_dedup", "synthetic", "real_dedup", [yr[i] for i in idx],
              [p3[i] for i in idx], [m3[i] for i in idx], len(syn))
    f1c = f1_score(yr, p3, labels=LABELS, average=None, zero_division=0)
    q3pc = {l: float(f) for l, f in zip(LABELS, f1c)}

    dc = {"synthetic": Counter(ys), "real": Counter(yr),
          "real_dedup": Counter(yr[i] for i in idx)}
    dist = {d: {l: int(c.get(l, 0)) for l in LABELS} for d, c in dc.items()}
    quads = [q1, q2, q3, q3d, q4]
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "table3_transfer.json"), "w") as f:
        json.dump({"label_source": src, "label_distribution": dist, "quadrants": quads,
                   "q3_per_class_f1": q3pc}, f, indent=2)

    md = ["# Table 3: transfer between synthetic and real training data", ""]
    if src == "rule":
        md += ["> **PLUMBING CHECK - labels derived from same keywords as features.** Labels come "
               "from `rule_label()` (ATT&CK-tactic keyword rules in `session_features.py`), the "
               "same keywords that drive the TF-IDF features. These numbers are NOT a paper "
               "result; re-run with `--real-labels` / `--synthetic-labels` human labels.", ""]
    md += [f"Label source: **{src}**. Sessions with >=1 command only. TF-IDF (normalized "
           "commands) + 3 numeric features, RandomForest(300, balanced, seed 42). "
           f"Q1: stratified {k}-fold; Q2/Q4: GroupKFold(5) by command template; Q3_dedup: one "
           "session per template. CV metrics pooled over folds. Majority baseline predicts the "
           "training-set majority class.", "",
           "| Quadrant | Train | Test | n_train | n_test | Macro-F1 | Accuracy | "
           "Majority macro-F1 | Majority acc |",
           "|---|---|---|---|---|---|---|---|---|"]
    for q in quads:
        md.append(f"| {q['id']} | {q['train']} | {q['test']} | {q['n_train']} | {q['n_test']} | "
                  f"{q['macro_f1']:.3f} | {q['accuracy']:.3f} | {q['majority_macro_f1']:.3f} | "
                  f"{q['majority_accuracy']:.3f} |")
    md += ["", "## Label distribution", "",
           "| Label | Synthetic | Real (sessions) | Real (dedup templates) |", "|---|---|---|---|"]
    for l in LABELS:
        md.append(f"| {l} | {dist['synthetic'][l]} | {dist['real'][l]} | {dist['real_dedup'][l]} |")
    md.append("| **total** | " + " | ".join(str(sum(dist[d].values())) for d in dist) + " |")
    md += ["", "## Q3 per-class F1 (synthetic -> real, session-weighted)", "",
           "| Label | F1 |", "|---|---|"]
    md += [f"| {l} | {q3pc[l]:.3f} |" for l in LABELS]
    md += ["", "## Predicted label counts per quadrant", "",
           "| Quadrant | " + " | ".join(LABELS) + " |", "|---|" + "---|" * len(LABELS)]
    md += [f"| {q['id']} | " + " | ".join(str(q["predicted"].get(l, 0)) for l in LABELS) + " |"
           for q in quads]
    md += ["", "Macro-F1 averages only over classes present in the test set. Real labels are "
           f"broadcast from templates, so the effective real sample size is {len(idx)} templates."]
    with open(os.path.join(a.out_dir, "table3_transfer.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
