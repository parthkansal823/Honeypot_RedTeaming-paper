# Table 3: transfer between synthetic and real training data

> **PLUMBING CHECK - labels derived from same keywords as features.** Labels come from `rule_label()` (ATT&CK-tactic keyword rules in `session_features.py`), the same keywords that drive the TF-IDF features. These numbers are NOT a paper result; re-run with `--real-labels` / `--synthetic-labels` human labels.

Label source: **rule**. Sessions with >=1 command only. TF-IDF (normalized commands) + 3 numeric features, RandomForest(300, balanced, seed 42). Q1: stratified 3-fold; Q2/Q4: GroupKFold(5) by command template; Q3_dedup: one session per template. CV metrics pooled over folds. Majority baseline predicts the training-set majority class.

| Quadrant | Train | Test | n_train | n_test | Macro-F1 | Accuracy | Majority macro-F1 | Majority acc |
|---|---|---|---|---|---|---|---|---|
| Q1 | synthetic | synthetic | 80 | 120 | 0.553 | 0.717 | 0.106 | 0.358 |
| Q2 | real | real | 1337 | 1672 | 0.557 | 0.926 | 0.187 | 0.879 |
| Q3 | synthetic | real | 120 | 1672 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q3_dedup | synthetic | real_dedup | 120 | 22 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q4 | real+synthetic | real | 1457 | 1672 | 0.553 | 0.926 | 0.187 | 0.879 |

## Label distribution

| Label | Synthetic | Real (sessions) | Real (dedup templates) |
|---|---|---|---|
| recon | 3 | 55 | 4 |
| credential_access | 43 | 0 | 0 |
| privilege_escalation | 23 | 0 | 0 |
| persistence | 42 | 13 | 3 |
| malware_drop | 9 | 52 | 6 |
| resource_hijacking | 0 | 1470 | 5 |
| defense_evasion | 0 | 0 | 0 |
| other | 0 | 82 | 4 |
| **total** | 120 | 1672 | 22 |

## Q3 per-class F1 (synthetic -> real, session-weighted)

| Label | F1 |
|---|---|
| recon | 0.000 |
| credential_access | 0.000 |
| privilege_escalation | 0.000 |
| persistence | 0.000 |
| malware_drop | 0.000 |
| resource_hijacking | 0.000 |
| defense_evasion | 0.000 |
| other | 0.000 |

## Predicted label counts per quadrant

| Quadrant | recon | credential_access | privilege_escalation | persistence | malware_drop | resource_hijacking | defense_evasion | other |
|---|---|---|---|---|---|---|---|---|
| Q1 | 0 | 48 | 30 | 37 | 5 | 0 | 0 | 0 |
| Q2 | 82 | 0 | 0 | 9 | 49 | 1470 | 0 | 62 |
| Q3 | 0 | 1671 | 1 | 0 | 0 | 0 | 0 | 0 |
| Q3_dedup | 0 | 21 | 1 | 0 | 0 | 0 | 0 | 0 |
| Q4 | 82 | 0 | 0 | 10 | 49 | 1469 | 0 | 62 |

Macro-F1 averages only over classes present in the test set. Real labels are broadcast from templates, so the effective real sample size is 22 templates.
