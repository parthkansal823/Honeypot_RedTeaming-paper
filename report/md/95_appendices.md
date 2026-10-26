# APPENDICES

## Appendix 1: User Manual

This appendix is a complete, step-by-step guide to rebuilding the project from an empty folder, running every stage and reading the outputs. It is written so that a reader who has never seen the project can reproduce it. Commands are shown for Windows (PowerShell) because that is where the project was developed; the Linux and macOS equivalents differ only in path separators.

### A1.1 What you need

Table: Prerequisites for running the project. {#tab:prereq widths=4,4,8}

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11 | Add it to the PATH during installation |
| Git | any recent | To clone the repository |
| Docker Desktop | any recent | Only needed to run the live honeypot; the analysis works without it |
| Disk space | about 2 GB | The raw real dataset is about 600 MB uncompressed |
| API access (optional) | – | Only to generate new synthetic sessions; the 120 existing logs are included |

> **Safety note.** The attacker harness is for use only against a honeypot you own and have configured. It has no scanning or target-discovery capability and connects to exactly one host that you set. Never point it at a system you do not control.

### A1.2 Step 1 — Get the code

```powershell
git clone https://github.com/parthkansal823/Honeypot_RedTeaming-paper.git
cd Honeypot_RedTeaming-paper
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The requirements file installs Paramiko (SSH), scikit-learn, SciPy, NumPy, pandas and the provider SDKs. If you only want to reproduce the analysis, this is all you need: the 120 synthetic session logs are already in `logs/`, and the normalised corpora are in `normalized/`.

### A1.3 Step 2 — Get the real dataset

The real data is not stored in the repository because of its size. Download it from Zenodo and extract it:

```powershell
# Download cyberlab_2019-11-15.json.gz from https://doi.org/10.5281/zenodo.3687527
# Place it in the project root, then:
tar -xzf cyberlab_2019-11-15.json.gz
```

You should now have a folder `cyberlab_2019-11-15.json/` containing `cowrie_2019-11-15.json`.

### A1.4 Step 3 — (Optional) Run the live honeypot

This step is only needed to generate *new* synthetic sessions. To reproduce the reported results you can skip to Step 5.

```powershell
# Start the Cowrie honeypot in Docker (listens on localhost:2222)
.\run_docker.bat start-honeypot

# Check that it answers with an SSH banner
python check.py
```

[@fig:console-docker] in Chapter 4 shows the expected output of these two commands. To switch to the LLM-backed honeypot, edit `cowrie_etc/cowrie.cfg`, change `backend = shell` to `backend = llm`, set the `[llm]` model and endpoint, and restart the container.

### A1.5 Step 4 — (Optional) Generate synthetic sessions

```powershell
# One quick test session against the static honeypot
python better_ai_attacker.py --host 127.0.0.1 --port 2222 `
  --username root --password root `
  --provider bedrock_openai --model deepseek.v3.2 `
  --sessions 1 --output logs\test

# A full batch from a config file (20 sessions per model/backend)
python better_ai_attacker.py --config batch_config.json
```

Each session is saved as one JSON file under the output folder, and a line is printed for each session with its final status ([@fig:console-attacker]). Keep the failed sessions; their counts are part of the result.

### A1.6 Step 5 — Parse and normalise the real data

```powershell
python parse_cyberlab.py --in cyberlab_2019-11-15.json\cowrie_2019-11-15.json `
  --out normalized\real_organic.jsonl
```

The script prints a summary that should read `Parsed 76785 sessions` with `with_commands: 1672` ([@fig:console-parse]). If it instead reports zero sessions, you are almost certainly using the wrong parser: `cowrie_session_parser.py` is for Cowrie's native logs, while the CyberLab export needs `parse_cyberlab.py`.

### A1.7 Step 6 — Run the analysis

```powershell
# Label-free comparison (JSD, Jaccard, C2ST, tactic profiles)
python domain_shift.py

# Attacker tables and paper figures
python generate_paper_tables.py
python make_figures.py

# Four-quadrant transfer experiment with the dual-LLM labels
python train_eval_classifier.py `
  --synthetic normalized\all_synthetic_120.jsonl `
  --real normalized\real_organic.jsonl `
  --real-labels annotation\labels_final.csv `
  --synthetic-labels annotation\labels_final.csv `
  --label-source llm-dual
```

Each script writes its results into the `results/` folder as both a readable `.md` file and a machine-readable `.json` file. Figures are written to `figures/`.

### A1.8 Step 7 — (Optional) Reproduce the labelling

```powershell
# Build the blind annotation sheets
python make_annotation_sheet.py

# After both annotators fill annotation\sheet_annotator1.csv and
# annotation\sheet_annotator2.csv, and the adjudicator fills
# annotation\adjudicated.csv, compute agreement and the final labels:
python agreement.py
```

This regenerates `annotation/labels_final.csv` and `results/annotation_agreement.md` ([@fig:console-agree]). To run the human audit described in future work, hand the two blank sheets to two analysts and follow the same steps.

### A1.9 Step 8 — Build this report

```powershell
# Regenerate the descriptive statistics, diagrams and charts
python report\src\compute_stats.py
python report\src\make_diagrams.py
python report\src\make_charts.py
# Build the Word document from the Markdown chapters
python report\src\build_report.py
```

### A1.10 Where every output lives

Table: Where to find each output. {#tab:outputs widths=6,10}

| You want… | Look in… |
|---|---|
| The raw synthetic sessions | `logs/<attacker>[_vs_qwen.qwen3-32b]/*.json` |
| The normalised corpora | `normalized/all_synthetic_120.jsonl`, `normalized/real_organic.jsonl` |
| Attacker behaviour ([@tab:attackers], [@tab:status-counts]) | `results/tables_1_2.md` / `.json` |
| Label-free comparison ([@tab:structure] to [@tab:cell-jsd]) | `results/domain_shift.md` / `.json` |
| Annotation agreement | `results/annotation_agreement.md`; `annotation/labels_final.csv` |
| Transfer results ([@tab:transfer]) | `results/table3_transfer.md` / `.json` |
| Sensitivity run | `results/sensitivity_dota/` |
| Keyword-rule plumbing check | `results/rule_labels/` |
| Figures | `figures/` (paper), `report/images/` (report) |
| Editable diagrams | `report/diagrams/*.drawio` |

### A1.11 Troubleshooting

Table: Common problems and fixes. {#tab:troubleshoot widths=6,10}

| Symptom | Likely cause and fix |
|---|---|
| `parse_cyberlab.py` reports 0 sessions | Wrong input path, or the file is still gzip-compressed; extract it first |
| The honeypot stops responding | A heavy command (for example `find /`) froze Cowrie; the harness recovers automatically, or restart the container |
| Attacker replies are cut off | The LLM backend is slow; raise `--response-wait` to 3–5 seconds |
| Commands contain English sentences | Chat-format leakage from the model; confirm the `<\|` stripping is active |
| Scores look suspiciously high | Make sure real folds are grouped by template (GroupKFold), not split randomly |
| A model refuses the task | Check the research framing in the system prompt; refusals are recorded as a status, not an error |

## Appendix 2: Annotation Rubric and Protocol

This appendix reproduces the labelling rubric used by both annotators and the adjudicator, so that the labels can be audited or reproduced.

### A2.1 Instructions to annotators

Label each item with exactly **one** primary-intent label. Judge the whole command sequence, not single keywords. Ignore any leaked `<|channel|>…` text (it has already been stripped). Do not open the key file, and do not discuss items with the other annotator until agreement has been computed. Record a confidence of 1 (guess), 2 (fairly sure) or 3 (certain), and use the notes column for anything unusual.

### A2.2 The eight labels

[@tab:rubric] in Chapter 3 gives the definitions. In short: **recon** is looking without changing anything; **credential access** is hunting for secrets, keys or password files; **privilege escalation** is trying to gain more rights; **persistence** is keeping access through cron, SSH keys or account changes; **malware drop** is downloading or running a payload; **resource hijacking** is deploying or inspecting a cryptominer; **defence evasion** is hiding or disabling defences; and **other** is for benign, unclear or noise sessions.

### A2.3 Tie-break order

When several behaviours appear in one session, choose the goal that progressed furthest, in this order (highest first):

resource hijacking → malware drop → persistence → privilege escalation → credential access → defence evasion → recon → other.

### A2.4 Worked rubric examples

Table: Example sessions and their labels under the rubric. {#tab:rubric-examples widths=7,3,6}

| Command sequence (shortened) | Label | Reason |
|---|---|---|
| `whoami; ls -la /root; cat /etc/passwd; sudo -l` | recon | Only looking; `sudo -l` alone is recon |
| `cat /etc/shadow; find / -name id_rsa; cat ~/.ssh/*` | credential access | Actively hunting for secrets and keys |
| `echo "ssh-rsa …" >> ~/.ssh/authorized_keys` | persistence | Adds a key to keep access |
| `cat /proc/cpuinfo; echo …\|chpasswd; wget <url>; sh …` (dota) | resource hijacking | Fingerprint + account takeover + miner kit; top of the tie-break |
| `cd /tmp; wget <url>/x.sh; chmod +x x.sh; ./x.sh` | malware drop | Download and run a payload, no miner identified |
| `/bin/busybox QWERT; cat /bin/busybox` | recon | Capability probe only, no download |

### A2.5 The adjudication record

The adjudicator resolved the 12 items on which the two annotators disagreed, writing a one-line reason for each. The most consequential was the dota template (item A036): one annotator chose malware drop, the other resource hijacking; the adjudicator chose resource hijacking because the session both drops a payload and deploys a miner, and resource hijacking is higher in the tie-break order. That decision sets the label of 1,038 real sessions and was reviewed and confirmed by the authors, and tested in the sensitivity run of Section 4.9.

## Appendix 3: Data Schemas

This appendix documents the main record formats, so that the released files can be read without reverse-engineering them. The relationships between these records are shown in [@fig:datamodel] in Chapter 3.

### A3.1 Raw synthetic session log

One JSON file per session under `logs/`. Key fields:

Table: Fields of a raw synthetic session log. {#tab:schema-raw widths=5,3,8}

| Field | Type | Meaning |
|---|---|---|
| session_id | string | Unique id: provider-model-index-hex |
| attacker_type | string | Always `synthetic_llm` |
| provider, model | string | How the attacker was reached |
| honeypot_backend_label | string | `static` or `dynamic_qwen.qwen3-32b` |
| status | string | One of the eight outcomes in [@tab:statuses] |
| total_turns | integer | Number of turns recorded |
| recovery_attempts | integer | Infrastructure retries before this attempt succeeded |
| turns | array | One object per turn (below) |

Each turn object has: `turn` (index), `timestamp`, `command`, `output`, `latency_sec`, and an optional `note` or `raw_response` for special cases (for example a refusal or a lost connection).

### A3.2 Normalised session (both corpora)

The synthetic logs are converted, and the real data is parsed, into one common per-session shape, stored as JSON Lines.

Table: Fields of a normalised session. {#tab:schema-norm widths=5,3,8}

| Field | Type | Meaning |
|---|---|---|
| session_id | string | Unique id |
| source | string | `cyberlab_2019-11-15` (real) or the synthetic provider |
| attacker_model, honeypot_backend | string | Present for synthetic sessions |
| src_ip | string | Hashed source identifier (real only) |
| country, protocol | string | Geolocation and `ssh`/`telnet` (real only) |
| start, end, duration_s | string / number | Session timing (real only) |
| login_attempts | array | `{username, password, success}` (real only) |
| login_success | boolean | Whether any login succeeded (real only) |
| commands | array of strings | The commands typed, in order |
| downloads | array | `{url, shasum, outfile}` (real only) |
| command_count | integer | Number of commands |

### A3.3 Annotation files

Table: Annotation files and their columns. {#tab:schema-annot widths=5,11}

| File | Columns |
|---|---|
| `annotation_sheet.csv` | item_id, commands (the blind item shown to annotators) |
| `sheet_annotator1.csv`, `sheet_annotator2.csv` | item_id, n_commands, commands, label, confidence, notes |
| `key.csv` (hidden during labelling) | item_id, session_id, source, attacker_model, honeypot_backend, template_size |
| `adjudicated.csv` | item_id, label, rationale |
| `disagreements.csv` | item_id, label_annotator1, label_annotator2, notes1, notes2, commands, label_final |
| `labels_final.csv` | session_id, label, source |

### A3.4 Result files

Every reported number is written by a script into `results/`. Each analysis produces a readable `.md` file and a `.json` file with the same content; the `.json` files are what the report's own charts read, so the numbers in the charts and in the text cannot drift apart.

## Appendix 4: List of Scripts

Table: The project's scripts and what they do. {#tab:scripts widths=5,11}

| Script | Purpose |
|---|---|
| `better_ai_attacker.py` | The attacker harness used for the study (recovery, retries, multiple providers) |
| `ai_attacker.py`, `another_ai_attacker.py` | Earlier harness versions, kept for history |
| `probe.py` | Check which model endpoints answer |
| `check.py` | Read the honeypot's SSH banner a few times |
| `parse_cyberlab.py` | Parse the CyberLab export into normalised sessions |
| `cowrie_session_parser.py` | Parse Cowrie's *native* logs (not the CyberLab format) |
| `convert_live_sessions.py` | Convert harness logs into the normalised schema |
| `session_features.py` | Normalisation, segments, verbs, tactic tags, template keys |
| `domain_shift.py` | Label-free comparison |
| `make_annotation_sheet.py` | Build the blind annotation sheets and key |
| `agreement.py` | Cohen's kappa, disagreements, final labels |
| `train_eval_classifier.py` | Four-quadrant transfer experiment |
| `generate_paper_tables.py` | Attacker behaviour tables |
| `make_figures.py` | Paper figures |
| `validate_logs.py` | Scan logs for corruption from the old marker design |
| `analyze.py`, `analyze_logs.ps1` | Quick per-model summaries |
| `report/src/compute_stats.py` | Descriptive statistics for this report |
| `report/src/make_diagrams.py` | Flowcharts and block diagrams (draw.io + PNG) |
| `report/src/make_charts.py` | Report charts and console pictures |
| `report/src/build_report.py` | Assemble the Word document from the Markdown chapters |

## Appendix 5: Glossary

Table: Glossary of key terms. {#tab:glossary widths=4,12}

| Term | Meaning in this report |
|---|---|
| Honeypot | A decoy system whose only purpose is to be attacked and observed |
| Cowrie | A medium-interaction SSH/Telnet honeypot that emulates a shell |
| Static backend | Cowrie's built-in command emulation |
| LLM backend | A Cowrie mode in which an LLM writes the shell's replies |
| Synthetic session | A session produced by an LLM attacker against our honeypot |
| Real session | A session from the public CyberLab honeynet data |
| Interactive session | A session in which at least one command was typed |
| Behaviour template | A group of sessions with identical normalised command sequences |
| Normalisation | Masking session-specific values so similar behaviours collapse together |
| Verb | The first word of a command segment (for example `ls`, `wget`) |
| Tactic | An ATT&CK-style category of attacker goal (discovery, persistence, …) |
| Intent label | The single primary goal assigned to a session by annotators |
| JSD | Jensen-Shannon divergence; a 0–1 distance between two distributions |
| C2ST | Classifier two-sample test; uses a classifier to measure how separable two sets are |
| AUC | Area under the ROC curve; 0.5 is random, 1.0 is perfect separation |
| Macro-F1 | Average of per-class F1 scores, over the classes present in the test set |
| GroupKFold | Cross-validation that keeps all sessions of one template in the same fold |
| Transfer | Training on one corpus and testing on another |
| dota | The Outlaw-style cryptominer dropper that dominates the real data |
| Chat-format leakage | A model typing its own control tokens and reasoning into the shell |
