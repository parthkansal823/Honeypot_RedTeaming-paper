# 4 Running the Pipeline

All commands run from the repository root. Each step writes its results to files, so the steps can be run one at a time and inspected in between.

## 4.1 Overview

Table: Pipeline steps. {#tab:doc-steps widths=1,5,5,5}

| # | Step | Command | Output |
|---|---|---|---|
| 1 | Parse the real data | `python parse_cyberlab.py` | `normalized/real_organic.jsonl` |
| 2 | Label-free comparison | `python domain_shift.py` | `results/domain_shift.md`, `.json` |
| 3 | Blind annotation sheets | `python make_annotation_sheet.py` | `annotation/` sheets and key |
| 4 | Agreement and final labels | `python agreement.py` | `annotation/labels_final.csv`, `results/annotation_agreement.md` |
| 5 | Transfer experiment | `python train_eval_classifier.py …` (see 4.6) | `results/table3_transfer.md`, `.json` |
| 6 | Attacker tables | `python generate_paper_tables.py` | `results/tables_1_2.md`, `.json` |
| 7 | Paper figures | `python make_figures.py` | `figures/*.png`, `*.pdf` |
| 8 | Report | see `report/README.md` | `report/Project_Report.docx`, `.pdf` |

## 4.2 Optional: the live honeypot

```powershell
.\run_docker.bat start-honeypot     # Cowrie on localhost:2222
python check.py                     # prints the SSH banner a few times
```

To switch Cowrie to the LLM backend, set `backend = llm` in `cowrie_etc/cowrie.cfg`, fill in the `[llm]` section and restart the container. New synthetic batches are run with the harness against this local honeypot only (see the project report, Section 3.7, for its settings).

## 4.3 Step 1: parse the real data

```powershell
python parse_cyberlab.py --in cyberlab_2019-11-15.json\cowrie_2019-11-15.json --out normalized\real_organic.jsonl
```

The summary should report 76,785 sessions and 1,672 with commands. If it reports zero sessions, the wrong parser was used: `cowrie_session_parser.py` reads Cowrie's native JSON-lines logs, not the CyberLab export.

## 4.4 Step 2: label-free comparison

```powershell
python domain_shift.py
```

Prints and saves corpus structure, tactic shares, verb JSD with bootstrap confidence intervals, Jaccard overlap and the classifier two-sample test, plus per-cell distances.

## 4.5 Steps 3 and 4: annotation

`make_annotation_sheet.py` writes two identical blind sheets, a shared item list and a hidden key. Each annotator fills the `label` column of their sheet using `annotation/RUBRIC.md`, without seeing the key or the other sheet. Disagreements are resolved in `annotation/adjudicated.csv`. `agreement.py` then computes Cohen's κ, writes the disagreements file and produces `labels_final.csv`, broadcasting each real template's label to all its sessions.

## 4.6 Step 5: transfer experiment

```powershell
python train_eval_classifier.py --synthetic normalized\all_synthetic_120.jsonl `
  --real normalized\real_organic.jsonl `
  --real-labels annotation\labels_final.csv --synthetic-labels annotation\labels_final.csv `
  --label-source llm-dual
```

Without the label options the script falls back to keyword-rule labels. Those labels share keywords with the features, so that run is only a plumbing check; its output is kept separately in `results/rule_labels/`.

## 4.7 Steps 6 to 8: tables, figures, report

```powershell
python generate_paper_tables.py
python make_figures.py
```

The report has its own build described in `report/README.md`.
