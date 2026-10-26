# 6 Script Reference

## 6.1 Analysis scripts

Table: parse_cyberlab.py options. {#tab:doc-parse widths=4,5,7}

| Option | Default | Meaning |
|---|---|---|
| `--in` | `cyberlab_2019-11-15.json/cowrie_2019-11-15.json` | CyberLab daily file (one JSON array) |
| `--out` | `normalized/real_organic.jsonl` | Output, one session per line |

Table: domain_shift.py options. {#tab:doc-ds widths=4,5,7}

| Option | Default | Meaning |
|---|---|---|
| `--synthetic` | `normalized/all_synthetic_120.jsonl` | Synthetic corpus |
| `--real` | `normalized/real_organic.jsonl` | Real corpus |
| `--out-dir` | `results` | Where `domain_shift.md` and `.json` are written |

Fixed settings inside the script: seed 42, 500 bootstrap samples, 5 × 5 repeated stratified cross-validation for the classifier two-sample test.

Table: make_annotation_sheet.py options. {#tab:doc-sheet widths=4,5,7}

| Option | Default | Meaning |
|---|---|---|
| `--real` | `normalized/real_organic.jsonl` | Real corpus (one item per distinct command sequence) |
| `--synthetic` | `normalized/all_synthetic_120.jsonl` | Synthetic corpus (one item per session) |
| `--out` | `annotation` | Output folder |
| `--seed` | 42 | Shuffle seed |

Table: agreement.py options. {#tab:doc-agree widths=4,5,7}

| Option | Default | Meaning |
|---|---|---|
| `--dir` | `annotation` | Folder with sheets, key and adjudication |
| `--a1`, `--a2` | `sheet_annotator1.csv`, `sheet_annotator2.csv` | Annotator sheets |
| `--adj` | `adjudicated.csv` | Adjudicated labels for disagreements |
| `--key` | `key.csv` | Hidden key |
| `--real` | `normalized/real_organic.jsonl` | Used to broadcast template labels |
| `--md` | `results/annotation_agreement.md` | Agreement report |

Table: train_eval_classifier.py options. {#tab:doc-train widths=4,5,7}

| Option | Default | Meaning |
|---|---|---|
| `--synthetic`, `--real` | required | Corpora |
| `--real-labels`, `--synthetic-labels` | none | Label CSVs (`session_id,label`); without them, keyword-rule labels are used (plumbing check only) |
| `--label-source` | `human` | Name printed in the results header, for example `llm-dual` |
| `--out-dir` | `results` | Output folder |

Fixed settings: TF-IDF with at most 2,000 tokens plus three numeric features; random forest with 300 trees, balanced class weights, seed 42; GroupKFold(5) by template for real data; macro-F1 over classes present in the test set.

## 6.2 Shared library: session_features.py

Table: Main functions of session_features.py. {#tab:doc-sf widths=5,11}

| Function | What it does |
|---|---|
| `normalize_cmd(cmd)` | Cuts leaked chat tokens, lower-cases, masks URLs, IPs, quoted strings, long hex, random tokens, numbers and random busybox tags |
| `segments(cmd)` | Splits a normalised command on `;`, `\|`, `&&`, `\|\|`, newline, `$(` and backtick |
| `verb(segment)` | First word of a segment, ignoring `VAR=value` prefixes and paths |
| `session_verbs(session)` | All verbs of a session |
| `session_tactics(session)` | Set of descriptive tactic names matched by the regular expressions |
| `template_key(session)` | Tuple of normalised commands; equal keys mean the same behaviour template |
| `has_chat_leak(cmd)`, `strip_chat_leak(cmd)` | Detect and remove leaked chat-format tokens |

## 6.3 Testbed scripts

Table: Testbed scripts. {#tab:doc-testbed widths=5,11}

| Script | Purpose |
|---|---|
| `better_ai_attacker.py` | Harness used for the study; settings are described in the report (Section 3.7) |
| `run_docker.bat` | `start-honeypot`, `stop-honeypot`, `tables`, `attack`, `eval` shortcuts around Docker Compose |
| `check.py` | Reads the honeypot's SSH banner a few times |
| `probe.py` | Sends a short test prompt to each candidate model endpoint |
| `validate_logs.py` | Scans old logs for marker-leak corruption |

## 6.4 Report scripts (`report/src/`)

Table: Report build scripts. {#tab:doc-report widths=5,11}

| Script | Purpose |
|---|---|
| `compute_stats.py` | Descriptive statistics for the report |
| `make_diagrams.py` (+ `diagram_lib.py`, `diagrams_a4.py`, `diagrams_software.py`) | All flowcharts and UML diagrams as `.drawio` and `.png` |
| `make_charts.py` | Data charts and console pictures |
| `make_appendix_md.py` | Data appendices generated from project files |
| `build_report.py` | Markdown → Word (`--docs` builds this documentation) |
| `finalize_word.ps1` | Native equations, field refresh and PDF export through Word |
