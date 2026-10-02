# Table 3: transfer between synthetic and real training data

Label source: **llm-dual-dota-as-malware_drop**. Sessions with >=1 command only. TF-IDF (normalized commands) + 3 numeric features, RandomForest(300, balanced, seed 42). Q1: stratified 2-fold; Q2/Q4: GroupKFold(5) by command template; Q3_dedup: one session per template. CV metrics pooled over folds. Majority baseline predicts the training-set majority class.

| Quadrant | Train | Test | n_train | n_test | Macro-F1 | Accuracy | Majority macro-F1 | Majority acc |
|---|---|---|---|---|---|---|---|---|
| Q1 | synthetic | synthetic | 60 | 120 | 0.493 | 0.758 | 0.168 | 0.725 |
| Q2 | real | real | 1337 | 1672 | 0.933 | 0.967 | 0.021 | 0.032 |
| Q3 | synthetic | real | 120 | 1672 | 0.021 | 0.022 | 0.000 | 0.000 |
| Q3_dedup | synthetic | real_dedup | 120 | 22 | 0.067 | 0.045 | 0.000 | 0.000 |
| Q4 | real+synthetic | real | 1457 | 1672 | 0.965 | 0.984 | 0.021 | 0.032 |

## Label distribution

| Label | Synthetic | Real (sessions) | Real (dedup templates) |
|---|---|---|---|
| recon | 14 | 137 | 8 |
| credential_access | 87 | 0 | 0 |
| privilege_escalation | 2 | 0 | 0 |
| persistence | 11 | 443 | 5 |
| malware_drop | 6 | 1092 | 9 |
| resource_hijacking | 0 | 0 | 0 |
| defense_evasion | 0 | 0 | 0 |
| other | 0 | 0 | 0 |
| **total** | 120 | 1672 | 22 |

## Q3 per-class F1 (synthetic -> real, session-weighted)

| Label | F1 |
|---|---|
| recon | 0.000 |
| credential_access | 0.000 |
| privilege_escalation | 0.000 |
| persistence | 0.000 |
| malware_drop | 0.064 |
| resource_hijacking | 0.000 |
| defense_evasion | 0.000 |
| other | 0.000 |

## Predicted label counts per quadrant

| Quadrant | recon | credential_access | privilege_escalation | persistence | malware_drop | resource_hijacking | defense_evasion | other |
|---|---|---|---|---|---|---|---|---|
| Q1 | 12 | 98 | 0 | 5 | 5 | 0 | 0 | 0 |
| Q2 | 193 | 0 | 0 | 435 | 1044 | 0 | 0 | 0 |
| Q3 | 0 | 1636 | 0 | 0 | 36 | 0 | 0 | 0 |
| Q3_dedup | 0 | 21 | 0 | 0 | 1 | 0 | 0 | 0 |
| Q4 | 155 | 4 | 0 | 435 | 1078 | 0 | 0 | 0 |

Macro-F1 averages only over classes present in the test set. Real labels are broadcast from templates, so the effective real sample size is 22 templates.
