# 4 Results Analysis and Validation

This chapter reports what we built and what we found. Every number in it comes from a file in the project's `results/` folder, from `report/data/report_stats.json` (descriptive statistics computed for this report) or directly from the session logs. We start with the tools and the deployed system, then describe both datasets, and then answer the research questions one by one. The chapter closes with the validation steps, the threats to validity and the project management practices we used.

## 4.1 Implementation Using Modern Engineering Tools

[@tab:tools] lists the tools used and what each one did. All analysis code is in Python 3.11 and runs on an ordinary laptop; no GPU was needed.

Table: Engineering tools used in the project. {#tab:tools widths=4,4,8}

| Tool | Version / form | Used for |
|---|---|---|
| Python | 3.11 | All scripts |
| Paramiko | ≥ 3.4 | SSH client inside the attacker harness |
| Cowrie (Oosterhof, 2015) | Docker image `cowrie/cowrie:latest` | Honeypot (static and LLM backends) |
| Docker and Docker Compose (Merkel, 2014) | Compose file v3.8 | Reproducible honeypot and analysis containers |
| AWS Bedrock (OpenAI-compatible endpoint) | Pay-per-use API | Attacker models and the Qwen3-32B honeypot backend |
| scikit-learn (Pedregosa et al., 2011) | ≥ 1.4 | TF-IDF, logistic regression, random forest, cross-validation, kappa |
| SciPy (Virtanen et al., 2020) and NumPy (Harris et al., 2020) | ≥ 1.12 / ≥ 1.26 | Jensen-Shannon distance, numeric arrays |
| Matplotlib (Hunter, 2007) | 3.x | All charts (colour-blind-safe palette; Okabe and Ito, 2008) |
| draw.io / diagrams.net | `.drawio` XML | Editable flowcharts and block diagrams (`report/diagrams/`) |
| Git and GitHub | Public repository | Version control and release of code and results |
| LaTeX (Springer LNCS class), Overleaf, Tectonic | `llncs.cls` | Research paper |
| Microsoft Word | 365 | This report (styles, captions, fields, equations) |
| Claude Code and Claude models | Sonnet 5.5, Opus 5.5 | Blind annotation and adjudication; engineering assistance |

[@fig:console-docker] and [@fig:console-attacker] show what running the system looks like. The honeypot starts with one command, a quick banner check confirms that it is answering, and each attacker batch prints one line per session with its outcome.

![Starting the Cowrie honeypot in Docker and checking that it answers with an SSH banner (typical console output).](images/t01_docker_start.png){#fig:console-docker}

![Running one attacker batch; each line reports the outcome of one session (example from the DeepSeek-V3.2 static batch).](images/t02_attacker_run.png){#fig:console-attacker}

## 4.2 Design Drawings and Schematics

The deployed system is shown in [@fig:deploy]. Two containers share a private bridge network: the Cowrie honeypot listens on port 2222, and the analysis container holds the harness and all scripts. When the LLM backend is enabled, Cowrie sends each command to the Qwen3-32B model over HTTPS; the attacker container calls the attacker models over a separate HTTPS connection.

![Docker deployment of the testbed.](images/d10_deployment_docker.png){#fig:deploy landscape}

[@tab:repo] gives the layout of the repository, so that every artefact in this report can be found.

Table: Repository layout. {#tab:repo widths=5,11}

| Path | Contents |
|---|---|
| `better_ai_attacker.py` | Attacker harness used for the 120 sessions (earlier versions: `ai_attacker.py`, `another_ai_attacker.py`) |
| `cowrie_etc/cowrie.cfg` | Honeypot configuration (backend switch) |
| `docker-compose.yml`, `Dockerfile.attacker`, `run_docker.bat` | Containers and Windows helper script |
| `logs/<attacker>[_vs_qwen.qwen3-32b]/` | 120 raw session logs (20 per cell) and `infra_events.log` |
| `parse_cyberlab.py`, `cowrie_session_parser.py` | Parsers for the CyberLab export and for native Cowrie logs |
| `session_features.py` | Normalisation, segments, verbs, tactic tags, template keys |
| `normalized/` | `all_synthetic_120.jsonl`, `real_organic.jsonl` |
| `domain_shift.py` | Label-free comparison → `results/domain_shift.md/.json` |
| `make_annotation_sheet.py`, `agreement.py`, `annotation/` | Blind sheets, rubric, labels, agreement, adjudication |
| `train_eval_classifier.py` | Four-quadrant experiment → `results/table3_transfer.md/.json` |
| `generate_paper_tables.py`, `make_figures.py` | Attacker tables and paper figures |
| `results/` | All reported numbers, including `sensitivity_dota/` and `rule_labels/` |
| `paper/` | Springer LNNS paper (Overleaf project) |
| `report/` | This report: Markdown sources, figures, draw.io files, build scripts |
| `docs/` | Project documentation |

## 4.3 Characterising the Real Data

### 4.3.1 Overall profile

The CyberLab file for 15 November 2019 contains 76,785 sessions ([@tab:real-profile]). Most of them never get past the login prompt or log in and leave at once: the median session lasts under three seconds. About 90% of sessions used SSH and the rest Telnet. Only 1,672 sessions (2.18%) typed at least one command, and those are the sessions this study is about. [@fig:funnel] shows how quickly the data shrinks from raw sessions to distinct behaviours.

Table: Profile of the real CyberLab data (15 November 2019). {#tab:real-profile widths=8,4,4}

| Measure | Value | Share |
|---|---|---|
| Sessions | 76,785 | 100% |
| SSH / Telnet sessions | 69,188 / 7,597 | 90.1% / 9.9% |
| Sessions with a successful login | 36,685 | 47.8% |
| Login attempts recorded | 68,861 | – |
| Sessions with a file download or upload event | 1,085 | 1.4% |
| Sessions with at least one command (interactive) | 1,672 | 2.18% |
| Distinct hashed sources among interactive sessions | 476 | – |
| Distinct behaviour templates among interactive sessions | 22 | – |
| Median / mean session duration | 2.76 s / 32.1 s | – |
| Median / maximum commands per interactive session | 23 / 50 | – |

![From raw sessions to behaviours (log scale), and the protocol split.](images/c01_real_funnel.png){#fig:funnel}

### 4.3.2 Where the traffic came from, and what it tried

The source countries ([@fig:countries]) are reported by the dataset's geolocation field; sources themselves are hashed. China, Ireland, Russia and the Seychelles lead the full set, and China, the United States, France and South Korea lead the interactive subset. These rankings describe hosting locations of attacking machines on one day, not the nationality of any person.

![Top source countries for all sessions and for interactive sessions.](images/c03_countries.png){#fig:countries}

The credentials tried are what one would expect from automated brute-forcing ([@fig:credentials]): `root` is by far the most common username and `admin` the most common password. The odd pair `nproc`/`nproc` appears 1,463 times; it is a botnet that first runs `nproc` (count CPU cores) and apparently reuses the string as a login guess.

![Most frequent usernames and passwords in login attempts (log scale).](images/c04_credentials.png){#fig:credentials}

### 4.3.3 A few scripts dominate

The 1,672 interactive sessions fall into only 22 behaviour templates, and the distribution is extremely skewed ([@fig:templates]). The five largest templates cover 96.2% of interactive sessions, and six templates were seen only once.

![Number of sessions in each of the 22 real behaviour templates.](images/c02_template_sizes.png){#fig:templates}

Table: The largest real behaviour templates (normalised commands; first steps only). {#tab:top-templates widths=2,2,4,8}

| Rank | Sessions | Commands | What the template does (first steps) |
|---|---|---|---|
| 1 | 1,038 | 23 | Counts CPU cores, resets the root password with `chpasswd`, writes and removes a hidden marker file in `/var/tmp`, checks memory and CPU model, then decodes and runs a base64 shell script that unpacks a "dota" kit, starts an SSH scanner and runs the kit's setup; an Outlaw-style cryptominer dropper (Trend Micro, 2018) |
| 2 | 429 | 19 | Same CPU fingerprinting, changes the password with `passwd`, writes and removes the marker file; no payload to unpack |
| 3 | 63 | 6 | Mirai-style shell escape (`shell`, `sh`, `enable`, `system`), random `busybox` tag probe, reads the busybox binary |
| 4 | 43 | 10 | Shell escape, reads `/proc/mounts`, probes writable directories such as `/dev/shm` with the busybox tag |
| 5 | 36 | 2 | Changes into a writable directory, downloads a script with `wget` and runs it with `sh` |

The largest template is worth describing in full, because it decides much of the result. It is a cryptomining dropper that matches the Outlaw group's published behaviour (Trend Micro, 2018): profile the CPU, take over the account, remove traces of earlier infections, then fetch and start a miner and a scanner. It is the same script run 1,038 times from many hosts. To a classifier it is one example, not 1,038, which is why we report per-template results throughout.

[@fig:console-parse] shows the parser's own summary, which matches these counts.

![Output of the CyberLab parser.](images/t04_parse_cyberlab.png){#fig:console-parse}

## 4.4 How the LLM Attackers Behaved (RQ1, RQ4)

### 4.4.1 Overview

All 120 synthetic sessions used the same prompt, so differences between cells come from the attacker model and the honeypot backend. [@tab:attackers] summarises each cell.

Table: Attacker behaviour per cell (20 sessions each). Recon and credential values are percentages of commands and can overlap. Latency is the mean time until output goes quiet; change is relative to the static backend. {#tab:attackers widths=4,2,2,2,2,2,2,3,2}

| Attacker / backend | Mean turns | Commands | Unique | Recon % | Cred. % | PrivEsc % | Latency (s) / change | Leak sessions |
|---|---|---|---|---|---|---|---|---|
| DeepSeek-V3.2 / static | 13.5 | 270 | 124 | 44.4 | 27.4 | 0.7 | 4.40 / – | 0 |
| DeepSeek-V3.2 / Qwen3-32B | 16.9 | 337 | 148 | 46.3 | 34.4 | 2.1 | 3.65 / −17.1% | 0 |
| Gemma-3-4B / static | 21.0 | 420 | 158 | 57.4 | 11.0 | 6.9 | 4.43 / – | 0 |
| Gemma-3-4B / Qwen3-32B | 18.5 | 370 | 199 | 47.8 | 20.0 | 7.0 | 2.38 / −46.3% | 0 |
| GPT-OSS-120B / static | 19.5 | 390 | 280 | 54.9 | 48.5 | 13.8 | 4.42 / – | 11 |
| GPT-OSS-120B / Qwen3-32B | 16.2 | 325 | 233 | 39.4 | 65.2 | 7.7 | 5.51 / +24.8% | 7 |

The three models behaved quite differently under the same instruction. On the static honeypot, DeepSeek-V3.2 ran the shortest sessions (13.5 turns on average) and Gemma-3-4B the longest (21.0). GPT-OSS-120B was the most varied, with 280 unique commands against 158 for Gemma-3-4B and 124 for DeepSeek-V3.2, and it was also the most interested in secrets: 48.5% of its static-backend commands matched our credential keywords, against 27.4% for DeepSeek-V3.2 and 11.0% for Gemma-3-4B ([@fig:attacker-cats]).

![Share of commands matching each keyword category, per attacker and honeypot backend.](images/c19_attacker_categories.png){#fig:attacker-cats}

![Total and unique commands per cell.](images/c07_commands.png){#fig:commands}

All agents opened in a very similar way. Of the 120 sessions, 48 started with `id` and 35 with `whoami` ([@fig:first]); this is the textbook first move of a human penetration tester, and almost never the first move of the bots in the real data, which usually start by counting CPU cores or escaping a restricted shell.

![The first command of each synthetic session.](images/c08_first_commands.png){#fig:first}

[@fig:console-json] shows the beginning of one real synthetic log, so the reader can see exactly what the harness records.

![The first three turns of a DeepSeek-V3.2 session against the static honeypot (output shortened).](images/t03_session_json.png){#fig:console-json}

### 4.4.2 Effect of the LLM-backed honeypot

The credential share rose on the LLM-backed honeypot for all three attackers: from 27.4% to 34.4% for DeepSeek-V3.2, from 11.0% to 20.0% for Gemma-3-4B and from 48.5% to 65.2% for GPT-OSS-120B. A plausible reason is that an LLM shell invents believable files and configuration on demand, which gives an agent looking for secrets more to follow up; we did not test this explanation directly.

The dynamic backend was not uniformly slower ([@fig:latency]). Mean latency fell by 17.1% for DeepSeek-V3.2 and by 46.3% for Gemma-3-4B, and rose by 24.8% for GPT-OSS-120B. Medians are close to 1.5 seconds everywhere, which is the idle-timeout itself: most replies arrive quickly and the reader then waits out the 1.5 s of silence. The means are pulled up by a minority of slow replies, so they depend heavily on which commands each attacker chose (a static `find /` can take much longer than an LLM's invented answer). We therefore do not read latency as a property of the backend alone.

![Mean and median latency per command.](images/c06_latency.png){#fig:latency}

### 4.4.3 How sessions ended

Sessions ended in different ways for different models ([@fig:status], [@tab:status-counts]). DeepSeek-V3.2 almost always finished by itself, refusing once. Gemma-3-4B often ran into the turn limit on the static backend. GPT-OSS-120B rarely said `DONE` on the static backend and, on the dynamic backend, was the least reliable attacker: 10 sessions lost the SSH connection, 6 ended with an LLM error and only 4 completed. It never refused.

![How the 20 sessions in each cell ended.](images/c05_session_status.png){#fig:status}

Table: Session status counts per cell (C completed, M turn limit, L connection lost, E LLM error, R refused, T timed out). {#tab:status-counts widths=6,2,2,2,2,2,2}

| Attacker / backend | C | M | L | E | R | T |
|---|---|---|---|---|---|---|
| DeepSeek-V3.2 / static | 19 | 0 | 0 | 0 | 1 | 0 |
| DeepSeek-V3.2 / Qwen3-32B | 20 | 0 | 0 | 0 | 0 | 0 |
| Gemma-3-4B / static | 11 | 8 | 0 | 0 | 0 | 1 |
| Gemma-3-4B / Qwen3-32B | 18 | 2 | 0 | 0 | 0 | 0 |
| GPT-OSS-120B / static | 3 | 17 | 0 | 0 | 0 | 0 |
| GPT-OSS-120B / Qwen3-32B | 4 | 0 | 10 | 6 | 0 | 0 |

## 4.5 A Contamination Finding: Chat-Format Token Leakage

In 18 of its 40 sessions (11 static, 7 dynamic), GPT-OSS-120B sent text such as `<|channel|>analysis<|message|>` followed by its own private reasoning as if it were a shell command. These are control tokens from the model's own chat template. The harness, which treats the whole reply as one command, typed this text into Cowrie. Neither DeepSeek-V3.2 nor Gemma-3-4B did this.

If left in place, the leaks would turn long English sentences into "commands" and distort every statistic in this chapter: command lengths, verb counts, tactic tags and the classifier features. Before any analysis we therefore cut each command at the first `<|` and drop everything after it. A small number of replies glued several commands together without separators; these cannot be repaired automatically and remain a known source of noise. For anyone building a similar pipeline, the lesson is simple: check every reply for known control tokens before sending it, and record the raw reply separately from the executed command (Greshake et al., 2023, describe related risks of untrusted text flowing through LLM pipelines).

## 4.6 Synthetic Versus Real Without Labels (RQ2, RQ4)

### 4.6.1 Corpus structure

The two corpora are built very differently ([@fig:structure], [@tab:structure]). Every synthetic session is unique, while real traffic is a handful of scripts repeated many times. Real commands are longer and are chained or piped about twice as often, which fits automated one-liners. Median session length is similar.

![Corpus structure: synthetic versus real.](images/c10_corpus_structure.png){#fig:structure}

Table: Corpus structure (results/domain_shift.md, Table 4a). {#tab:structure widths=8,4,4}

| Metric | Synthetic | Real (interactive) |
|---|---|---|
| Sessions | 120 | 1,672 |
| Distinct behaviour templates | 120 | 22 |
| Share of top-5 templates | 4.2% | 96.2% |
| Median commands per session | 18 | 23 |
| Mean characters per command | 43.0 | 53.3 |
| Commands with chaining or pipes | 19.4% | 40.3% |

### 4.6.2 Tactic profiles

The tactic profiles barely overlap ([@fig:tactics], [@tab:tactic-shares]). All synthetic sessions involved discovery and 97.5% involved credential access; privilege escalation (40.0%) and persistence (18.3%) were also common. Real sessions almost never touched credential access (1.2%), persistence (0.4%) or privilege escalation (0.1%). Instead they ran execution (98.1%), account manipulation (89.4%) and resource hijacking (87.9%), for which the synthetic shares were 6.7%, 34.2% and 0.0%. Discovery is the only tactic both sides use heavily.

![Share of sessions touching each tactic at least once.](images/c20_tactics.png){#fig:tactics}

Table: Share of sessions touching each tactic (results/domain_shift.md, Table 4b). {#tab:tactic-shares widths=6,3,3,4}

| Tactic | Synthetic | Real | Real (one per template) |
|---|---|---|---|
| Discovery | 100.0% | 92.2% | 59.1% |
| Credential access | 97.5% | 1.2% | 18.2% |
| Account manipulation | 34.2% | 89.4% | 50.0% |
| Persistence | 18.3% | 0.4% | 4.5% |
| Privilege escalation | 40.0% | 0.1% | 4.5% |
| Defence evasion | 1.7% | 1.3% | 22.7% |
| Ingress tool transfer | 7.5% | 3.1% | 27.3% |
| Execution | 6.7% | 98.1% | 68.2% |
| Resource hijacking | 0.0% | 87.9% | 22.7% |

The template view is less extreme: counted once per template, real discovery drops to 59.1%, execution to 68.2% and resource hijacking to 22.7%. The very high session-level shares come from a few heavily repeated scripts. Neither view, however, looks like the synthetic profile.

### 4.6.3 Command verbs

The verb distributions are far apart ([@fig:verbs], [@tab:verb-stats]). The agents mostly browse files (`ls`, `cat`, `head`, `find`); the bots mostly process text and fingerprint the system (`grep`, `cat`, `echo`, `uname`). Interestingly, the synthetic vocabulary is not small: it covers 82.0% of real verb occurrences. The agents know the commands; they use them in very different proportions and for different purposes.

![The ten most frequent verbs in each corpus.](images/c09_top_verbs.png){#fig:verbs}

Table: Verb-distribution statistics (results/domain_shift.md, Table 4c). {#tab:verb-stats widths=9,7}

| Statistic | Value |
|---|---|
| JSD(synthetic, real), base 2 | 0.700 (95% CI 0.688–0.717) |
| JSD(synthetic, real templates) | 0.729 (95% CI 0.719–0.745) |
| Jaccard index of verb vocabularies | 0.285 |
| Real verb occurrences covered by the synthetic vocabulary | 82.0% |
| Top synthetic verbs | ls (712), cat (606), head (243), find (217), grep (116) |
| Top real verbs | grep (8,880), cat (8,123), echo (6,964), uname (4,437), rm (3,136) |

### 4.6.4 Classifier two-sample test

A simple classifier separates the corpora almost perfectly ([@tab:c2st]). With normalised commands the AUC is 1.000 ± 0.000, and with verbs alone it is still 0.996 ± 0.010. The verb-only result shows that the separation does not depend on file paths or arguments. By the domain-adaptation bound of Ben-David et al. (2010), such easy separability is a warning sign for transfer, although it does not prove that every downstream task must fail.

Table: Classifier two-sample test, synthetic versus real templates (results/domain_shift.md, Table 4d). {#tab:c2st widths=8,8}

| Features | AUC (mean ± sd, 5 × 5 CV) |
|---|---|
| Normalised commands | 1.000 ± 0.000 |
| Verbs only | 0.996 ± 0.010 |

[@fig:console-ds] shows the first part of the script's output.

![Beginning of the label-free analysis output.](images/t05_domain_shift.png){#fig:console-ds}

### 4.6.5 Which synthetic cell is closest to real?

All six cells stay far from real traffic ([@fig:cell-jsd], [@tab:cell-jsd]). Their JSD to the real templates ranges from 0.741 to 0.798. Only for Gemma-3-4B do the confidence intervals of the two backends not overlap: the LLM backend brought it closer (0.746 against 0.798). For DeepSeek-V3.2 (0.785 against 0.783) and GPT-OSS-120B (0.746 against 0.741) the dynamic value is slightly higher and the intervals overlap. With 20 sessions per cell and no correction for multiple comparisons, we make no claim about a significant ordering of the cells.

![Verb JSD between each attacker × backend cell and the real templates, with 95% bootstrap confidence intervals.](images/c21_condition_jsd.png){#fig:cell-jsd}

Table: Distance of each cell to the real templates (results/domain_shift.md, Table 4e). {#tab:cell-jsd widths=4,4,5,3}

| Attacker | Backend | JSD [95% CI] | Tactics matching real (of 9) |
|---|---|---|---|
| DeepSeek-V3.2 | Static Cowrie | 0.783 [0.771, 0.810] | 5 |
| DeepSeek-V3.2 | Qwen3-32B | 0.785 [0.769, 0.814] | 5 |
| Gemma-3-4B | Static Cowrie | 0.798 [0.785, 0.826] | 5 |
| Gemma-3-4B | Qwen3-32B | 0.746 [0.732, 0.778] | 7 |
| GPT-OSS-120B | Static Cowrie | 0.741 [0.730, 0.764] | 5 |
| GPT-OSS-120B | Qwen3-32B | 0.746 [0.734, 0.780] | 7 |

## 4.7 Annotation Results

### 4.7.1 Agreement

The two blind annotators agreed well ([@tab:kappa]). Raw agreement over all 184 items was 0.935 and Cohen's kappa was 0.898, which falls in the "almost perfect" band of Landis and Koch (1977). Agreement was slightly lower on synthetic items (κ = 0.835) than on real ones (κ = 0.873). The annotators agreed on 172 items and the adjudicator resolved the other 12.

Table: Inter-annotator agreement (results/annotation_agreement.md). {#tab:kappa widths=5,3,4,4}

| Subset | Items | Raw agreement | Cohen's κ |
|---|---|---|---|
| All | 184 | 0.935 | 0.898 |
| Real | 64 | 0.953 | 0.873 |
| Synthetic | 120 | 0.925 | 0.835 |

![Confusion between the two annotators (rows: annotator A; columns: annotator B).](images/c11_annotation_confusion.png){#fig:confusion}

The confusion matrix ([@fig:confusion]) shows where the disagreements were. The most common split was *recon* against *credential access* on synthetic sessions that read sensitive files while exploring, which is a genuinely borderline case under the rubric. One disagreement mattered far more than all the others: on the large "dota" template, one annotator chose *malware drop* and the other *resource hijacking*. The adjudicator chose *resource hijacking* by the rubric's tie-break, and that single decision sets the label of 1,038 real sessions. The authors reviewed and confirmed it, and Section 4.9 tests what happens if it is changed.

![Output of the agreement script.](images/t07_agreement.png){#fig:console-agree}

### 4.7.2 Final labels

The final label sets of the two corpora hardly overlap ([@fig:labels], [@tab:labels]). Most synthetic sessions are credential access (87 of 120, 72.5%), a class that never occurs in the real data. Most real sessions are resource hijacking (1,040) or persistence (443), and resource hijacking never occurs in the synthetic data. The second-largest real template shows how thin some boundaries are: it performs the same fingerprinting as the dota dropper and changes a password, but has no payload, so it is labelled persistence.

![Final label distribution as a share of each corpus (counts on top of bars).](images/c12_label_distribution.png){#fig:labels}

Table: Final label counts. Real labels are copied from 22 templates, so the effective real sample size is 22. {#tab:labels widths=6,3,4,4}

| Label | Synthetic | Real sessions | Real templates |
|---|---|---|---|
| Recon | 14 | 137 | 8 |
| Credential access | 87 | 0 | 0 |
| Privilege escalation | 2 | 0 | 0 |
| Persistence | 11 | 443 | 5 |
| Malware drop | 6 | 52 | 6 |
| Resource hijacking | 0 | 1,040 | 3 |
| Defence evasion, other | 0 | 0 | 0 |
| **Total** | **120** | **1,672** | **22** |

## 4.8 The Transfer Experiment (RQ3)

### 4.8.1 Main results

[@tab:transfer] and [@fig:transfer] give the main result of the project.

Table: Transfer results (results/table3_transfer.md). For Q1, Q2 and Q4, n_train is the mean training size per fold and n_test counts pooled out-of-fold predictions. F1 is macro-F1 over classes present in the test set. {#tab:transfer widths=3,5,2,2,2,2,2,2}

| Quadrant | Train → test | n_train | n_test | Macro-F1 | Accuracy | Majority F1 | Majority acc. |
|---|---|---|---|---|---|---|---|
| Q1 | Synthetic → synthetic | 60 | 120 | 0.493 | 0.758 | 0.168 | 0.725 |
| Q2 | Real → real | 1,337 | 1,672 | 0.983 | 0.992 | 0.001 | 0.001 |
| Q3 | Synthetic → real | 120 | 1,672 | 0.205 | 0.022 | 0.000 | 0.000 |
| Q3-dedup | Synthetic → real, one per template | 120 | 22 | 0.071 | 0.045 | 0.000 | 0.000 |
| Q4 | Real + synthetic → real | 1,457 | 1,672 | 0.981 | 0.992 | 0.001 | 0.001 |

![Macro-F1 of the classifier and of the majority-class baseline in each quadrant.](images/c18_transfer.png){#fig:transfer}

**Q1 (synthetic → synthetic)** is moderate: macro-F1 0.493 and accuracy 0.758, above its majority baseline (0.168 and 0.725). With only 60 training sessions per fold and two classes of six or fewer examples, this is roughly what one would expect.

**Q2 (real → real)** is easy: macro-F1 0.983 and accuracy 0.992 on templates the model never saw during training. We treat Q2 as an upper reference rather than a realistic estimate, because scripts that are close variants of each other can form different templates in different folds, and real templates with the same label often share most of their commands.

The **majority baselines** for Q2 and Q4 are close to zero (0.001) by construction. GroupKFold places the whole dota template in one test fold, whose training majority is then persistence; in the other folds the training majority is resource hijacking, which hardly occurs in their test sets.

**Q3 (synthetic → real)** fails. Macro-F1 is 0.205 and accuracy 0.022; with one session per template (Q3-dedup) the figures are 0.071 and 0.045. The model labels 1,636 of the 1,672 real sessions as credential access ([@fig:q3]), a class that does not exist in the real labels. The only class it recognises is malware drop, with a per-class F1 of 0.818, and the entire macro-F1 comes from that one class ([@tab:q3-classes]).

**Q4 (real + synthetic → real)** shows no improvement: 0.981 against 0.983 for Q2, with the same accuracy (0.992). Adding the synthetic sessions neither helps nor seriously harms.

![True labels of the real sessions and the labels predicted by the synthetic-trained model.](images/c13_q3_predictions.png){#fig:q3}

Table: Per-class F1 of the synthetic-trained model on real sessions (Q3). {#tab:q3-classes widths=8,4,4}

| Label | Real sessions with this label | F1 |
|---|---|---|
| Recon | 137 | 0.000 |
| Persistence | 443 | 0.000 |
| Malware drop | 52 | 0.818 |
| Resource hijacking | 1,040 | 0.000 |

Table: Number of sessions predicted in each class per quadrant (results/table3_transfer.md). {#tab:predicted widths=3,2,3,3,3,3,3}

| Quadrant | Recon | Credential access | Privilege esc. | Persistence | Malware drop | Resource hijacking |
|---|---|---|---|---|---|---|
| Q1 | 12 | 98 | 0 | 5 | 5 | 0 |
| Q2 | 142 | 0 | 0 | 439 | 51 | 1,040 |
| Q3 | 0 | 1,636 | 0 | 0 | 36 | 0 |
| Q3-dedup | 0 | 21 | 0 | 0 | 1 | 0 |
| Q4 | 142 | 4 | 0 | 435 | 52 | 1,039 |

![Console output of the transfer experiment.](images/t06_transfer.png){#fig:console-transfer}

### 4.8.2 Why transfer fails

Part of the failure is a **label-space problem**. A model trained without any resource-hijacking examples cannot predict that label, which covers most real sessions. But the failure goes beyond missing classes: *recon* and *persistence* exist in both corpora and still score an F1 of 0.000. Synthetic persistence is an intruder writing a reverse-shell cron entry or appending an SSH key; real persistence is a bot script that changes a password between fingerprinting steps. The label is the same but the behaviour is not. This is concept shift in the sense of Moreno-Torres et al. (2012), on top of a strong label shift. Correcting for label shift alone (Lipton, Wang and Smola, 2018) would not fix it.

## 4.9 Sensitivity and Robustness Checks

### 4.9.1 Does the dota label drive the result?

Because one label decides 1,038 sessions, we reran the experiment with all three resource-hijacking templates, including dota, relabelled as malware drop ([@tab:sensitivity], [@fig:sources]). Q3 stayed near zero (macro-F1 0.021) and Q3-dedup at 0.067, while Q2 and Q4 reached 0.933 and 0.965. The transfer failure does not depend on this label. The small difference between Q2 and Q4 in this run (0.933 against 0.965) goes the other way from the main run, so neither run shows a consistent benefit from synthetic data.

Table: Main labels versus the dota sensitivity run (macro-F1 / accuracy). {#tab:sensitivity widths=4,6,6}

| Quadrant | Main (dual-LLM labels) | Sensitivity: dota as malware drop |
|---|---|---|
| Q1 | 0.493 / 0.758 | 0.493 / 0.758 |
| Q2 | 0.983 / 0.992 | 0.933 / 0.967 |
| Q3 | 0.205 / 0.022 | 0.021 / 0.022 |
| Q3-dedup | 0.071 / 0.045 | 0.067 / 0.045 |
| Q4 | 0.981 / 0.992 | 0.965 / 0.984 |

![Macro-F1 per quadrant under three label sources. The keyword-rule labels are a plumbing check only and are not a result.](images/c14_label_sources.png){#fig:sources}

### 4.9.2 The keyword-rule plumbing check

With labels from our keyword rules (Design A), Q3 also collapsed to a macro-F1 of 0.000. We do not count this as evidence for or against transfer, because those labels share keywords with the features; it only confirms that the code path runs end to end. The rule labels also show how badly keyword rules describe real traffic: they put 1,470 of 1,672 real sessions into resource hijacking and 82 into *other*.

### 4.9.3 Other robustness choices

Three further choices protect the main result: the C2ST was repeated with verbs only (Section 4.6.4); the transfer test was repeated on one session per template (Q3-dedup); and all cross-validation of real data groups sessions by template. Each of these guards against a known way of inflating results (Arp et al., 2022; Kapoor and Narayanan, 2023).

## 4.10 Answers to the Research Questions

Table: Research questions, hypotheses and outcomes. {#tab:answers widths=2,7,7}

| ID | Outcome | Evidence |
|---|---|---|
| RQ1 | The three attackers behaved very differently under the same prompt (session length, variety, interest in secrets, how sessions ended) | [@tab:attackers], [@tab:status-counts]; [@fig:attacker-cats] to [@fig:status] |
| RQ2 | Synthetic and real sessions are almost perfectly separable; the gap is about intent | JSD 0.700; C2ST AUC 1.000 (verbs only 0.996); tactic profiles |
| RQ3 | No transfer and no augmentation benefit | Q3 macro-F1 0.205 (dedup 0.071) vs Q2 0.983; Q4 0.981 |
| RQ4 | The LLM backend helped only the smallest attacker and raised credential hunting for all | Gemma JSD 0.798 → 0.746; others unchanged within CI |
| H1 | Supported | JSD ≫ 0.5; AUC ≈ 1 |
| H2 | Supported | Q3 ≪ Q2, also after the dota sensitivity run |
| H3 | Not supported | Only one of three attackers moved closer to real traffic |

## 4.11 Discussion

### 4.11.1 The gap is about intent

The agents did not fail at their task; they did a different task. They were asked to act like a curious intruder, and they listed directories, read configuration files and searched for keys, which is exactly what a capture-the-flag player or a penetration tester does (Happe and Cito, 2023; Shao et al., 2024). The real traffic on our sample day was driven by bots that profiled the CPU, took over the account and launched a scanner and miner kit (Trend Micro, 2018). Nobody asked the agents to behave like that population, and they did not. The finding of Barron and Nikiforakis (2017), that bots behave the same regardless of environment, helps explain why the LLM backend did not close the gap: making the environment richer changes how a curious agent explores, not whether it behaves like a bot.

### 4.11.2 What the LLM-backed honeypot changed

Qwen3-32B reduced the divergence only for the smallest attacker, Gemma-3-4B. Richer shell output may give a weak attacker more to react to, but we did not test this. Even the closest cell (JSD 0.741) remains far from real traffic, and the backend increased credential hunting for every attacker, which pushes the synthetic data further towards the one label (credential access) that real traffic never has. LLM shells are known to invent inconsistent state (Ji et al., 2023; Sladić et al., 2023), so an agent attacking one is partly reacting to the other model's imagination.

### 4.11.3 What this means for practitioners

Three practical messages follow. First, do not assume that agent sessions are realistic training data; measure the gap with label-free tests before using them. Second, if synthetic data is used, design the personas to match the population you expect to defend against (droppers, miners, credential stuffers), not a generic explorer. Third, filter chat-format leakage and record raw replies, or the data will contain the model's thoughts instead of commands.

## 4.12 Threats to Validity

Table: Threats to validity and how they were handled. {#tab:threats widths=4,6,6}

| Threat | Description | Mitigation and remaining risk |
|---|---|---|
| Label quality | Labels were first produced by LLMs from one provider, which may share biases | Two different models, blind and independent; adjudication; author cross-verification; sensitivity run. Remaining: no independent human audit yet |
| Imperfect blindness | LLM-generated commands have a recognisable style, so an annotator could guess the source | Cannot be measured; our own verification was not blind either |
| Small synthetic sample | 20 sessions per cell | Bootstrap CIs; no claim of significant ordering between cells |
| One day, one honeynet | Real data from 15 November 2019 only; one campaign is 62% of interactive sessions | Per-template reporting; de-duplicated tests; more days in future work |
| Tagger errors | Tactic regexes and keyword shares were written by us and can mislabel (for example any path containing `passwd`) | Only large differences are interpreted; tagger never used as ground truth |
| Confounded persona | One prompt for all sessions; persona and model effects are not separated | Conclusions limited to this persona |
| Glued commands | Some replies concatenated commands without separators | Cannot be repaired by leak stripping; small effect |
| One classifier family | C2ST and transfer use simple linear and tree models | Perfect separability shows the corpora are separable, not that no other representation could bridge them |
| Normaliser quirk | URL mask can swallow an adjacent `;` | Affects segment splitting of a few commands in both corpora equally |

## 4.13 Testing, Characterisation and Data Validation

We validated the system at every stage ([@fig:validation]). [@tab:tests] lists the main checks, how they were run and what they showed.

![Validation checks used throughout the project.](images/d20_validation_checks.png){#fig:validation landscape}

Table: Testing and validation checks. {#tab:tests widths=4,6,6}

| Check | How | Result |
|---|---|---|
| Honeypot reachable | `check.py` and `probe_banner()` read the SSH banner | Banner `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5` returned |
| Model endpoints | `probe.py` sent a test prompt to each candidate model | Working models selected for the study |
| Reply boundaries | `validate_logs.py` scans logs for leaked markers and repeated prompts | Used to reject an earlier marker-based design |
| Recovery | Frozen-honeypot events logged in `infra_events.log` | Recovery attempts recorded with timestamps (for example during the DeepSeek static batch) |
| Parser correctness | Session count and field checks after parsing | 76,785 sessions; 1,672 interactive; matches the dataset's structure |
| Normaliser | Worked examples run through the real code ([@fig:normalisation]) | Masks and splits behave as designed; one URL quirk documented |
| Leakage | GroupKFold by template; Q3-dedup | No template in both train and test |
| Label reliability | Cohen's κ; disagreement file; adjudication | κ = 0.898; 12 adjudicated |
| Sensitivity | dota relabel run; rule-label plumbing run | Conclusions unchanged |
| Reproducibility | Fixed seed 42; scripts regenerate `results/` | Same numbers on rerun |
| Report numbers | Every number traced to `results/` or `report/data/` | Checked while writing |

### 4.13.1 Software testing strategy

Testing followed the usual four levels ([@tab:test-levels]). Because this is research software, the most important tests are not about whether a function runs but about whether a number can be trusted, so several tests compare an output with an independent count or a hand-worked example.

Table: Testing levels. {#tab:test-levels widths=3,6,7}

| Level | What was tested | How |
|---|---|---|
| Unit | Normalisation, segment splitting, verbs, tactic tags, macro-F1 over present classes | Worked examples run through the real functions ([@fig:normalisation]) |
| Integration | Raw file → parser → normalised sessions → analysis scripts | Session and template counts compared across stages |
| System | The full pipeline from logs and raw data to `results/` | Every script run end to end; outputs checked against each other |
| Acceptance | Every number in the paper and this report | Traced to a file in `results/` or `report/data/`; supervisor review |

### 4.13.2 Test cases

Table: Test cases with expected and observed results. {#tab:testcases widths=2,6,4,4,2}

| ID | Test | Expected | Observed | Result |
|---|---|---|---|---|
| TC-01 | Parse the CyberLab file | All sessions read | 76,785 sessions; 1,672 with commands | Pass |
| TC-02 | Run the native Cowrie parser on the CyberLab file | Shows the format mismatch | Zero sessions, no error | Pass (pitfall confirmed) |
| TC-03 | Normalise `echo "root:…"\|chpasswd\|bash` | Password masked | `echo <str>\|chpasswd\|bash` | Pass |
| TC-04 | Normalise `/bin/busybox QWERT` | Random tag masked | `/bin/busybox <tag>` | Pass |
| TC-05 | Split `cat /proc/cpuinfo \| grep name \| wc -l` | Three segments | Verbs `cat`, `grep`, `wc` | Pass |
| TC-06 | Detect chat-format leakage | Leaks found only for GPT-OSS-120B | 11 static + 7 dynamic sessions | Pass |
| TC-07 | Group real sessions into templates | Far fewer templates than sessions | 22 templates | Pass |
| TC-08 | Grouped folds keep templates apart | No template in train and test | Holds by construction (GroupKFold) | Pass |
| TC-09 | Agreement and final labels | κ computed on all items; every session labelled | κ = 0.898 on 184 items; 1,672 + 120 labelled | Pass |
| TC-10 | Honeypot freeze is noticed | Event written to the infrastructure log | Recovery attempts logged on 27 September 2026 | Pass |
| TC-11 | Report numbers match results | No number without a source file | Checked while writing | Pass |
| TC-12 | Report build | All references cited and linked; no broken fields | 124 of 124 references linked; no field errors | Pass |

## 4.14 Report Preparation, Project Management and Communication

The project was managed as a small research engineering effort. Work was split into the seven work packages of Chapter 1 and tracked in a shared task list (`PENDING.md`) with a done/next/future structure. The repository was the single source of truth: data generation, analysis and paper tables all ran from scripts, and generated files were never edited by hand. Results were written to `results/` as both Markdown (for reading) and JSON (for other scripts), which made it easy to check every number in the paper and in this report.

Communication followed three rules: agree on definitions before measuring (for example, the rubric was written before labelling began); report negative results as clearly as positive ones; and keep a written record of every design change and its reason, such as the move from marker-based to idle-timeout reading. The paper was first written in IEEE format and then converted, without changing its text, to Springer's LNCS/LNNS format for submission to the International Conference on Intelligent Communication, Control and Devices (ICICCD 2026). This report and the project documentation were written from Markdown sources and built into Word documents by script, so that figures, tables and numbers stay consistent across all outputs.
