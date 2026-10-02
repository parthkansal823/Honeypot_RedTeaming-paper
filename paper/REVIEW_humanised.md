# Review of the humanised paper (`paper/overleaf/main.tex`)

Checked against the verified version (`paper/main.tex`) and `results/*.md`. Line numbers refer to `paper/overleaf/main.tex`.
Still OK: all 25 citations resolve, every `\ref` has a label, braces/environments balance, `references.bib` unchanged, Table I/II numbers unchanged, **8 pages** once the two compile errors are fixed.

## 1. Compile / rendering errors — must fix

| # | Line | Problem | Fix |
|--:|:--|:--|:--|
| 1 | L40 | `ATT&CK` — unescaped `&` is a hard error; strict LaTeX stops here (Overleaf hides it) | `ATT\&CK` |
| 2 | L30 | `or 45%.` — `%` starts a comment: the abstract silently ends at "or 45" | `45\%` |
| 3 | L101 | `Sonnet\~5.5`, `Opus\~5.5` — `\~` is a tilde accent, prints "Sonnet5.5" | `Sonnet~5.5`, `Opus~5.5` |
| 4 | L236, L238, L253 | `\lbl\{resource hijacking\}` (7×) prints literal braces, not italic | `\lbl{resource hijacking}` etc. |
| 5 | L232, L273 + others | `chose\lbl{...}` → "chosemalware drop"; `\cmd{passwd}may` → "passwdmay"; missing space after periods: "blind.This", "commands.Each", "GPT-OSS-120B.Our", "level.So", "0.798.The", "wrote.They", "4.0,where" | add the missing spaces |
| 6 | L67 | `test. ~\cite{lopezpaz2017c2st}` — citation orphaned after the period | `test~\cite{lopezpaz2017c2st}.` |
| 7 | L250, L269, L291 | plain space before `\cite`; raw Unicode `–` / `—` | `~\cite`, `--`, rephrase without the dash |

## 2. Wrong facts / numbers — must fix

| # | Line | Wrong | Correct |
|--:|:--|:--|:--|
| 8 | L30 | "in **40 of its 40** sessions, or 45%" | **18 of its 40** sessions (45\%); and "into the shell", not "into itself" |
| 9 | L30 | "Many of the personas in our context were not applicable…" | there was only **one** persona: "In our setting, a single ``explore the system'' persona did not produce useful training data for real honeypot traffic." |
| 10 | L271 | "One campaign accounts for **96.2%** … top 5 templates account for **98.1%**" | largest campaign = 1,038 of 1,672 (62\%); **top five = 96.2\%**; 98.1\% is the execution-tactic share |
| 11 | L155 | "**GPT-OSS-170B**" | GPT-OSS-**120B** |
| 12 | L189 | "Only the intervals for Gemma-3-4B do not overlap with the rest" | only Gemma's *own* static and dynamic intervals are disjoint (its dynamic CI overlaps other cells) |
| 13 | L189 | "tactics … present in the data but not found in the model increased from 5 to 7" | Match counts tactics whose presence/absence **agrees** with real data: "rose from 5 to 7 of 9" |
| 14 | L265 | "this results in a near zero achievement value for Q3" | reversed cause: relabeling the dota template **leaves Q3 near zero** (0.021); "achievement value" is not a metric |
| 15 | L256 | "Credential Access is the very thing that you don't find in our labels" | it is the **synthetic majority** (87); it is absent only from the **real** labels |
| 16 | L230 | "All but a handful of synthetic sessions are credential access (87 of 120)" | 87/120 = 72.5\%: "mostly credential access (87 of 120)" |
| 17 | L40 | "only 1,672 of 76,785 sessions used one command" | "ran **even one** command" (at least one) |
| 18 | L180 | "there are no arguments or paths in the separation" | "the separation does not depend on paths or arguments" |
| 19 | L153 | "latency is the time until **we** stop outputting" | until the **honeypot's** output goes quiet; depends on the commands each attacker sent |
| 20 | L238 | "It only has one class: malware drop" | it is the only class the model **recognizes** (F1 0.818); the model labels 1,636 of 1,672 real sessions as credential access |
| 21 | L114 | "macro-F1 and accuracy averaged across folds"; "a rare class has a significant effect" | **pooled** over folds; "a rare class counts as much as a common one" |
| 22 | L96 | "over 5-fold cross validation"; "fails to outperform chance it turns out … very similar"; "to ensure that paths… don't affect" | **five repetitions** of 5-fold CV; "if it cannot beat chance, the corpora look alike"; "to **check**" |
| 23 | L277 | "three attacker models are used for each session" | each session has **one** attacker: "All sessions use one prompt, three attacker models and one backend model, so persona effects are not separated from model effects." |
| 24 | L172 | "The biggest real template is **only** 1,038 of 1,672" | "alone covers 1,038 of the 1,672 sessions" (62\% is dominance, not "only") |
| 25 | L282 | "anonymized to hashes"; "doesn't actually contain any data"; "default post-compromise commands" | "source IP addresses are replaced by hashes"; "holds no **real** data"; "**standard** post-compromise commands" |

## 3. Meaning changed / garbled sentences

| # | Line | Problem | Fix |
|--:|:--|:--|:--|
| 26 | L44 | research question reversed: "train a classifier for agent-generated sessions on real…, and if so, how?"; "difference between numbers" | "Does a classifier trained on agent-generated sessions work on real honeypot sessions, and if not, where do the two kinds of data differ?" / "the difference between the two corpora" |
| 27 | L101, L267 | "Everyone… the other persons", "him/her" — LLM annotators written as people (reads as human labels) | "Annotator~A was Claude Sonnet~5.5 and annotator~B was Claude Opus~5.5…"; "An annotator may guess the source and be swayed by it. We cannot measure how often this happened." |
| 28 | L250 | "Our agents weren't unsuccessful at their job, they're not successful at the job they were hired to do." (double negative, contradictory) | "Our agents did not fail at their task; they did a different one." |
| 29 | L253 | "F0.000 for the term(s)…", "If you try to add a real persistence…, that's the bot script to do" | "But recon and persistence, which both corpora contain, also score an F1 of 0.000. Synthetic persistence is an intruder writing a reverse-shell cron entry or appending an SSH key. Real persistence is a bot script that changes a password between fingerprinting steps." |
| 30 | L256 | "**Weaker** shell output could give the weak attacker more" | "**Richer** shell output may give a weak attacker more to react to; we have not tested this." |
| 31 | L259 | harness advice reversed; "Try to use dropper…" (imperative) | "log the raw reply **apart from** the executed command"; "Future work should try bot-like personas (dropper, cryptominer, credential stuffer)." |
| 32 | L287 | Conclusion: "scavenge for a credential and…" (subject missing); "LLM ensnared honeypot"; research question replaced | "The agents browse files and hunt for credentials, while most real sessions run one cryptominer dropper." / "LLM-backed honeypot" / "We asked whether LLM red-team agents produce honeypot traffic realistic enough to train defenses for real traffic." Re-add "(JSD 0.700) … (AUC 1.000)". |
| 33 | L159 | "We used our harness to do this" — implies we did it on purpose | "Our harness treated the whole reply as a command and typed it into Cowrie." / "Some leaked text remains where the model joined commands with no separator." |
| 34 | L153 | "attackers were **lured** into credential hunting" (causal, n=20) | "The credential share was higher on the LLM-backed honeypot for all three attackers." |
| 35 | L189 | "failed to conclude as it… made mistakes in the LLM" | "also ended differently, mostly in lost connections and LLM errors" (backend errors, not attacker mistakes) |
| 36 | L265 | "can have biases"; "may over-estimate the accuracy and reliability" | "may **share** biases… may overstate how correct the labels are"; "we did not validate them against human annotators" |
| 37 | L87 | "number of independent observations is thus reduced to 22"; garbled template definition | "The effective real sample size is therefore 22." / "Two sessions with the same sequence of normalized commands share a behavior template." |
| 38 | L40, L92 | "as in MITRE ATT&CK tactics"; "the nine categories from MITRE ATT&CK" (our labels are our own rubric) | "in the spirit of MITRE ATT\&CK tactics"; "nine categories aligned with MITRE ATT\&CK"; "we never use it to label training data" |
| 39 | L30 | "We did a test to find out if this is possible"; "wide distance between the two corpora without any labels"; "The gap is a gap of intent" | "We tested whether this works." / "Without any labels, the two corpora are far apart." / "The gap is one of intent." |
| 40 | L48–51 | contributions: "extract the CyberLab export"; "a blank"; vague "they" | "parses the CyberLab export"; "reads the CyberLab export as empty"; see `paper/main.tex` L48–51 |
| 41 | L291 | "the labels that the annotators used" | "both annotators' labels" (they produced them) |

## 4. Terminology and naming

| # | Line | Problem | Fix |
|--:|:--|:--|:--|
| 42 | L103, L232 | "adjusts raw agreement **to** the chance agreement"; "labels for the LLM"; "full level of agreement" | "corrects raw agreement **for** chance"; "LLM labels"; "**raw** agreement" |
| 43 | L106 | "balanced (equal) class weight"; stray "Classifier 300:" | "a random forest with 300 trees and balanced class weights" (balanced ≠ equal) |
| 44 | L96 | TF-IDF described as two features | "weights each token by its frequency in a session and its rarity across sessions" |
| 45 | L94 | "Jensen-Shannon divergence Jensen-Shannon divergence (JSD)" (duplicated); "common, different verbs"; "bootstrap" dropped | define once; "shared distinct verbs"; "we bootstrap: resample sessions with replacement" |
| 46 | L174 | "manipulation of accounts", "hijacking of resources"; "privilege escalation (40.0%) **or** persistence" | use the tactic names: account manipulation, resource hijacking; "and" |
| 47 | many | inconsistent names: "Cyber Lab", "1672", "synthesized", "crypto miner", "red teamers", "a node we control", "honey pot", "OPUS", "back-end", "behaviours", "Cyber-Physical", "LLM-supported" | CyberLab, 1,672, synthetic, cryptominer, LLM red-team agents, a honeypot we control, honeypot, Opus, backend, behaviors, cyber-physical, LLM-backed |
| 48 | L120 | Table I caption shortened by me — precision restored (✅ fixed) | — |

## 5. Grammar / style

| # | Line | Problem | Fix |
|--:|:--|:--|:--|
| 49 | L30 | "Two LLM blind and independent annotator… labeled sessions"; "Classifier trained on…"; "the real sessions trained one" | "We labeled sessions with two blind, independent LLM annotators (Cohen's kappa 0.898)." / "A classifier trained on the 120 synthetic sessions reached…, against 0.983 for one trained on real sessions." |
| 50 | L40, L42 | "honeypot for example Cowrie"; "no-brainer"; "as we please"; "Real honey pot logs have different bots" | "such as Cowrie"; formal wording; "The bots that fill real honeypot logs behave differently." |
| 51 | L101, L106, L232 | duplicated sentences: adjudicator sentence, TF-IDF sentence, "One issue is far more important than any other." | delete the second copy |
| 52 | L232 | "The real items kappas…"; "TWELVE items"; "Throughout the dota template" | "Kappa was 0.873 on real items…"; "The annotators agreed on 172 items, and the adjudicator resolved the other 12."; "On the dota template" |
| 53 | L233–236 | garbled Q1/Q2/GroupKFold sentences; Q2 never named | see `paper/main.tex` (Q1 trains on 60 sessions per fold…; Q2 reaches 0.983…) |
| 54 | 13 places | contractions (don't, it's, can't, weren't, didn't, they're…) — informal for IEEE | expand: do not, it is, cannot… |
| 55 | L60–81 | tense shifts; "Rabanser et al.\ compares"; mid-sentence "Distributed" | "compare"; present tense; lower-case |
| 56 | L87, L92 | "using the same bot script, using…"; "IP numbers"; "5 letter"; "We have 3 measures"; missing comma in the tactic list (reads as 8 categories) | "IP addresses"; "five-letter"; "three measures"; "ingress tool transfer, execution and resource hijacking" |
| 57 | L159–189 | "If left to their own devices… mess up"; "almost void of"; "Both do not appear"; comma splices | "Left in place, the leaks would… distort every statistic"; "almost absent"; "Neither view looks like the synthetic profile." |
| 58 | L265–287 | fragments ("Future work: Human audit…"); "lacks of"; "1 day", "top 5" | "A human audit of all 184 items is future work."; "lacks"; "one day", "top five" |
| 59 | L43, L52 | "all combinations of synthetic and real data" (real→synthetic is never run) | "four train–test pairings" |

**Counts:** compile/render 7 · wrong facts/numbers 18 · meaning/garbled 16 · terminology 7 · grammar/style 11.
