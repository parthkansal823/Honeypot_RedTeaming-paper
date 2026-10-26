# 5 Data Formats

## 5.1 Overview

[@fig:doc-model] shows how the records relate. Raw synthetic logs are converted into the same normalised session shape as the real data; each real template and each synthetic session becomes one annotation item; final labels are broadcast back to sessions.

![Data model.](images/d13_data_model.png){#fig:doc-model}

## 5.2 Raw synthetic session log (`logs/**/<session_id>.json`)

Table: Raw synthetic session log fields. {#tab:doc-raw widths=5,3,8}

| Field | Type | Meaning |
|---|---|---|
| session_id | string | provider-model-index-random hex |
| attacker_type | string | always `synthetic_llm` |
| provider, model | string | how the attacker model was reached |
| honeypot_backend_label | string | `static` or `dynamic_qwen.qwen3-32b` |
| status | string | how the session ended (completed, max_turns_reached, timed_out, attacker_refused, llm_error, connection_lost, honeypot_unresponsive, connection_failed) |
| started_at, ended_at | ISO time | UTC timestamps |
| total_turns | integer | number of recorded turns |
| turns | array | `{turn, timestamp, command, output, latency_sec, note}` |

## 5.3 Normalised session (`normalized/*.jsonl`, one JSON object per line)

Table: Normalised session fields. {#tab:doc-norm widths=5,3,8}

| Field | Type | Meaning |
|---|---|---|
| session_id | string | unique id |
| commands | list of strings | commands in order |
| attacker_model, honeypot_backend, status | string | synthetic sessions only |
| source | string | `cyberlab_2019-11-15` for real sessions |
| src_ip | string | hashed source identifier (real only) |
| country, protocol | string | geolocation code and `ssh` / `telnet` (real only) |
| start, end, duration_s | time / number | session timing (real only) |
| login_attempts | list | `{username, password, success}` (real only) |
| downloads | list | `{url, shasum, outfile}` (real only) |
| command_count | integer | number of commands |

## 5.4 Annotation files (`annotation/`)

Table: Annotation files. {#tab:doc-annot widths=5,11}

| File | Columns |
|---|---|
| `annotation_sheet.csv` | item_id, commands |
| `sheet_annotator1.csv`, `sheet_annotator2.csv` | item_id, n_commands, commands, label, confidence, notes |
| `key.csv` (hidden while labelling) | item_id, session_id, source, attacker_model, honeypot_backend, template_size |
| `adjudicated.csv` | item_id, label, rationale |
| `disagreements.csv` | item_id, label_annotator1, label_annotator2, notes1, notes2, commands, label_final |
| `labels_final.csv` | session_id, label, source |
| `RUBRIC.md` | the eight labels, examples and the tie-break order |

## 5.5 Result files (`results/`)

Every analysis writes a Markdown file for reading and a JSON file with the same numbers for other scripts:

Table: Result files. {#tab:doc-results widths=6,10}

| File | Contents |
|---|---|
| `domain_shift.md`, `.json` | corpus structure, tactics, verbs, JSD, C2ST, per-cell distances |
| `annotation_agreement.md` | κ by subset, confusion matrix, final label counts |
| `table3_transfer.md`, `.json` | four-quadrant results, label distribution, per-class F1, predictions |
| `tables_1_2.md`, `.json` | attacker behaviour per cell and session outcomes |
| `sensitivity_dota/` | transfer results with the dota template relabelled |
| `rule_labels/` | keyword-rule plumbing check (not a result) |
