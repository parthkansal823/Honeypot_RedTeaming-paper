# 1 Introduction

## 1.1 Background and Motivation

### 1.1.1 Why defenders watch attackers

Every machine with a public IP address is probed within minutes of going online. Most of this traffic is automated: scanners sweep the address space, bots try default passwords, and successful logins are followed by short, scripted command sequences (Durumeric et al., 2013; Antonakakis et al., 2017). Defenders who want to understand this activity need to see it up close, and the classic way to do that is a honeypot: a system that has no production value, so any interaction with it is suspicious by definition (Spitzner, 2003a).

The idea is old. Clifford Stoll followed an intruder through Lawrence Berkeley Laboratory's systems in the 1980s (Stoll, 1989), and Bill Cheswick built a jail to watch a cracker he named "Berferd" (Cheswick, 1992). The Honeynet Project later turned these one-off efforts into a research discipline (Spitzner, 2003b), and low-cost virtual honeypots made large deployments practical (Provos, 2004; Provos and Holz, 2007). Today the most widely used SSH and Telnet honeypot is Cowrie, a medium-interaction honeypot that emulates a Linux shell and logs every login attempt, every command and every downloaded file (Oosterhof, 2015).

### 1.1.2 From logs to learning

Honeypot logs are valuable on their own, but their real promise is as training data. If we can label each session with what the intruder was trying to achieve (looking around, stealing credentials, installing a backdoor, mining cryptocurrency), we can train a classifier that does this labelling automatically for new traffic. Such labels map naturally onto the tactics of the MITRE ATT&CK knowledge base (Strom et al., 2018) and onto the stages of the intrusion kill chain (Hutchins et al., 2011). A security operations centre (SOC) can then prioritise the rare session that tries to persist over the thousands that only probe.

### 1.1.3 The supply problem

The difficulty is supply. Real interactive sessions are rare and highly repetitive. In the single day of public CyberLab data used in this project (Sedlar et al., 2020), only 1,672 of 76,785 sessions (2.18%) typed even one command, and those 1,672 sessions collapse to just 22 distinct behaviours once IP addresses, URLs and random passwords are masked. One botnet script alone accounts for 1,038 sessions. Machine learning on such data runs straight into the problems that Sommer and Paxson (2010) and Arp et al. (2022) warned about: small samples, sampling bias and evaluation that quietly rewards memorisation.

### 1.1.4 A tempting shortcut: LLM red-team agents

Large language models (LLMs) changed the picture in 2023 and 2024. Research prototypes showed that LLM agents can plan and carry out multi-step penetration tests (Happe and Cito, 2023; Deng et al., 2024), escalate privileges on Linux machines (Happe et al., 2023) and even attack web applications without human help (Fang et al., 2024b). If an agent can behave like an intruder, it can be pointed at a honeypot we own and asked to "attack" it as many times as we like. Every session would be cheap, fully logged and free of privacy concerns. That is the shortcut this project puts to the test.

> **Key idea.** Synthetic sessions are only useful as training data if a model trained on them still works on real traffic. This report measures exactly that, instead of assuming it.

## 1.2 Identification of the Client and the Need

### 1.2.1 Who needs this work

The "client" of a research project is the group of people whose problem it solves. [@tab:stakeholders] lists the main stakeholders we identified and what each of them needs from the answer.

Table: Stakeholders and their needs. {#tab:stakeholders widths=4,6,6}

| Stakeholder | Typical situation | What they need from this project |
|---|---|---|
| SOC analysts and blue teams | Run honeypots or sensors, drown in repetitive alerts | To know whether synthetic data can train intent classifiers they can trust |
| Honeypot operators and researchers | Collect data slowly, have few labelled sessions | A tested pipeline and an honest estimate of how far synthetic data can go |
| ML-for-security researchers | Publish detectors trained on public or synthetic data | Evidence about dataset shift between agent and real traffic, plus reusable code |
| Builders of LLM-based honeypots | Use an LLM to imitate a shell (Sladić et al., 2023; Wang et al., 2024) | To learn whether an adaptive backend changes attacker behaviour |
| Educators and students | Teach intrusion analysis with realistic examples | Labelled, documented, ethically sourced example sessions |
| AI safety and policy community | Track what offensive AI agents actually do (Weidinger et al., 2021) | A measured description of agent behaviour, including failure modes such as token leakage |

### 1.2.2 Evidence that the need is real

Three observations justify the need. First, real interactive data is scarce: the 2.18% interaction rate above is typical of internet-facing honeypots, where most connections are scans or failed logins (Barron and Nikiforakis, 2017; Vetterl and Clayton, 2018). Second, the scarce data is skewed: a handful of botnet families, such as Mirai and its descendants (Antonakakis et al., 2017; Kolias et al., 2017) or the Outlaw cryptomining group (Trend Micro, 2018), produce most of it. Third, practitioners are already experimenting with LLMs in security work, both for defence and for attack simulation (Xu H. et al., 2024; Yao Y. et al., 2024). If synthetic agent data does not transfer, people need to know that before they build on it.

## 1.3 Relevant Contemporary Issues

The project sits where several current debates meet. [@tab:issues] summarises them and shows how each one touches our work.

Table: Contemporary issues connected to the project. {#tab:issues widths=4,7,5}

| Issue | What is happening | Connection to this project |
|---|---|---|
| Offensive use of LLMs | Agents that plan and run attacks are now research tools (Deng et al., 2024; Fang et al., 2024a) | We study their footprints, not their success rate, and keep them inside our own testbed |
| LLMs that imitate systems | LLMs are used as fake shells to keep attackers busy (McKee and Noever, 2023; Otal and Canbaz, 2024) | One of our two honeypot backends is exactly such an LLM shell |
| Training on synthetic data | Models trained on generated data can drift away from reality (Shumailov et al., 2024) | Our transfer test is a direct, domain-specific check of this risk |
| Botnets and cryptojacking | IoT and Linux botnets keep growing (Herwig et al., 2019; Dang et al., 2019) | The dominant real behaviour in our data is a cryptominer dropper |
| Data protection | India's DPDP Act 2023 and the IT Act 2000 govern personal data (Government of India, 2000; 2023) | The real dataset uses hashed IPs; we never try to re-identify anyone |
| Incident reporting | CERT-In requires cyber incidents to be reported within six hours (CERT-In, 2022) | Better automatic triage of honeypot sessions supports faster reporting |
| AI regulation and risk management | The EU AI Act and NIST AI RMF ask for documented, tested AI systems (European Union, 2024; NIST, 2023) | We document data provenance, labelling and limitations in detail |
| Reproducibility of ML research | Leakage and weak evaluation inflate results (Kapoor and Narayanan, 2023) | We group folds by template, de-duplicate and publish all scripts |

## 1.4 Problem Identification

Putting the background together, the problem can be stated in plain words:

*Defenders want to train intent classifiers for honeypot sessions, but real labelled sessions are scarce and repetitive. LLM agents can generate unlimited synthetic sessions against a honeypot we control, but nobody has measured whether a model trained on those sessions works on real traffic, or how the two kinds of traffic differ.*

During the early phase of the project we also found three practical problems in our own first prototype, which shaped the final design:

1. **Circular labels.** Our first classifier used keyword rules (for example, "contains `wget`" means *download*) both to create labels and, indirectly, as features. A model trained this way only re-learns the rules, so its scores look high but mean little (Arp et al., 2022).
2. **Fragile terminal input and output.** Cowrie's LLM backend sometimes replied slowly, so a naive reader cut replies short or mixed the tail of one reply into the next turn. A long-running command such as a recursive `find /` could also freeze the honeypot for minutes.
3. **A single persona.** All agents received the same "explore the system" instruction. This keeps the comparison clean, but it also means the synthetic data may simply be about a different kind of intruder than the bots that dominate real logs.

## 1.5 Task Identification

We broke the work into seven work packages. [@fig:wbs] shows the work breakdown structure and [@tab:tasks] lists the tasks, their outputs and how we checked each output.

![Work breakdown structure of the project.](images/d17_work_breakdown.png){#fig:wbs landscape}

Table: Task identification, deliverables and verification. {#tab:tasks widths=3,6,5,5}

| Work package | Main tasks | Deliverable | How it was verified |
|---|---|---|---|
| WP1 Literature and planning | Survey honeypots, IDS datasets, LLM agents, dataset shift; write research questions | Literature review, project plan | Supervisor review; gap analysis (Chapter 2) |
| WP2 Testbed | Configure Cowrie (static and LLM backends), build attacker harness, add recovery logic | `cowrie.cfg`, `better_ai_attacker.py`, Docker files | Banner probes, test sessions, infra event log |
| WP3 Data | Run 6 × 20 synthetic sessions; parse CyberLab | 120 session logs; `real_organic.jsonl` | Session counts, status counts, parser cross-check (76,785 sessions) |
| WP4 Analysis | Normalise commands, build templates, label-free comparison | `domain_shift.md/.json` | Bootstrap confidence intervals; verb-only control |
| WP5 Labels | Rubric, blind sheets, two LLM annotators, adjudication, author check | `labels_final.csv` | Cohen's kappa; disagreement review |
| WP6 Experiments | Four-quadrant transfer test, sensitivity runs, plumbing check | `table3_transfer.md/.json` | Grouped cross-validation, de-duplicated test, majority baselines |
| WP7 Dissemination | Paper (IEEE, then Springer LNNS), this report, documentation, open repository | Paper, report, docs, GitHub | Number-by-number check against `results/` |

## 1.6 Research Questions and Hypotheses

We framed the study around four research questions (RQ) and three testable hypotheses (H). Writing them down before running the final experiments helped us avoid moving the goalposts later.

Table: Research questions and hypotheses. {#tab:rq widths=2,9,6}

| ID | Question or hypothesis | Where it is answered |
|---|---|---|
| RQ1 | How do different LLM attackers behave against the same honeypot and prompt? | Section 4.4 |
| RQ2 | Without using any labels, how different are synthetic and real sessions? | Section 4.6 |
| RQ3 | Does an intent classifier trained on synthetic sessions transfer to real sessions? Does adding synthetic data help a model trained on real data? | Section 4.8 |
| RQ4 | Does an LLM-backed (adaptive) honeypot make agent traffic look more realistic? | Sections 4.4 and 4.6 |
| H1 | Synthetic and real command distributions are clearly different (JSD well above 0.5; C2ST AUC well above 0.5) | Supported (Section 4.10) |
| H2 | A synthetic-trained classifier performs much worse on real data than a real-trained one | Supported |
| H3 | The LLM backend reduces the distance between synthetic and real traffic for every attacker | Not supported (only for Gemma-3-4B) |

## 1.7 Timeline

The project ran from August to October 2026. [@fig:gantt] shows the schedule. The bars in blue are taken from the timestamps in our own log and result files (for example, all synthetic sessions were recorded between 24 and 29 September 2026); the grey bars are the planned windows for activities that leave no timestamped trace, such as reading papers.

![Project timeline (Gantt chart). Blue bars come from log and file timestamps; grey bars are approximate planned windows.](images/c17_gantt.png){#fig:gantt}

Table: Project schedule and milestones. {#tab:timeline widths=4,4,7}

| Phase | Period (2026) | Milestone |
|---|---|---|
| Literature review and planning | 1–31 August | Research questions fixed; risks listed |
| Testbed development | 10 August – 23 September | Harness with recovery logic; both Cowrie backends working |
| Synthetic data collection | 24–29 September | 120 sessions across 6 attacker × backend cells |
| Real data parsing and normalisation | 25 September – 1 October | 76,785 sessions parsed; 22 templates found |
| Label-free analysis | 28 September – 1 October | `domain_shift.md` written |
| Annotation and adjudication | 29 September – 1 October | κ = 0.898; `labels_final.csv` |
| Transfer and sensitivity experiments | 1–2 October | `table3_transfer.md`, sensitivity and plumbing runs |
| Paper writing | 1–26 October | Springer LNNS version prepared for ICICCD 2026 |
| Report and documentation | 20–31 October | This report and the project documentation |

## 1.8 Contributions

The main contributions of this project are:

1. **An open, documented pipeline** that runs LLM attackers against Cowrie, records every turn with timing information, recovers from honeypot freezes, parses the CyberLab export correctly and regenerates every table and figure from scripts.
2. **A label-free comparison** of agent and real honeypot traffic, using verb-distribution divergence with bootstrap confidence intervals and a classifier two-sample test (Lopez-Paz and Oquab, 2017), which shows that the two are almost perfectly separable and explains why.
3. **A four-quadrant transfer experiment** with blind dual-LLM labels, template-grouped cross-validation and sensitivity checks, which shows that the synthetic sessions do not transfer and do not help.
4. **A practical warning** about chat-format token leakage from one attacker model, with a simple way to detect and strip it.
5. **A parsing pitfall** that affects anyone who reuses the CyberLab data: a parser written for Cowrie's native logs silently reads zero sessions.

## 1.9 Organisation of the Report

The rest of the report is organised as follows. Chapter 2 reviews the literature on honeypots, attack datasets, botnets, synthetic data, dataset shift, LLM agents, LLM honeypots and LLM-based annotation, and ends with the problem definition and objectives. Chapter 3 describes the design process: the concepts we generated, the specifications and constraints, three alternative designs and the reasons we chose one of them, and the detailed implementation plan with flowcharts and algorithms. Chapter 4 presents the implementation, the data, all results and the validation steps. Chapter 5 concludes, discusses where results differed from our expectations and lists future work. The appendices contain a step-by-step user manual, the annotation rubric and data schemas, and the project's achievements.
