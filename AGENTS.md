# Honeypot research paper — LLM red-team vs. real Cowrie traffic

**Research question:** does a classifier trained on synthetic LLM-attacker sessions transfer to real honeypot traffic?
Authors: Parth Kansal, Keshav. Plan: `honeypot_research_paper_plan.md`. Task list: `PENDING.md`.

## Pipeline (run from repo root, `python` = Python 3.11)
1. `parse_cyberlab.py` — raw CyberLab (Zenodo 10.5281/zenodo.3687527) -> `normalized/real_organic.jsonl`
2. `domain_shift.py` — label-free synthetic-vs-real comparison -> `results/domain_shift.md`
3. `make_annotation_sheet.py` -> `annotation/`; labels = blind dual-LLM (Sonnet A, Opus B, Opus adjudicator) merged by `agreement.py` -> `annotation/labels_final.csv` (kappa 0.898)
4. `train_eval_classifier.py --synthetic normalized/all_synthetic_120.jsonl --real normalized/real_organic.jsonl --real-labels annotation/labels_final.csv --synthetic-labels annotation/labels_final.csv --label-source llm-dual` -> `results/table3_transfer.md` (rule-label plumbing check: `results/rule_labels/`)
5. `generate_paper_tables.py` (Tables 1-2 -> `results/tables_1_2.md`), `make_figures.py` (`figures/`)
6. Paper: `paper/main.tex` (IEEEtran, max 25 refs in `paper/references.bib`, simple professional English). Compile with Tectonic: `tectonic paper/main.tex`

## Data facts (don't re-derive)
- Synthetic: 120 sessions = 3 attackers (DeepSeek-V3.2, Gemma-3-4B, GPT-OSS-120B) x 2 backends (static Cowrie, Qwen3-32B LLM) x 20. All used one "explore the system" prompt.
- Real: 76,785 sessions from 2019-11-15; 1,672 have commands, collapsing to 22 behavior templates (after masking random `busybox ABCDE` tags). One Outlaw "dota" template = 1,038 sessions. IPs are hashed.
- Macro-F1 in Table 3 averages only over classes present in the test set (a zero-support predicted class otherwise fakes a drop).
- CyberLab is NOT Cowrie JSON-lines: it's an array of `{session_id: [events]}`; commands are in `message` as `"CMD: ..."`. `cowrie_session_parser.py` cannot read it.

## Rules
- Never Read/cat the raw dataset or `real_organic.jsonl` whole (hooks block it). Summarize with python, or delegate to the `data-explorer` agent.
- Delegate pipeline runs to `experiment-runner`, label batches to `session-labeler`, draft review to `paper-reviewer`.
- Rule labels (`rule_label()`) come from the same keywords as the features: any result on them is a plumbing check and must be labelled as such in the paper. Reported numbers use the dual-LLM labels in `annotation/labels_final.csv`; the paper must call them LLM-annotated, never human.
- Every number in the paper must come from a file in `results/` (`paper_tables.md` is superseded by `results/tables_1_2.md`).
- `ai_attacker*.py` scripts target only our own Cowrie instance.
- Be terse: short answers, no restating file contents, no full sklearn reports in chat.
