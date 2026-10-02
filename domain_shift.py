"""
Label-free comparison of synthetic LLM-attacker sessions vs real CyberLab
honeypot sessions. Needs no annotation, so it is immune to the circular
weak-label problem and is the paper's primary evidence on realism.

Measures:
  1. corpus structure (effective number of distinct behaviors after template dedup)
  2. ATT&CK tactic coverage per corpus
  3. command-verb distributions: Jensen-Shannon divergence, vocabulary overlap
  4. classifier two-sample test (C2ST): can a simple model tell the corpora apart?
  5. per attacker x backend condition: which synthetic source is closest to real?

Usage:
    python domain_shift.py [--synthetic normalized/all_synthetic_120.jsonl]
                           [--real normalized/real_organic.jsonl]
Writes results/domain_shift.md and results/domain_shift.json.
"""

import argparse
import json
import random
import statistics
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold

from session_features import (TACTICS, has_chat_leak, load_jsonl, normalize_cmd, segments,
                              session_tactics, session_verbs, template_key)

SEED = 42
N_BOOT = 500


def dedup_by_template(sessions):
    seen, out = set(), []
    for s in sessions:
        k = template_key(s)
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


def corpus_stats(sessions):
    cmds = [c for s in sessions for c in s["commands"]]
    templates = Counter(map(template_key, sessions))
    return {
        "sessions": len(sessions),
        "distinct_templates": len(templates),
        "top5_template_share": sum(n for _, n in templates.most_common(5)) / len(sessions),
        "median_cmds_per_session": statistics.median(len(s["commands"]) for s in sessions),
        "mean_chars_per_cmd": statistics.mean(len(c) for c in cmds),
        "pct_cmds_chained": sum(len(segments(c)) > 1 for c in cmds) / len(cmds),
    }


def tactic_shares(sessions):
    counts = Counter(t for s in sessions for t in session_tactics(s))
    return {t: counts[t] / len(sessions) for t in TACTICS}


def verbs_of(session):
    """session_verbs() is regex-heavy; cache it on the session for the bootstrap."""
    if "_verbs" not in session:
        session["_verbs"] = Counter(session_verbs(session))
    return session["_verbs"]


def jsd(a_sessions, b_sessions):
    a, b = Counter(), Counter()
    for s in a_sessions:
        a.update(verbs_of(s))
    for s in b_sessions:
        b.update(verbs_of(s))
    vocab = sorted(a.keys() | b.keys())
    pa = np.array([a[v] for v in vocab], dtype=float)
    pb = np.array([b[v] for v in vocab], dtype=float)
    return float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2))


def jsd_with_ci(a_sessions, b_sessions, rng):
    point = jsd(a_sessions, b_sessions)
    boots = sorted(jsd(rng.choices(a_sessions, k=len(a_sessions)), b_sessions) for _ in range(N_BOOT))
    return point, boots[int(0.025 * N_BOOT)], boots[int(0.975 * N_BOOT)]


def c2st_auc(synthetic, real, text_fn):
    """5x5 repeated stratified CV AUC of a logistic regression separating the two
    corpora. 0.5 = indistinguishable, 1.0 = trivially separable."""
    docs = [text_fn(s) for s in synthetic + real]
    y = np.array([1] * len(synthetic) + [0] * len(real))
    aucs = []
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
    for tr, te in cv.split(docs, y):
        vec = TfidfVectorizer(token_pattern=r"[^\s]+", min_df=1)
        X_tr = vec.fit_transform([docs[i] for i in tr])
        X_te = vec.transform([docs[i] for i in te])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X_tr, y[tr])
        aucs.append(roc_auc_score(y[te], clf.predict_proba(X_te)[:, 1]))
    return float(np.mean(aucs)), float(np.std(aucs))


def fmt_pct(x):
    return f"{100 * x:.1f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--synthetic", default="normalized/all_synthetic_120.jsonl")
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--out-dir", default="results")
    args = ap.parse_args()
    rng = random.Random(SEED)

    synthetic = [s for s in load_jsonl(args.synthetic) if s.get("commands")]
    real_all = load_jsonl(args.real)
    real = [s for s in real_all if s.get("commands")]
    real_dedup = dedup_by_template(real)

    res = {"n_real_total": len(real_all), "n_real_interactive": len(real),
           "n_real_templates": len(real_dedup), "n_synthetic": len(synthetic)}
    res["structure"] = {"synthetic": corpus_stats(synthetic), "real": corpus_stats(real)}
    res["tactics"] = {"synthetic": tactic_shares(synthetic), "real": tactic_shares(real),
                      "real_dedup": tactic_shares(real_dedup)}

    syn_v = Counter(v for s in synthetic for v in session_verbs(s))
    real_v = Counter(v for s in real for v in session_verbs(s))
    res["verbs"] = {
        "top_synthetic": syn_v.most_common(10),
        "top_real": real_v.most_common(10),
        "jaccard": len(set(syn_v) & set(real_v)) / len(set(syn_v) | set(real_v)),
        "real_mass_covered_by_synthetic_vocab": sum(n for v, n in real_v.items() if v in syn_v) / sum(real_v.values()),
        "jsd_vs_real": jsd_with_ci(synthetic, real, rng),
        "jsd_vs_real_dedup": jsd_with_ci(synthetic, real_dedup, rng),
    }

    res["c2st"] = {
        "normalized_commands": c2st_auc(synthetic, real_dedup,
                                        lambda s: " ".join(normalize_cmd(c) for c in s["commands"])),
        "verbs_only": c2st_auc(synthetic, real_dedup, lambda s: " ".join(session_verbs(s))),
    }

    conditions = sorted({(s["attacker_model"], s["honeypot_backend"]) for s in synthetic})
    res["per_condition"] = []
    for model, backend in conditions:
        sub = [s for s in synthetic if (s["attacker_model"], s["honeypot_backend"]) == (model, backend)]
        point, lo, hi = jsd_with_ci(sub, real_dedup, rng)
        shares = tactic_shares(sub)
        res["per_condition"].append({
            "attacker": model, "backend": backend, "n": len(sub),
            "sessions_with_chat_leak": sum(any(has_chat_leak(c) for c in x["commands"]) for x in sub),
            "jsd_vs_real_dedup": [point, lo, hi],
            "tactics_matching_real": sum(1 for t in TACTICS if (shares[t] > 0) == (res["tactics"]["real_dedup"][t] > 0)),
        })

    out = Path(args.out_dir)
    out.mkdir(exist_ok=True)
    (out / "domain_shift.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    (out / "domain_shift.md").write_text(render_md(res), encoding="utf-8")
    print(render_md(res))


def render_md(r):
    s, rl = r["structure"]["synthetic"], r["structure"]["real"]
    L = ["# Label-free domain-shift analysis: synthetic vs. real\n",
         f"Real: {r['n_real_total']:,} sessions, {r['n_real_interactive']:,} with >=1 command, "
         f"{r['n_real_templates']} distinct normalized templates. Synthetic: {r['n_synthetic']} sessions.\n",
         "## Table 4a: Corpus structure\n",
         "| Metric | Synthetic | Real (interactive) |", "| :--- | ---: | ---: |",
         f"| Sessions | {s['sessions']} | {rl['sessions']:,} |",
         f"| Distinct behavior templates | {s['distinct_templates']} | {rl['distinct_templates']} |",
         f"| Share of top-5 templates | {fmt_pct(s['top5_template_share'])} | {fmt_pct(rl['top5_template_share'])} |",
         f"| Median commands / session | {s['median_cmds_per_session']} | {rl['median_cmds_per_session']} |",
         f"| Mean chars / command | {s['mean_chars_per_cmd']:.1f} | {rl['mean_chars_per_cmd']:.1f} |",
         f"| Commands with chaining/pipes | {fmt_pct(s['pct_cmds_chained'])} | {fmt_pct(rl['pct_cmds_chained'])} |",
         "\n## Table 4b: Share of sessions touching each ATT&CK tactic\n",
         "| Tactic | Synthetic | Real | Real (template-dedup) |", "| :--- | ---: | ---: | ---: |"]
    for t in TACTICS:
        L.append(f"| {t} | {fmt_pct(r['tactics']['synthetic'][t])} | {fmt_pct(r['tactics']['real'][t])} | "
                 f"{fmt_pct(r['tactics']['real_dedup'][t])} |")
    v = r["verbs"]
    L += ["\n## Table 4c: Command-verb distribution\n",
          f"- JSD(synthetic, real) = {v['jsd_vs_real'][0]:.3f} (95% bootstrap CI {v['jsd_vs_real'][1]:.3f}-{v['jsd_vs_real'][2]:.3f}); "
          f"vs. template-dedup real = {v['jsd_vs_real_dedup'][0]:.3f} ({v['jsd_vs_real_dedup'][1]:.3f}-{v['jsd_vs_real_dedup'][2]:.3f}). "
          "Range 0 (identical) to 1 (disjoint).",
          f"- Verb vocabulary Jaccard = {v['jaccard']:.3f}; synthetic vocabulary covers "
          f"{fmt_pct(v['real_mass_covered_by_synthetic_vocab'])} of real verb occurrences.",
          f"- Top synthetic verbs: {', '.join(f'{w} ({n})' for w, n in v['top_synthetic'])}",
          f"- Top real verbs: {', '.join(f'{w} ({n})' for w, n in v['top_real'])}",
          "\n## Table 4d: Classifier two-sample test (synthetic vs. template-dedup real)\n",
          "| Features | AUC (mean +/- sd, 5x5 CV) |", "| :--- | ---: |"]
    for name, (m, sd) in r["c2st"].items():
        L.append(f"| {name.replace('_', ' ')} | {m:.3f} +/- {sd:.3f} |")
    L += ["\nAUC 0.5 = indistinguishable; 1.0 = perfectly separable.\n",
          "## Table 4e: Per attacker x backend distance to real (template-dedup)\n",
          "| Attacker | Backend | n | JSD vs real [95% CI] | Tactics present/absent as in real (of 9) | Sessions with chat-format leak |",
          "| :--- | :--- | ---: | :--- | ---: | ---: |"]
    for c in r["per_condition"]:
        p, lo, hi = c["jsd_vs_real_dedup"]
        L.append(f"| {c['attacker']} | {c['backend']} | {c['n']} | {p:.3f} [{lo:.3f}, {hi:.3f}] | "
                 f"{c['tactics_matching_real']} | {c['sessions_with_chat_leak']} |")
    L.append("\nLeaked chat-format tokens and the reasoning text after them are stripped before all "
             "analyses; commands the model concatenated without separators cannot be recovered.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
