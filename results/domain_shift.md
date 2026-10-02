# Label-free domain-shift analysis: synthetic vs. real

Real: 76,785 sessions, 1,672 with >=1 command, 22 distinct normalized templates. Synthetic: 120 sessions.

## Table 4a: Corpus structure

| Metric | Synthetic | Real (interactive) |
| :--- | ---: | ---: |
| Sessions | 120 | 1,672 |
| Distinct behavior templates | 120 | 22 |
| Share of top-5 templates | 4.2% | 96.2% |
| Median commands / session | 18.0 | 23.0 |
| Mean chars / command | 43.0 | 53.3 |
| Commands with chaining/pipes | 19.4% | 40.3% |

## Table 4b: Share of sessions touching each ATT&CK tactic

| Tactic | Synthetic | Real | Real (template-dedup) |
| :--- | ---: | ---: | ---: |
| discovery | 100.0% | 92.2% | 59.1% |
| credential_access | 97.5% | 1.2% | 18.2% |
| account_manipulation | 34.2% | 89.4% | 50.0% |
| persistence | 18.3% | 0.4% | 4.5% |
| privilege_escalation | 40.0% | 0.1% | 4.5% |
| defense_evasion | 1.7% | 1.3% | 22.7% |
| ingress_tool_transfer | 7.5% | 3.1% | 27.3% |
| execution | 6.7% | 98.1% | 68.2% |
| resource_hijacking | 0.0% | 87.9% | 22.7% |

## Table 4c: Command-verb distribution

- JSD(synthetic, real) = 0.700 (95% bootstrap CI 0.688-0.717); vs. template-dedup real = 0.729 (0.719-0.745). Range 0 (identical) to 1 (disjoint).
- Verb vocabulary Jaccard = 0.285; synthetic vocabulary covers 82.0% of real verb occurrences.
- Top synthetic verbs: ls (712), cat (606), head (243), find (217), grep (116), echo (114), done (76), id (72), pwd (64), whoami (62)
- Top real verbs: grep (8880), cat (8123), echo (6964), uname (4437), rm (3136), awk (2950), wc (2945), head (2945), which (2517), bash (2515)

## Table 4d: Classifier two-sample test (synthetic vs. template-dedup real)

| Features | AUC (mean +/- sd, 5x5 CV) |
| :--- | ---: |
| normalized commands | 1.000 +/- 0.000 |
| verbs only | 0.996 +/- 0.010 |

AUC 0.5 = indistinguishable; 1.0 = perfectly separable.

## Table 4e: Per attacker x backend distance to real (template-dedup)

| Attacker | Backend | n | JSD vs real [95% CI] | Tactics present/absent as in real (of 9) | Sessions with chat-format leak |
| :--- | :--- | ---: | :--- | ---: | ---: |
| DeepSeek-V3.2 | Dynamic Qwen-32B | 20 | 0.785 [0.769, 0.814] | 5 | 0 |
| DeepSeek-V3.2 | Static Cowrie | 20 | 0.783 [0.771, 0.810] | 5 | 0 |
| GPT-OSS-120B | Dynamic Qwen-32B | 20 | 0.746 [0.734, 0.780] | 7 | 7 |
| GPT-OSS-120B | Static Cowrie | 20 | 0.741 [0.730, 0.764] | 5 | 11 |
| Gemma-3-4B | Dynamic Qwen-32B | 20 | 0.746 [0.732, 0.778] | 7 | 0 |
| Gemma-3-4B | Static Cowrie | 20 | 0.798 [0.785, 0.826] | 5 | 0 |

Leaked chat-format tokens and the reasoning text after them are stripped before all analyses; commands the model concatenated without separators cannot be recovered.
