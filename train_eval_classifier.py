"""
Extract features from session records and run the train/test matrix:
synthetic->synthetic, synthetic->real, real->real, real+synthetic->real.

Deliberately simple (TF-IDF over command text + a few numeric session
features -> Random Forest), because the question is about the DATA
SOURCE, not classifier sophistication. A fancier model would only make
it harder to tell whether a result is about the data or about the model.

LABEL PROVENANCE -- read this before trusting any number out of this script:
  - Synthetic sessions (from synthetic_session_generator.py) carry a clean
    ground-truth `archetype` label, because you told the model what to write.
  - Real sessions (from cowrie_session_parser.py) do NOT have a ground-truth
    archetype -- only heuristic keyword-based `findings` flags. This script
    can derive a weak label from those flags (see weak_label()) so you can
    exercise the pipeline today, but that label was built from the same
    keywords your features are built from. A classifier "detecting" a
    weak label is partly just detecting its own label-construction rule.
    Treat weak-labeled results as a plumbing check, NOT a paper result.
  - For the number you actually report, hand-label a subset of real
    sessions yourself (skim the transcript, assign one of the 6 archetypes
    or "other") and pass it via --real-labels as a CSV: session_id,label.
    A few hundred is plenty -- these are short.

Usage:
    pip install scikit-learn --break-system-packages

    python train_eval_classifier.py \
        --synthetic claude_synthetic.jsonl gemini_synthetic.jsonl \
        --real real_sessions.jsonl \
        --real-labels hand_labeled.csv
"""

import json
import argparse
import csv
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix
from scipy.sparse import hstack, csr_matrix

# Priority order for turning heuristic `findings` flags into a single
# weak label. Same taxonomy as ARCHETYPES in synthetic_session_generator.py --
# keep these in sync if you change one.
WEAK_LABEL_PRIORITY = [
    ("malware_staging", "payload_download_attempt"),
    ("persistence_attempt", "persistence_attempt"),
    ("defense_evasion", "defense_evasion"),
    ("credential_bruteforce_then_recon", "credential_bruteforce"),
    ("recon_only", "reconnaissance"),
]


def load_sessions(paths):
    rows = []
    for path in paths:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def load_hand_labels(path):
    with open(path) as f:
        return {row["session_id"]: row["label"] for row in csv.DictReader(f)}


def weak_label(session):
    findings = set(session.get("findings", []))
    for label, flag in WEAK_LABEL_PRIORITY:
        if flag in findings:
            return label
    if session.get("command_count", 0) == 0:
        return "login_only"  # automated bot noise, not one of the 6 archetypes
    return "interactive_manual_probe"


def featurize(sessions, vectorizer=None, fit=False):
    command_text = [" ".join(s.get("commands") or []) for s in sessions]
    if fit:
        vectorizer = TfidfVectorizer(max_features=500, token_pattern=r"[^\s]+", min_df=1)
        text_features = vectorizer.fit_transform(command_text)
    else:
        text_features = vectorizer.transform(command_text)

    numeric = np.array([[
        s.get("command_count", 0) or 0,
        s.get("login_attempt_count", 0) or 0,
        s.get("duration_s") or 0,
        len(s.get("downloads") or []),
    ] for s in sessions], dtype=float)

    return hstack([text_features, csr_matrix(numeric)]), vectorizer


def new_forest():
    return RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--synthetic", nargs="*", default=[])
    ap.add_argument("--real", nargs="*", default=[])
    ap.add_argument("--real-labels", default=None, help="CSV: session_id,label (hand-labeled subset)")
    ap.add_argument("--synthetic-labels", default=None,
                     help="CSV: session_id,label - hand labels for LIVE AGENTIC synthetic sessions. "
                          "Not needed for fabricated-transcript sessions that already carry a "
                          "prompted `archetype` - but see the docstring caveat about what that label "
                          "actually proves before trusting it as your reported number.")
    ap.add_argument("--min-real-commands", type=int, default=1,
                     help="Drop real sessions with fewer commands than this before evaluation "
                          "(default 1). Real traffic is dominated by zero-command login-only bot "
                          "noise that neither the synthetic generator nor the live attacker "
                          "produces; leaving it in silently turns synth->real into a "
                          "class-coverage artifact rather than a measurement of realism.")
    args = ap.parse_args()

    synthetic = load_sessions(args.synthetic)
    real_all = load_sessions(args.real)
    real = [s for s in real_all if s.get("command_count", 0) >= args.min_real_commands]
    if len(real) < len(real_all):
        print(f"Filtered real sessions to command_count >= {args.min_real_commands}: "
              f"{len(real_all)} -> {len(real)} (dropped {len(real_all) - len(real)} "
              f"non-interactive/login-only sessions - see --min-real-commands)")

    hand_labels_synth = load_hand_labels(args.synthetic_labels) if args.synthetic_labels else {}
    for s in synthetic:
        s["label"] = hand_labels_synth.get(s["session_id"]) or s.get("archetype") or weak_label(s)
    synthetic_hand = [s for s in synthetic if s["session_id"] in hand_labels_synth]
    synthetic_prompted = [s for s in synthetic
                           if s["session_id"] not in hand_labels_synth and s.get("archetype")]
    synthetic_weak = [s for s in synthetic
                       if s["session_id"] not in hand_labels_synth and not s.get("archetype")]

    hand_labels = load_hand_labels(args.real_labels) if args.real_labels else {}
    for s in real:
        s["label"] = hand_labels.get(s["session_id"], weak_label(s))
    real_hand = [s for s in real if s["session_id"] in hand_labels]
    real_weak = [s for s in real if s["session_id"] not in hand_labels]

    if not synthetic and not real:
        print("Nothing to do -- pass --synthetic and/or --real.")
        return

    print(f"Loaded: {len(synthetic)} synthetic ({len(synthetic_hand)} hand-labeled, "
          f"{len(synthetic_prompted)} prompted-archetype, {len(synthetic_weak)} weak-labeled), "
          f"{len(real)} real ({len(real_hand)} hand-labeled, {len(real_weak)} weak-labeled).")
    if synthetic_prompted:
        print(f"! {len(synthetic_prompted)} synthetic session(s) are labeled with the same "
              f"archetype used to generate them. Any result built on these measures whether the "
              f"model can reproduce a stereotype it was handed, not whether synthetic data "
              f"resembles real attacker behavior. Hand-label a blind sample via --synthetic-labels "
              f"for the number you actually report.")

    # --- Condition 1: synthetic -> synthetic, 5-fold CV. Sanity check only. ---
    if len(synthetic) >= 20:
        X, _ = featurize(synthetic, fit=True)
        y = [s["label"] for s in synthetic]
        k = max(2, min(5, min(Counter(y).values())))
        preds = cross_val_predict(new_forest(), X, y, cv=StratifiedKFold(k, shuffle=True, random_state=42))
        print(f"\n=== synthetic -> synthetic ({k}-fold CV) === [sanity check, not a transfer result]")
        print(classification_report(y, preds, zero_division=0))

    # --- Condition 2: synthetic -> real. THE core question. ---
    if synthetic and real:
        test_set = real_hand or real_weak
        note = "hand-labeled" if real_hand else "WEAK-LABELED -- plumbing check only, see caveat in docstring"
        X_train, vec = featurize(synthetic, fit=True)
        y_train = [s["label"] for s in synthetic]
        X_test, _ = featurize(test_set, vectorizer=vec, fit=False)
        y_test = [s["label"] for s in test_set]
        clf = new_forest().fit(X_train, y_train)
        preds = clf.predict(X_test)
        print(f"\n=== synthetic -> real ({note}) ===")
        print(f"train n={X_train.shape[0]}, test n={X_test.shape[0]}")
        print(classification_report(y_test, preds, zero_division=0))
        labels = sorted(set(y_test) | set(preds))
        print("confusion matrix", labels, "\n", confusion_matrix(y_test, preds, labels=labels))

    # --- Conditions 3 & 4: real->real vs real+synthetic->real, on IDENTICAL
    #     held-out folds so the comparison is apples-to-apples and nothing
    #     used for training ever appears in that fold's test set. ---
    if len(real_hand) >= 10:
        y_real = [s["label"] for s in real_hand]
        k = max(2, min(5, min(Counter(y_real).values())))
        skf = StratifiedKFold(k, shuffle=True, random_state=42)
        real_only_preds, combined_preds, y_true = [], [], []

        for train_idx, test_idx in skf.split(real_hand, y_real):
            train_fold = [real_hand[i] for i in train_idx]
            test_fold = [real_hand[i] for i in test_idx]
            y_train_fold = [y_real[i] for i in train_idx]
            y_test_fold = [y_real[i] for i in test_idx]

            X_tr, vec = featurize(train_fold, fit=True)
            X_te, _ = featurize(test_fold, vectorizer=vec, fit=False)
            real_only_preds.extend(new_forest().fit(X_tr, y_train_fold).predict(X_te))

            combined_train = train_fold + synthetic
            y_combined = y_train_fold + [s["label"] for s in synthetic]
            X_tr2, vec2 = featurize(combined_train, fit=True)
            X_te2, _ = featurize(test_fold, vectorizer=vec2, fit=False)
            combined_preds.extend(new_forest().fit(X_tr2, y_combined).predict(X_te2))

            y_true.extend(y_test_fold)

        print(f"\n=== real -> real ({k}-fold, hand-labeled only) === [best-case baseline]")
        print(classification_report(y_true, real_only_preds, zero_division=0))

        if synthetic:
            print(f"\n=== real + synthetic -> real (same {k} folds) === [does synthetic data help?]")
            print(classification_report(y_true, combined_preds, zero_division=0))
    else:
        print("\n(Skipping real->real and real+synthetic->real: need >=10 hand-labeled "
              "real sessions via --real-labels. Everything above still ran.)")


if __name__ == "__main__":
    main()
