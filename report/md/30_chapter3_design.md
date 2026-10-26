# 3 Design Flow and Process

This chapter explains how we went from the problem in Chapter 2 to a working research system. We first generated several concepts, then wrote down the specifications a good solution must meet, listed the constraints we had to respect, compared three alternative designs and chose one. The second half of the chapter is the implementation plan: block diagrams, flowcharts, algorithms and the exact settings used in every step.

## 3.1 Concept Generation

We began with one question: *how can a defender get enough labelled attack sessions?* Brainstorming produced six concepts, shown in [@fig:concepts] and compared in [@tab:concepts].

![Concept generation: six ways to obtain labelled attack sessions.](images/d16_concept_generation.png){#fig:concepts landscape}

Table: Concepts considered and their trade-offs. {#tab:concepts widths=4,6,6}

| Concept | Advantages | Disadvantages |
|---|---|---|
| C1 Collect more real data with our own internet-facing honeypots | Most realistic data | Months of collection; legal and operational risk; still repetitive (Barron and Nikiforakis, 2017) |
| C2 Scripted synthetic generator with fixed attack "archetypes" | Free labels (the script knows its archetype); fast | Data reflects only what we wrote; nothing new is learned |
| C3 Generative models (for example GANs) trained on traffic | Can produce many variations (Ring et al., 2019) | Needs a large real training set, which is exactly what is missing |
| C4 LLM agent attacking a static Cowrie honeypot | Cheap, unlimited, fully logged, contained | Unknown realism; agent may behave like a CTF player, not a bot |
| C5 LLM agent attacking an LLM-backed Cowrie honeypot | Same as C4, with a richer environment that answers any command | Hallucinated shell state; slower; extra cost (Sladić et al., 2023) |
| C6 Replay or mutate real sessions | Stays close to real behaviour | Mutations are hard to label; may only copy the same few templates |

The concepts that best match the stated goal are C4 and C5: they are the "LLM red-team" idea in its two natural forms. They need a source of real data to compare against; rather than waiting months for C1, we used a public real dataset (Sedlar et al., 2020). C2 and C3 were rejected for the reasons in the table, and C6 was kept for future work.

## 3.2 Evaluation and Selection of Specifications and Features

### 3.2.1 Functional requirements

Table: Functional requirements of the research system. {#tab:freq widths=2,9,5}

| ID | Requirement | Implemented by |
|---|---|---|
| F1 | Drive an interactive SSH shell with an LLM, one command per turn | `better_ai_attacker.py` |
| F2 | Support several LLM providers through one interface | `call_llm()` dispatcher |
| F3 | Run the same attacker against a static and an LLM-backed honeypot | Cowrie `backend = shell` / `backend = llm` |
| F4 | Log every turn: command, output, timestamp, latency, and the session outcome | Per-session JSON log |
| F5 | Detect and survive honeypot freezes without losing a whole batch | Banner probe, stall detection, retries |
| F6 | Parse the CyberLab export into per-session records | `parse_cyberlab.py` |
| F7 | Normalise commands so that the same script from different IPs becomes one template | `session_features.py` |
| F8 | Compare corpora without labels | `domain_shift.py` |
| F9 | Produce blind annotation sheets and measure agreement | `make_annotation_sheet.py`, `agreement.py` |
| F10 | Run the four-quadrant transfer experiment with baselines | `train_eval_classifier.py` |
| F11 | Regenerate every table and figure from scripts | `generate_paper_tables.py`, `make_figures.py` |

### 3.2.2 Non-functional requirements

Table: Non-functional requirements. {#tab:nfreq widths=3,8,5}

| Quality | Requirement | How we met it |
|---|---|---|
| Validity | No circular labels; no leakage of templates between train and test | Dual-LLM labels; GroupKFold by template; de-duplicated test |
| Reproducibility | Same inputs give the same numbers | Fixed seeds (42); scripts write all results to files |
| Containment | The attacker can reach only our honeypot | Single configured target; no scanning code |
| Privacy | No re-identification of real sources | Hashed IPs only; no enrichment |
| Robustness | A frozen honeypot must not corrupt or kill a batch | Idle-timeout reads, stall detection, retries, infra log |
| Scalability | The 600 MB real file must not need to fit in memory | Line-by-line streaming parser |
| Transparency | Every reported number traceable to a file | `results/` folder; this report cites it |
| Cost | Stay within a student budget | Small open-weight models via a pay-per-use endpoint; 20 sessions per cell |

### 3.2.3 Weighted decision matrix

To compare the concepts in a structured way we scored each one from 1 (poor) to 5 (excellent) on five criteria and weighted the criteria by importance. The scores are our own engineering judgement, made before the experiments, and are shown so that the reasoning is visible.

Table: Weighted decision matrix for the six concepts (higher is better). {#tab:decision widths=5,2,2,2,2,2,2,2}

| Criterion (weight) | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| Answers the research question (0.30) | 2 | 1 | 2 | 5 | 5 | 3 |
| Feasible in the project time (0.25) | 1 | 5 | 2 | 4 | 4 | 3 |
| Cost (0.15) | 2 | 5 | 3 | 4 | 3 | 4 |
| Safety and ethics (0.15) | 2 | 5 | 5 | 5 | 5 | 4 |
| Novelty (0.15) | 2 | 1 | 2 | 4 | 5 | 2 |
| **Weighted score** | **1.75** | **3.10** | **2.60** | **4.45** | **4.45** | **3.15** |

C4 and C5 tie at the top, which is why the final design uses both as two experimental conditions rather than choosing one.

## 3.3 Design Constraints

The format of this report asks us to consider a broad set of constraints. [@tab:constraints] lists each one and the design decision it forced.

Table: Design constraints and how the design responds to them. {#tab:constraints widths=3,6,7}

| Constraint | What it means here | Design response |
|---|---|---|
| Regulations | IT Act 2000, DPDP Act 2023, CERT-In directions (Government of India, 2000; 2023; CERT-In, 2022); dataset licence CC BY 4.0 | Attack only our own system; use only the public, hashed dataset; credit the dataset authors |
| Economic | API calls cost money; no budget for paid annotators | Small and mid-size models through one pay-per-use endpoint; 120 sessions; LLM annotation with author verification instead of paid experts |
| Environmental | LLM inference uses energy | Short sessions (turn and time limits); no model training; small classifiers on a laptop |
| Health | Long hours reading malicious command logs | Automation of labelling; scripts instead of manual counting |
| Manufacturability (deployability) | Others must be able to rebuild the system | Docker Compose file, pinned requirements, one config file for Cowrie |
| Safety | An attacking agent must not escape the testbed | No scanning or target discovery; target host is a fixed setting; honeypot holds no real data |
| Professional | ACM Code of Ethics (ACM, 2018); honest reporting | Report negative results; label LLM annotations as such; keep failed sessions in the data |
| Ethical | Menlo Report principles (Dittrich and Kenneally, 2012) | No deception of real people; no re-identification; no release of new attack capability |
| Social and political | Public concern about offensive AI (Weidinger et al., 2021) | Study footprints, not attack success; publish defensive findings |

Three constraints shaped the design most. **Safety** ruled out any design in which the agent could choose its own targets, so the harness connects to exactly one configured host and has no scanning code. **Economics** ruled out paid human annotation at the scale we needed, which led to the blind dual-LLM protocol with author verification. **Professional honesty** led us to keep every failed session (connection lost, LLM error, refusal) in the data, because failure rates are themselves a finding.

## 3.4 Analysis and Feature Finalisation Subject to Constraints

[@tab:features] shows which candidate features made it into the final system, and why the others were dropped.

Table: Feature finalisation. {#tab:features widths=5,2,9}

| Candidate feature | Kept? | Reason |
|---|---|---|
| One fixed "explore the system" persona for all agents | Yes | Isolates model and backend effects; persona diversity is future work |
| Several attacker models of different size and vendor | Yes | Shows whether a finding is one model's quirk |
| Static and LLM-backed honeypot conditions | Yes | Directly tests RQ4 |
| Output-marker injection to detect end of reply | No | The LLM backend parsed the marker as part of the command and leaked it |
| Idle-timeout reading (stop after 1.5 s of silence) | Yes | Works for both fast static and slow LLM replies |
| Automatic honeypot restart over admin SSH | Optional | Used only when an admin connection is configured; otherwise wait for a watchdog |
| Keyword-rule labels as ground truth | No | Circular with the features (Design A below) |
| Blind dual-LLM labels with adjudication | Yes | Feasible, measurable agreement, no keyword circularity |
| Response text as a classifier feature | No | Real Cowrie logs do not record command output, so it is not comparable |
| Random train/test splits | No | Would put copies of one bot script on both sides |
| Template-grouped cross-validation | Yes | Prevents leakage of repeated scripts |

## 3.5 Design Flow: Alternative Designs

We worked through three complete designs, shown in [@fig:designs].

![Three alternative designs. Design A was our first prototype; Design B is the final design; Design C is the ideal but unaffordable option.](images/d11_alternative_designs.png){#fig:designs landscape}

**Design A (keyword-rule labels).** Our first prototype labelled every session with simple rules: if a command contains `wget` or `curl`, the session is a *download*; if it touches `/etc/shadow`, it is *credential access*; and so on. A TF-IDF random forest was then trained to predict these labels. The scores looked good, but the design is circular: the TF-IDF features contain exactly the keywords that defined the labels, so the classifier only rediscovers the rules. Worse, the rules mislabel real behaviour. Mirai-style bots run a bare `tftp; wget` with no argument just to check whether the tools exist; a keyword rule calls that a download, while a human reader sees reconnaissance. We kept Design A only as a *plumbing check* that the code runs end to end, and we label its numbers as such everywhere.

**Design B (label-free tests plus blind dual-LLM labels).** The final design answers the realism question twice. First, without any labels, by measuring how different the command distributions are and whether a classifier can tell the corpora apart. Second, with intent labels that do not come from keywords: two LLM annotators label every distinct session blind to its source, an adjudicator resolves disagreements and the authors cross-verify the result. The transfer experiment then uses template-grouped folds, a de-duplicated test set, majority baselines and a sensitivity run on the most influential label.

**Design C (human experts).** The ideal design would replace the LLM annotators with two or three trained security analysts outside the author team. It gives the most defensible labels but needs recruitment, training and weeks of paid time, which the project could not afford. We designed Design B so that Design C can be added later without changing anything else: the blind sheets, rubric and agreement script already support human annotators.

## 3.6 Best Design Selection

[@tab:design-compare] compares the three designs on the criteria that matter most.

Table: Comparison of the alternative designs. {#tab:design-compare widths=4,4,4,4}

| Criterion | Design A | Design B | Design C |
|---|---|---|---|
| Labels independent of features | No (circular) | Yes | Yes |
| Answers realism without any labels | No | Yes | Yes |
| Agreement can be measured | No | Yes (κ) | Yes (κ) |
| Cost | Very low | Low | High |
| Time to complete | Days | About a week | Several weeks |
| Risk of shared bias in labels | Total | Moderate (one provider) | Low |
| Extensible to human labels later | No | Yes | Already human |
| **Decision** | Rejected (kept as plumbing check) | **Selected** | Future work |

Design B was selected because it is the only design that is both valid and feasible. Its main weakness, that both annotators come from one model provider, is handled in three ways: the two annotators are different models (Claude Sonnet 5.5 and Claude Opus 5.5) working independently, the authors cross-verify the final labels, and the most consequential label is tested in a sensitivity run. Chapter 4 reports the remaining limitation honestly.

## 3.7 Implementation Plan

### 3.7.1 Overall architecture and method

[@fig:architecture] shows the complete system in three blocks: synthetic data generation in our own testbed, data preparation for both corpora, and analysis. [@fig:method] shows the nine stages of the research method in order.

![System architecture: synthetic data generation, data preparation and analysis.](images/d01_system_architecture.png){#fig:architecture landscape}

![Research methodology in nine stages.](images/d14_methodology_overview.png){#fig:method landscape}

### 3.7.2 Testbed configuration

The honeypot is Cowrie (Oosterhof, 2015), configured as shown in [@tab:cowrie-config]. The same configuration file switches between the two experimental conditions by changing one line.

Table: Cowrie honeypot configuration (from cowrie_etc/cowrie.cfg; secrets omitted). {#tab:cowrie-config widths=5,5,6}

| Setting | Value | Purpose |
|---|---|---|
| hostname | svr04 | Name shown in the fake prompt |
| SSH listen endpoint | tcp:2222 | Port the attacker connects to |
| SSH version banner | SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5 | Looks like a common Ubuntu server |
| Telnet | disabled | Only SSH is studied in the testbed |
| Fake kernel | 5.4.0-42-generic, linux-x64-lsb | What `uname` reports |
| interactive_timeout | 300 s | Idle sessions are closed |
| tty logging | enabled | Full terminal transcripts kept |
| backend (Condition A) | shell | Cowrie's built-in emulated commands |
| backend (Condition B) | llm, model qwen.qwen3-32b, temperature 0.7, max_tokens 512 | An LLM writes every reply |

The three attacker models were reached through one OpenAI-compatible endpoint, which kept the request format identical across vendors. [@tab:models] summarises the models.

Table: Language models used in the project. {#tab:models widths=4,3,4,5}

| Model | Role | Vendor | Why it was included |
|---|---|---|---|
| DeepSeek-V3.2 (DeepSeek-AI, 2025) | Attacker | DeepSeek | Large open-weight frontier model |
| Gemma-3-4B (Gemma Team, 2025) | Attacker | Google | Very small model; tests whether size matters |
| GPT-OSS-120B (OpenAI, 2025) | Attacker | OpenAI | Large open-weight reasoning model |
| Qwen3-32B (Yang et al., 2025) | Honeypot backend | Alibaba (Qwen) | Mid-size model writing the fake shell output |
| Claude Sonnet 5.5 | Annotator A | Anthropic | Independent blind labels |
| Claude Opus 5.5 | Annotator B and adjudicator | Anthropic | Independent blind labels; separate instance for adjudication |

All attacker sessions used the same system prompt. In short, it told the model that this was an authorised research exercise against a deliberately fake, isolated system owned by the researchers, asked it to behave like an intruder who has just gained a shell (look around, look for valuable data or credentials, consider persistence), and required it to answer with exactly one raw shell command per turn, or the word `DONE` to finish.

### 3.7.3 Harness structure

The harness is a single Python program. [@fig:modules] shows its main parts: a command-line front end and a batch-config reader, a configuration data class, a session runner wrapped in a recovery layer, a thin SSH driver, an LLM dispatcher with retry and back-off, and small helpers for refusal detection and output cleaning. [@tab:harness-params] lists the settings that control a run.

![Module structure of the attacker harness.](images/d18_harness_modules.png){#fig:modules landscape}

Table: Main harness parameters (defaults in the code; batch files can override them). {#tab:harness-params widths=5,3,8}

| Parameter | Default | Meaning |
|---|---|---|
| max_turns | 25 | Maximum commands per session (some batches used 20) |
| max_session_seconds | 600 | Wall-clock limit per session |
| response_wait | 1.5 s | Silence that marks the end of a reply |
| max_response_wait | 20 s | Hard ceiling per command if the reply never ends |
| command_delay_range | 0.8–2.2 s | Random pause between commands |
| consecutive_timeout_limit | 2 | Empty replies at the ceiling in a row that mean "honeypot frozen" |
| max_session_retries | 3 | Retries for a session that failed because of infrastructure |
| recovery_max_wait | 90 s | How long to wait for the honeypot to come back |
| LLM retries | 3 (back-off 2 s, 4 s) | Retries for a failed API call |

### 3.7.4 The attacker session loop

Each session follows the flowchart in [@fig:session] and the steps in [@alg:session]. The loop is simple on purpose: the model sees the transcript so far, returns one command, the harness sends it and records what comes back. Six different exits are possible, and each one is saved as the session *status* ([@tab:statuses]).

![Attacker session loop: health check, connection, the decisions taken in every turn, and the status saved at each exit.](images/d03_attacker_session_flowchart.png){#fig:session}

```algorithm {#alg:session} Attacker session loop (run_session)
Input: configuration C (target, model, limits), system prompt P
Output: session log L with turns and a final status

1   L ← new log with session id, model, backend label, start time
2   try: open SSH shell to C.host:C.port; read banner B
3   on failure: L.status ← connection_failed; return L
4   context ← "You have just connected. Banner: " + B
5   messages ← [ ]; stalls ← 0
6   for turn = 0 … C.max_turns − 1 do
7       if elapsed time > C.max_session_seconds then L.status ← timed_out; break
8       append (user, context) to messages
9       reply ← call_llm(C.provider, C.model, P, messages)     ▷ up to 3 tries
10      on failure: L.status ← llm_error; break
11      append (assistant, reply) to messages
12      if reply = "DONE" then L.status ← completed; break
13      if looks_like_refusal(reply) then L.status ← attacker_refused; break
14      (output, latency) ← send_command(reply)                 ▷ Algorithm 3.2
15      on socket error: L.status ← connection_lost; break
16      append {turn, time, reply, output, latency} to L.turns
17      if output is empty and latency ≥ ceiling then stalls ← stalls + 1 else stalls ← 0
18      if stalls ≥ C.consecutive_timeout_limit then L.status ← honeypot_unresponsive; break
19      context ← "Command output: " + output
20      sleep a random time in C.command_delay_range
21  if no break happened then L.status ← max_turns_reached
22  close the connection; record end time and number of turns
23  return L
```

Table: Session outcomes recorded by the harness. {#tab:statuses widths=4,8,4}

| Status | Meaning | Counts as |
|---|---|---|
| completed | The model answered `DONE` | Normal data |
| max_turns_reached | The turn limit was hit | Normal data |
| timed_out | The wall-clock limit was hit | Normal data |
| attacker_refused | The reply looked like a refusal, not a command | Normal data (a model behaviour) |
| llm_error | The API call failed three times | Model/infrastructure failure, kept |
| connection_lost | The SSH socket died mid-command | Infrastructure failure, retried |
| honeypot_unresponsive | Two empty replies at the time ceiling in a row | Infrastructure failure, retried |
| connection_failed | The honeypot did not answer or recover | Infrastructure failure, retried |

The refusal check is a small heuristic. It flags a reply that contains phrases such as "I cannot" or "as an AI", or that contains no shell characters at all and reads like prose. Requiring the absence of shell characters was important: without it, a long `find` command with several `-name "*.txt"` patterns was mistaken for prose because file extensions contain full stops.

### 3.7.5 Reading the honeypot's reply

A fixed wait before reading the reply does not work for both backends: the static shell answers in well under a second, while the LLM backend can take several seconds. Reading too early captures half a reply and pushes the rest into the next turn, which corrupts every later prompt. We therefore read until the channel has been quiet for 1.5 seconds, with a hard ceiling ([@fig:drain], [@alg:drain]).

![Idle-timeout reading of the honeypot's reply.](images/d19_drain_algorithm.png){#fig:drain}

```algorithm {#alg:drain} Idle-timeout read (send_command and _drain)
Input: shell channel S, command c, idle time τ = 1.5 s, ceiling T = max_response_wait
Output: cleaned output text and latency

1   t0 ← now; write c + newline to S
2   buffer ← ""; last ← none
3   loop
4       while S has bytes waiting do
5           buffer ← buffer + read(S, 64 KB); last ← now
6       if last ≠ none and now − last ≥ τ then break          ▷ reply finished
7       if now − t0 ≥ T then break                             ▷ reply never finished
8       sleep 0.15 s
9   output ← remove ANSI escape codes from buffer; normalise line endings
10  return (output, now − t0)
```

### 3.7.6 Surviving a frozen honeypot

Cowrie runs on a single-threaded event loop. During testing, a recursive `find /` over the large fake file system blocked it for minutes: no new connections were accepted and existing ones hung. Without protection, one such command would waste the rest of a batch. The recovery layer in [@fig:recovery] and [@alg:recovery] checks the honeypot before every session, restarts it if an admin connection is configured (otherwise it waits for an external watchdog), and retries only sessions that failed because of infrastructure. Real outcomes such as a refusal are never retried, because that would hide genuine behaviour.

![Session retry and recovery logic.](images/d04_recovery_flowchart.png){#fig:recovery}

```algorithm {#alg:recovery} Session with recovery (run_session_with_recovery)
Input: configuration C, session index i
Output: one saved log per attempt; the final log for session i

1   attempt ← 0
2   loop
3       if not banner_answers(C.host, C.port) then
4           log "honeypot unresponsive" to infra_events.log
5           if admin access configured then restart Cowrie remotely
6           wait up to C.recovery_max_wait for the banner
7           if still silent then return log with status connection_failed
8       L ← run_session(C, i)                                   ▷ Algorithm 3.1
9       if L.status ∉ {connection_failed, honeypot_unresponsive, connection_lost} then return L
10      if attempt ≥ C.max_session_retries then return L
11      save L (failed attempt kept for honest reporting); attempt ← attempt + 1
12      wait 3 s
```

### 3.7.7 Parsing the real dataset

The CyberLab export is not Cowrie's native log format. Cowrie normally writes one JSON event per line; CyberLab instead stores one large JSON array in which each element maps a session ID to its list of events, and the command text sits in the `message` field as `CMD: <command>` rather than in an `input` field. A parser written for native Cowrie logs therefore reads zero sessions and raises no error, which is the most dangerous kind of failure. Our parser ([@fig:parser], [@alg:parser]) streams the 600 MB file one line at a time and merges sessions that appear more than once.

![Streaming parser for the CyberLab export.](images/d05_cyberlab_parser_flowchart.png){#fig:parser}

```algorithm {#alg:parser} Streaming CyberLab parser (parse_cyberlab.py)
Input: CyberLab daily file F
Output: one normalised JSON line per session

1   sessions ← empty map from session id to record
2   for each line ℓ in F do                                    ▷ never load F whole
3       strip "[", "]" and a trailing "," from ℓ
4       try obj ← parse_json(ℓ) except: continue
5       for each (sid, events) in obj do
6           s ← sessions[sid] or a new empty record
7           for each event e in events sorted by timestamp do
8               update start/end time, hashed source id, country
9               switch e.eventid:
10                  session.connect → s.protocol ← e.protocol
11                  login.success / login.failed → append (username, password, success)
12                  command.input → append text of e.message without the "CMD: " prefix
13                  file_download / file_upload → append (url, hash, file)
14                  client.version → s.client_version; session.closed → s.duration
15  for each record s do add counts and rule-based findings; write s as one JSON line
```

### 3.7.8 Normalisation and behaviour templates

The same bot script, run from different machines, produces commands that differ only in IP addresses, URLs and random passwords. To compare *behaviours* rather than *instances*, every command is normalised ([@fig:normalisation], [@alg:normalise], [@tab:masks]). Two sessions belong to the same **behaviour template** when their sequences of normalised commands are identical.

![Command normalisation in six steps, with three worked examples produced by the project's own code.](images/d06_normalization_pipeline.png){#fig:normalisation landscape}

Table: Values masked during normalisation (session_features.py). {#tab:masks widths=4,6,6}

| Pattern | Replaced by | Example |
|---|---|---|
| URL (http, https, ftp, tftp) | `<url>` | `http://203.0.113.7/x.sh` → `<url>` |
| IPv4 address with optional port | `<ip>` | `198.51.100.4:8080` → `<ip>` |
| Quoted string | `<str>` | `"root:Xk29qPa7mz"` → `<str>` |
| Hex string of 16+ characters | `<hex>` | file hashes |
| Random alphanumeric token (8+ chars with letters and digits) | `<tok>` | random file names |
| Bare number | `<n>` | `head -n 10` → `head -n <n>` |
| Random Mirai busybox tag (not a real applet name) | `busybox <tag>` | `/bin/busybox QWERT` → `/bin/busybox <tag>` |
| Leaked chat-format text after `<\|` | removed | GPT-OSS control tokens and reasoning |

```algorithm {#alg:normalise} Normalisation, segments, verbs and template key
Input: a session with commands c1 … cn
Output: normalised commands, verbs, tactic set, template key

1   for each command c do
2       c ← text before the first "<|" (drops leaked chat tokens); lower-case; trim
3       replace URLs, IPs, quoted strings, long hex, random tokens and numbers by placeholders
4       replace "busybox X" by "busybox <tag>" unless X is a known applet (wget, cat, echo, …)
5       collapse repeated spaces
6       segments(c) ← split c on ";", "|", "&&", "||", newline, "$(" and backtick
7       verb(segment) ← first word that is not a VAR=value prefix, without its path
8       tactics(c) ← every tactic whose regular expression matches some segment
9   template key ← tuple of all normalised commands, in order
10  return normalised commands, verbs, tactic set, template key
```

One limitation of the URL mask is worth recording. The URL pattern stops only at whitespace, so in a command such as `wget http://…/x.sh; chmod 777 x.sh` the semicolon directly after the URL is swallowed by the mask and the two parts are treated as one segment. This affects only the splitting of a few chained download commands, not the template grouping, and it applies equally to both corpora.

### 3.7.9 Tactic tagging

For the label-free comparison we also describe each session by the ATT&CK-style tactics it touches (Strom et al., 2018). A command segment can match zero or more of nine regular-expression categories ([@tab:tactics]). This tagger is *descriptive only*: it is never used as a training label for reported results.

Table: The nine tactic categories and example patterns. {#tab:tactics widths=4,7,5}

| Tactic | Example patterns (simplified) | Typical command |
|---|---|---|
| Discovery | `uname`, `whoami`, `id`, `ps`, `ls`, `/proc/cpuinfo`, `crontab -l` | `cat /proc/cpuinfo \| grep name` |
| Credential access | `/etc/shadow`, `.ssh`, `id_rsa`, `.bash_history`, "password", "secret" | `cat /etc/shadow` |
| Account manipulation | `chpasswd`, `passwd`, `useradd`, `authorized_keys` | `echo <str> \| chpasswd` |
| Persistence | `crontab` (not `-l`), `/etc/cron`, `systemctl enable`, `rc.local` | adding a cron entry |
| Privilege escalation | `sudo`, `su`, `-perm -4000`, `getcap`, `/etc/sudoers` | `sudo -l` |
| Defence evasion | `history -c`, `unset HISTFILE`, deleting logs, `chattr`, `pkill` | `history -c` |
| Ingress tool transfer | `wget`/`curl`/`tftp` **with** an argument | `wget <url>` |
| Execution | `chmod +x`, `./file`, `sh`, `bash`, `base64 -d`, `nohup` | `./x.sh` |
| Resource hijacking | `xmrig`, `minerd`, `stratum`, `miner`, `dota` | starting a miner |

### 3.7.10 Label-free measures

[@fig:labelfree] shows the five label-free measures. The most important are the verb-distribution divergence and the classifier two-sample test.

![Label-free domain-shift analysis.](images/d07_label_free_analysis.png){#fig:labelfree landscape}

**Verb distributions.** The verb of a segment is its first word (`ls`, `cat`, `wget`). Counting verbs over all sessions gives a probability distribution for each corpus. We compare the synthetic distribution $P$ and the real distribution $Q$ with the Jensen-Shannon divergence in base 2 (Lin, 1991), built from the Shannon entropy and the Kullback-Leibler divergence (Kullback and Leibler, 1951):

$$ H(P)=−∑_i P(i) log_2 P(i) $$ {#eq:entropy}

$$ D_KL (P∥Q)=∑_i P(i) log_2 (P(i)/Q(i)) $$ {#eq:kl}

$$ JSD(P∥Q)=1/2 D_KL (P∥M)+1/2 D_KL (Q∥M),  M=1/2 (P+Q) $$ {#eq:jsd}

JSD is 0 when the distributions are identical and 1 when they share no verb at all. Its square root is a metric (Endres and Schindelin, 2003). We also report the Jaccard index of the two verb vocabularies $V_S$ and $V_R$ (Jaccard, 1912), and the coverage, the share of real verb occurrences whose verb also appears in the synthetic vocabulary:

$$ J(V_S,V_R)=|V_S∩V_R|/|V_S∪V_R| $$ {#eq:jaccard}

$$ Cov=(∑_(v∈V_S∩V_R) n_R (v))/(∑_(v∈V_R) n_R (v)) $$ {#eq:coverage}

**Uncertainty.** A single JSD value does not say how stable it is. We resample the synthetic sessions with replacement $B = 500$ times, recompute JSD each time and take the 2.5th and 97.5th percentiles as a 95% confidence interval (Efron and Tibshirani, 1993; [@alg:bootstrap]):

$$ CI_0.95=[θ̂_((⌊0.025B⌋)), θ̂_((⌊0.975B⌋))] $$ {#eq:ci}

```algorithm {#alg:bootstrap} Bootstrap confidence interval for JSD
Input: synthetic sessions S, real sessions R, B = 500, seed 42
Output: point estimate and 95% CI

1   θ ← JSD(verb counts of S, verb counts of R)
2   for b = 1 … B do
3       S* ← |S| sessions drawn from S with replacement
4       θ*_b ← JSD(verb counts of S*, verb counts of R)
5   sort θ*_1 … θ*_B
6   return θ, [θ*_(0.025B), θ*_(0.975B)]
```

**Classifier two-sample test.** If a simple classifier can tell synthetic sessions from real ones, the corpora differ in ways that a downstream model can exploit (Lopez-Paz and Oquab, 2017). Each session becomes a document of its normalised commands, weighted with TF-IDF (Spärck Jones, 1972; Salton and Buckley, 1988):

$$ w(t,d)=tf(t,d)×(ln((1+N)/(1+df(t)))+1) $$ {#eq:tfidf}

A balanced logistic regression is trained to separate the corpora, and its ranking quality is measured by the area under the ROC curve (Hanley and McNeil, 1982; Fawcett, 2006), which equals the probability that a random synthetic session scores higher than a random real one:

$$ AUC=1/(n_+ n_−) ∑_(i∈+) ∑_(j∈−) 1[s_i>s_j] $$ {#eq:auc}

An AUC of 0.5 means the corpora cannot be told apart; 1.0 means perfect separation. We use 5 repeats of 5-fold stratified cross-validation (Kohavi, 1995) and compare synthetic sessions with the de-duplicated real templates, so that the 1,038 copies of one script do not dominate. To make sure that file paths and arguments are not doing all the work, we repeat the test with verbs only ([@alg:c2st]).

```algorithm {#alg:c2st} Classifier two-sample test (C2ST)
Input: synthetic sessions S (label 1), real templates R (label 0), text function g
Output: mean and standard deviation of AUC

1   docs ← [g(s) for s in S ∪ R]; y ← [1]·|S| + [0]·|R|
2   for each of the 5 × 5 stratified folds (train, test) do
3       fit a TF-IDF vectoriser on docs[train] only            ▷ no test information leaks
4       fit logistic regression (balanced weights) on the training vectors
5       record AUC of predicted probabilities on docs[test]
6   return mean and standard deviation of the 25 AUC values
```

### 3.7.11 Annotation protocol

The transfer experiment needs intent labels that do not come from keywords. [@fig:annotation] shows the protocol and [@tab:rubric] the label set.

![Blind dual-LLM annotation, adjudication, author verification and template broadcast.](images/d08_annotation_workflow.png){#fig:annotation}

Table: Annotation rubric: one primary intent per session (annotation/RUBRIC.md). {#tab:rubric widths=4,6,6}

| Label | Definition | Common confusion and rule |
|---|---|---|
| recon | Learning about the system; nothing changed | Reading `/etc/passwd` alone is recon, not credential access |
| credential_access | Harvesting or guessing credentials, keys or secrets | Searching for secret files counts |
| privilege_escalation | Trying to gain higher privileges | `sudo -l` alone is recon |
| persistence | Keeping access: cron, rc, SSH keys, new or changed accounts | Changing the root password is persistence |
| malware_drop | Downloading or running a payload | A download without execution still counts |
| resource_hijacking | Deploying or inspecting cryptominers; abusing compute | A miner fetched by `wget` is resource hijacking |
| defense_evasion | Hiding or disabling defences | Clean-up after a download follows the tie-break |
| other | Benign, unclear or noise | Use only if no intent above is evident |

When a session shows several behaviours, annotators pick the goal that progressed furthest, using a fixed tie-break order ([@fig:tiebreak]).

![The rubric's tie-break order, read from top to bottom.](images/d15_label_tiebreak.png){#fig:tiebreak}

The annotation set contained 184 items: every distinct real command sequence (64 sequences that fall into the 22 templates) and all 120 synthetic sessions. Items were shuffled with a fixed seed, the source was hidden, the synthetic agents' `DONE` token was removed (it would reveal the source) and very long sessions were shortened to their first 30 commands. Agreement between the two annotators is measured with Cohen's kappa (Cohen, 1960), where $p_o$ is the observed agreement and $p_e$ the agreement expected by chance from each annotator's label frequencies:

$$ κ=(p_o−p_e)/(1−p_e),  p_e=∑_k p_(A,k) p_(B,k) $$ {#eq:kappa}

```algorithm {#alg:annotation} Blind dual-LLM annotation and template broadcast
Input: real sessions R, synthetic sessions S, rubric, seed 42
Output: labels_final.csv with one label per session

1   items ← one representative per distinct real command sequence ∪ all of S
2   shuffle items (seed 42); give ids A001…; write a hidden key (id → source)
3   for each annotator a ∈ {A, B} independently do
4       label every item with one rubric label (source hidden, no access to the other's labels)
5   κ ← Cohen's kappa(A, B); write disagreements
6   for each item: if A = B then final ← A else final ← adjudicator's label (blind, uses rubric)
7   authors cross-verify the final labels (special check of the largest template)
8   for each real session r: label(r) ← final label of the item with r's template key
9   write (session id, label, source) for all real and synthetic sessions
```

### 3.7.12 Four-quadrant transfer experiment

The transfer design is shown in [@fig:quadrants]. Every session becomes a feature vector: TF-IDF weights of its normalised commands (up to 2,000 tokens) plus three numbers: the number of commands, the mean command length and the share of chained commands. The classifier is a random forest (Breiman, 2001) with the settings in [@tab:rf].

![The four quadrants of the transfer experiment, with the main results.](images/d09_transfer_quadrants.png){#fig:quadrants}

Table: Classifier and evaluation settings. {#tab:rf widths=5,5,6}

| Setting | Value | Reason |
|---|---|---|
| Features | TF-IDF (max 2,000 tokens) + 3 numeric | Simple, transparent, comparable across corpora |
| Classifier | Random forest, 300 trees | Robust on small, mixed feature sets |
| Class weights | balanced | Rare classes are not ignored (He and Garcia, 2009) |
| Seed | 42 | Reproducible |
| Q1 folds | Stratified 2-fold within synthetic | Two classes have six or fewer examples |
| Q2/Q4 folds | GroupKFold(5) by template | No template appears in both train and test |
| Q3 | Train on all synthetic, test on all real | Zero-shot transfer |
| Q3-dedup | Test on one session per real template | Removes the weight of repeated scripts |
| Baseline | Always predict the training majority class | Shows what "no learning" scores |

Performance is measured with per-class precision $P_c$ and recall $R_c$, the per-class F1, macro-F1 over the classes **present in the test set** and accuracy (Sokolova and Lapalme, 2009):

$$ F1_c=(2 P_c R_c)/(P_c+R_c) $$ {#eq:f1}

$$ Macro‑F1=1/|C_test | ∑_(c∈C_test) F1_c $$ {#eq:macrof1}

$$ Acc=1/n ∑_(i=1)^n 1[ŷ_i=y_i] $$ {#eq:acc}

Averaging only over classes present in the test set matters. Otherwise a class that the model predicts but that never occurs in the test set adds a zero to the average and makes the score look worse than it really is.

```algorithm {#alg:transfer} Four-quadrant transfer evaluation
Input: synthetic sessions S with labels yS, real sessions R with labels yR, template id g(r)
Output: macro-F1, accuracy and baselines for Q1, Q2, Q3, Q3-dedup, Q4

1   Q1: for each stratified fold (train, test) of S: fit on train, predict test; pool predictions
2   for each GroupKFold(5) fold (train, test) of R grouped by g do
3       Q2: fit on R[train]; predict R[test]
4       Q4: fit on R[train] ∪ S; predict R[test]                ▷ same folds as Q2
5       baseline: predict the majority label of yR[train]
6   Q3: fit on all of S; predict all of R
7   Q3-dedup: keep the Q3 predictions for the first session of each real template
8   for each quadrant: macro-F1 over classes present in its test labels; accuracy
```

```algorithm {#alg:macro} Macro-F1 over classes present in the test set
Input: true labels y, predicted labels ŷ
Output: macro-F1

1   C ← set of distinct values in y                            ▷ not in ŷ
2   for each class c in C do
3       P_c ← precision of c; R_c ← recall of c (0 if undefined)
4       F1_c ← 2·P_c·R_c / (P_c + R_c), or 0 if both are 0
5   return the mean of F1_c over c ∈ C
```

### 3.7.13 Data model

[@fig:datamodel] shows how the main records relate: a synthetic log contains turns and is converted into a normalised session; real sessions map many-to-one onto templates; each template and each synthetic session becomes one annotation item; and final labels are broadcast back to sessions.

![Data model of the project's main records.](images/d13_data_model.png){#fig:datamodel landscape}

### 3.7.14 Risk register

Table: Risks identified during design and how they were handled. {#tab:risks widths=5,2,2,7}

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Honeypot freezes on heavy commands | High | High | Stall detection, retries, infra log, optional remote restart |
| Slow LLM backend truncates replies | High | High | Idle-timeout reading instead of fixed waits |
| Attacker model refuses the task | Medium | Medium | Research framing in the prompt; refusals recorded as an outcome |
| Parser silently reads nothing | Medium | High | Dedicated CyberLab parser; cross-check of session counts |
| Template leakage inflates scores | High | High | GroupKFold by template; de-duplicated test |
| Circular labels | High | High | Dual-LLM labels; rule labels only as plumbing check |
| Shared bias of LLM annotators | Medium | Medium | Two different models, blind; adjudication; author check; sensitivity run |
| Chat tokens leak into commands | Medium | Medium | Detection and stripping of `<\|…` text before analysis |
| API cost overrun | Low | Medium | Small cells (20 sessions), turn and time limits |
| Attacker escapes the testbed | Low | Very high | One fixed target; no scanning code; isolated honeypot with no real data |

## 3.8 Software Design and Engineering

The research questions are answered by software, so the quality of the software decides the quality of the answers. This section describes the system the way a software engineer would: how it was developed, who uses it and for what, how data moves through it, how it is split into components and modules, how the parts talk to each other, how a session moves between states, how expensive each algorithm is, and how errors, configuration and security are handled.

### 3.8.1 Development life cycle

We followed an iterative and incremental life cycle ([@fig:sdlc]). Each iteration planned a small change, built it, ran a batch or an analysis, looked at the output and then refined the design. This suited a research project in which the right design was not known at the start: several decisions in this report, such as reading replies with an idle timeout or grouping folds by template, came directly from a failed earlier iteration.

![Iterative development life cycle, with the main design changes made in this project.](images/d28_sdlc.png){#fig:sdlc}

### 3.8.2 Use cases

[@fig:usecase] shows who uses the system and for what. The researcher drives almost every step; the LLM annotators take part only in labelling; and readers or reviewers use the published results to check or reproduce the work.

![Use case diagram of the research pipeline.](images/d21_use_case.png){#fig:usecase}

Table: Use case summary. {#tab:usecases widths=2,5,3,6}

| ID | Use case | Actor | Result |
|---|---|---|---|
| UC1 | Configure the honeypot | Researcher | Static or LLM backend selected in one configuration file |
| UC2 | Run a synthetic batch | Researcher | 20 session logs per cell, with outcomes |
| UC3 | Parse and normalise real data | Researcher | `real_organic.jsonl` and behaviour templates |
| UC4 | Run the label-free comparison | Researcher | `results/domain_shift.md` and `.json` |
| UC5 | Build blind annotation sheets | Researcher | Shuffled items and a hidden key |
| UC6 | Label and adjudicate items | LLM annotators | Two independent label sets and adjudicated disagreements |
| UC7 | Compute agreement and final labels | Researcher | κ and `labels_final.csv` |
| UC8 | Run the transfer experiment | Researcher | `results/table3_transfer.md` and `.json` |
| UC9 | Generate tables, figures and the report | Researcher | Paper tables, figures and this document |
| UC10 | Read and reproduce results | Reader / reviewer | Independent check of every reported number |

### 3.8.3 Data-flow diagrams

The context diagram ([@fig:dfd0]) treats the whole pipeline as one process and shows what crosses its boundary. The level-1 diagram ([@fig:dfd1]) opens that process into eight sub-processes and four data stores. Every arrow carries a named file or message, which is why the stores in the diagram match the folders of the repository.

![Data-flow diagram, level 0 (context diagram).](images/d22_dfd_level0.png){#fig:dfd0}

![Data-flow diagram, level 1.](images/d23_dfd_level1.png){#fig:dfd1}

Table: Data dictionary of the main stores and flows. {#tab:datadict widths=4,4,4,4}

| Store or flow | Format | Written by | Read by |
|---|---|---|---|
| D1 `logs/` | One JSON file per session | Process 1.0 | Process 3.0 |
| D2 `normalized/` | JSON Lines, one session per line | Processes 2.0 and 3.0 | Processes 4.0 and 5.0 |
| D3 `annotation/` | CSV sheets, key and final labels | Process 6.0 | Process 7.0 |
| D4 `results/` | Markdown and JSON | Processes 5.0 and 7.0 | Process 8.0 |
| Raw CyberLab file | One JSON array (about 600 MB) | External (Zenodo) | Process 2.0 |
| Report and paper | Word, PDF, LaTeX | Process 8.0 | Readers |

### 3.8.4 Components and technology stack

[@fig:components] groups the software into a testbed layer, an analysis layer, third-party libraries and outputs. One shared library, `session_features`, is imported by every analysis component, so the corpora are always normalised the same way. [@tab:stack] lists the technologies and why each was chosen.

![Component diagram.](images/d24_component.png){#fig:components}

Table: Technology stack. {#tab:stack widths=3,4,3,6}

| Layer | Technology | Version | Why it was chosen |
|---|---|---|---|
| Language | Python | 3.11 | Mature data and ML ecosystem; one language for every step |
| Honeypot | Cowrie in Docker | latest image | Standard SSH honeypot with structured logs and an LLM backend |
| Containers | Docker, Docker Compose | Compose file 3.8 | Same environment on every machine (Merkel, 2014) |
| SSH client | Paramiko | ≥ 3.4 | Pure-Python SSH with interactive channels |
| Model access | AWS Bedrock (OpenAI-compatible API), requests, boto3 | ≥ 2.31 / ≥ 1.34 | One request format for several model vendors |
| Machine learning | scikit-learn | ≥ 1.4 | TF-IDF, logistic regression, random forest, grouped CV, kappa (Pedregosa et al., 2011) |
| Numerics | NumPy, SciPy, pandas | ≥ 1.26 / ≥ 1.12 / ≥ 2.2 | Arrays, Jensen-Shannon distance, tables (Harris et al., 2020; Virtanen et al., 2020) |
| Charts and diagrams | Matplotlib; draw.io XML | 3.x | Reproducible figures; editable diagrams (Hunter, 2007) |
| Documents | LaTeX (Springer LNCS class); python-docx and Microsoft Word | – | Paper and this report built from source |
| Version control | Git and GitHub | – | History, collaboration, public release |

### 3.8.5 Class and module design

[@fig:classes] shows the main classes and modules. The analysis code is written as small, pure functions grouped by module: each function takes sessions or labels and returns numbers, which makes it easy to test and to reuse. [@tab:interfaces] lists the most important analysis functions.

![Class and module diagram.](images/d25_class_diagram.png){#fig:classes}

Table: Main analysis interfaces. {#tab:interfaces widths=5,5,6}

| Function (module) | Input | Output |
|---|---|---|
| `normalize_cmd` (session_features) | One command string | Lower-cased command with values masked |
| `segments` (session_features) | One command string | List of chained or piped sub-commands |
| `verb` (session_features) | One segment | Its first word, without path |
| `session_tactics` (session_features) | One session | Set of descriptive tactic names |
| `template_key` (session_features) | One session | Tuple of normalised commands |
| `corpus_stats` (domain_shift) | List of sessions | Templates, top-5 share, lengths, chaining |
| `jsd_with_ci` (domain_shift) | Two session lists, random generator | JSD and its 95% bootstrap interval |
| `c2st_auc` (domain_shift) | Two session lists, text function | Mean and standard deviation of AUC |
| `fit_predict` (train_eval_classifier) | Training sessions, test sessions, labels | Predicted labels |
| `row` (train_eval_classifier) | True, predicted and baseline labels | Macro-F1, accuracy and baselines |
| `kappa` (agreement) | Two label maps, item ids | Cohen's κ |

### 3.8.6 Interaction and state views

[@fig:sequence] shows, as a sequence diagram, the messages exchanged during one synthetic session between the command line, the harness, the model API, the honeypot and the log file. [@fig:states] shows the same session as a state machine: every path ends in exactly one of the outcome states listed in [@tab:statuses], which is what makes the outcome counts in Chapter 4 complete.

![Sequence diagram of one session.](images/d26_sequence.png){#fig:sequence}

![State machine of a session and its possible outcomes.](images/d27_state_machine.png){#fig:states}

### 3.8.7 Algorithmic complexity

[@tab:complexity] gives the cost of the main analysis steps. $N$ is the number of sessions, $L$ the length of a command, $E$ the number of events in the raw file, $V$ the verb vocabulary size, $B$ the number of bootstrap samples, $T$ the number of trees and $d$ the number of features.

Table: Time and memory cost of the main analysis steps. {#tab:complexity widths=5,4,3,4}

| Step | Time | Memory | Note |
|---|---|---|---|
| Streaming parse of the raw file | O(E + Σ eₛ log eₛ) | O(N) records | Events sorted per session; file never loaded whole |
| Normalising one command | O(L) | O(L) | A fixed list of regular expressions |
| Grouping sessions into templates | O(N · L) | O(N) | Hash map keyed by the template tuple |
| One JSD evaluation | O(V) | O(V) | Verb counts cached per session |
| Bootstrap confidence interval | O(B · (N + V)) | O(V) | B = 500 |
| Classifier two-sample test | 25 × (TF-IDF + logistic regression) | Sparse matrix | 5 × 5 cross-validation |
| Random forest training | ≈ O(T · n log n · √d) | O(T · nodes) | T = 300 |
| Cohen's κ | O(N + k²) | O(k²) | k = 8 labels |

### 3.8.8 Engineering practices

Table: Engineering practices used in the project. {#tab:practices widths=4,12}

| Practice | How it was applied |
|---|---|
| Coding style | PEP 8 naming, short functions, docstrings that explain *why* a step exists |
| Configuration | Run settings in a data class or JSON batch file; honeypot settings in one `cowrie.cfg` |
| Secrets | API keys only in environment variables; never written to logs or the repository |
| Reproducibility | Fixed seed 42 in every random step; results written to files by scripts |
| Data safety | The raw dataset is never loaded whole; hashed identifiers only |
| Error handling | Infrastructure failures recorded as a session status and in a separate event log; batches continue |
| Version control | Git history for code, results and documents; generated files rebuilt rather than edited |
| Documentation | Markdown sources for the report and documentation; editable draw.io sources for diagrams |


