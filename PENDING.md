# Honeypot Research Paper — Status

## ✅ Done (2026-10-01)

| Task | Output |
| :-- | :-- |
| 120 synthetic sessions (3 attackers × 2 honeypot backends × 20) | `logs/`, `normalized/all_synthetic_120.jsonl` |
| Real CyberLab data parsed (76,785 sessions; 1,672 with commands; 22 behavior templates after masking Mirai busybox tags) | `parse_cyberlab.py` → `normalized/real_organic.jsonl` |
| Label-free realism analysis (C2ST AUC 1.000, verb JSD, tactic coverage) | `domain_shift.py` → `results/domain_shift.md` |
| Tables 1–2 recomputed (fixed unanchored-regex counts, GPT-OSS chat-leak stripping) | `generate_paper_tables.py` → `results/tables_1_2.md` |
| Blind dual-LLM annotation (184 items, κ = 0.898, 12 adjudicated) | `annotation/`, `agreement.py` → `annotation/labels_final.csv` |
| 4-quadrant transfer matrix (Q3 synth→real macro-F1 0.205, dedup 0.071; Q4 ≈ Q2, no gain) + dota-label sensitivity run | `train_eval_classifier.py` → `results/table3_transfer.md` |
| Rule-label plumbing check (circular, not reported as a result) | `results/rule_labels/`; sensitivity: `results/sensitivity_dota/` |
| Figures (single-column, colorblind-safe) | `make_figures.py` → `figures/` |
| IEEE paper + 25 verified references | `paper/main.tex`, `paper/references.bib`, `paper/main.pdf` |
| Editable Overleaf package | `paper/honeypot_paper_overleaf.zip` |
| Repo: LICENSE (MIT), CITATION.cff, README, .gitignore, CLAUDE.md, agents, hooks | root, `.claude/` |

## 🟡 Before submission
- [ ] Fill in author affiliation in `paper/main.tex` ("Affiliation TBD").
- [ ] Optional but recommended: a human spot-check of the LLM labels (`annotation/sheet_annotator1.csv`, see `annotation/README.md`).
- [ ] Pick the target venue and check its page limit / anonymization rules.
- [ ] Commit and push (nothing is committed yet; datasets stay out of git via `.gitignore`).

## 🟢 Future work (next paper)
- Persona diversification: bot-like archetypes (dropper, cryptominer, credential stuffer) from `honeypot_research_paper_plan.md`, then re-run the transfer matrix.
- More real data (more days / more honeypot networks than one day of CyberLab 2019).
- Test the Docker pipeline end to end (`docker-compose.yml`).
