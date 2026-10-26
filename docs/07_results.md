# 7 Results Summary

All numbers below are copied from `results/`. The project report discusses them in detail.

## 7.1 Label-free comparison

Table: Label-free comparison of synthetic and real sessions. {#tab:doc-lf widths=8,4,4}

| Measure | Synthetic | Real |
|---|---|---|
| Sessions | 120 | 1,672 (22 templates) |
| Share of top-5 templates | 4.2% | 96.2% |
| Mean characters per command | 43.0 | 53.3 |
| Commands chained or piped | 19.4% | 40.3% |
| Verb JSD (synthetic vs real) | 0.700 (95% CI 0.688–0.717) | |
| Verb vocabulary Jaccard | 0.285 | |
| Classifier two-sample AUC (commands / verbs only) | 1.000 / 0.996 | |

## 7.2 Labels

Cohen's κ between the two blind annotators was 0.898 over 184 items (172 agreed, 12 adjudicated). Most synthetic sessions are credential access (87 of 120); most real sessions are resource hijacking (1,040) or persistence (443).

## 7.3 Transfer

Table: Four-quadrant transfer results. {#tab:doc-transfer widths=5,3,3,3}

| Quadrant | Macro-F1 | Accuracy | Majority F1 |
|---|---|---|---|
| Q1 synthetic → synthetic | 0.493 | 0.758 | 0.168 |
| Q2 real → real | 0.983 | 0.992 | 0.001 |
| Q3 synthetic → real | 0.205 | 0.022 | 0.000 |
| Q3-dedup (one per template) | 0.071 | 0.045 | 0.000 |
| Q4 real + synthetic → real | 0.981 | 0.992 | 0.001 |

![Macro-F1 per quadrant.](images/c18_transfer.png){#fig:doc-transfer}

## 7.4 Robustness

Relabelling the dota template (and the other resource-hijacking templates) as malware drop leaves Q3 near zero (0.021) while Q2 and Q4 reach 0.933 and 0.965. The keyword-rule run collapses Q3 to 0.000 but is only a plumbing check.

## 7.5 Other findings

- GPT-OSS-120B leaked chat-format control tokens and reasoning into the shell in 18 of 40 sessions (11 static, 7 dynamic).
- The LLM-backed honeypot raised the share of credential-hunting commands for every attacker and moved only Gemma-3-4B closer to real traffic (JSD 0.798 → 0.746).
- A parser written for native Cowrie logs reads zero sessions from the CyberLab export without raising an error.
