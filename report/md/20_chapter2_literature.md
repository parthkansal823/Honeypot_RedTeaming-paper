# 2 Literature Survey

This chapter reviews the work that this project builds on. We start with a timeline of the problem, then look at the reviewed literature as a whole (a small bibliometric analysis), and then go theme by theme: honeypots, the data they produce, the threats that dominate it, machine learning on intrusion data, synthetic data, LLMs and LLM agents, LLM-based honeypots, dataset shift, and LLM-based annotation. The chapter ends with a summary table of the solutions proposed by other researchers, a gap analysis, the formal problem definition and our objectives.

## 2.1 Timeline of the Reported Problem

The question "how do we get realistic attack data?" is almost as old as networked computing. [@fig:timeline] places the key works on one time axis and [@tab:timeline-lit] describes what each one changed.

![Timeline of work on honeypots, attack data and LLM agents, from 1989 to this project.](images/d12_literature_timeline.png){#fig:timeline landscape}

Table: Milestones in the history of the problem. {#tab:timeline-lit widths=2,5,9}

| Year | Work | What changed |
|---|---|---|
| 1989 | The Cuckoo's Egg (Stoll, 1989) | Showed that watching a live intruder reveals goals and methods that logs alone hide |
| 1992 | An Evening with Berferd (Cheswick, 1992) | First deliberate "jail" built to keep an attacker busy and observed |
| 2000 | DARPA/KDD critique (McHugh, 2000) | Warned that synthetic intrusion benchmarks may not resemble real traffic |
| 2003 | Honeynet Project; Honeypots: Tracking Hackers (Spitzner, 2003a; 2003b) | Gave honeypots a vocabulary, a taxonomy and an ethics discussion |
| 2004 | Honeyd (Provos, 2004); Honeycomb (Kreibich and Crowcroft, 2004) | Cheap virtual honeypots at scale; automatic signatures from honeypot traffic |
| 2005 | Internet Motion Sensor (Bailey et al., 2005) | Large darknet monitoring; showed how much of the internet's noise is automated |
| 2009 | Kippo SSH honeypot (Tamminen, 2009) | Medium-interaction SSH shell emulation; ancestor of Cowrie |
| 2010 | Outside the Closed World (Sommer and Paxson, 2010) | Explained why ML-based intrusion detection fails outside the lab |
| 2015 | Cowrie (Oosterhof, 2015); IoTPOT (Pa et al., 2015) | Modern SSH/Telnet honeypot; first large IoT honeypot study |
| 2017 | Mirai (Antonakakis et al., 2017) | Botnets built from IoT devices with default passwords dominate honeypot logs |
| 2018 | Outlaw (Trend Micro, 2018); Bitter Harvest (Vetterl and Clayton, 2018) | Cryptomining botnets on Linux; honeypots can be fingerprinted at internet scale |
| 2019 | CyberLab capture (Sedlar et al., 2020); HoneyCloud (Dang et al., 2019) | Public honeynet dataset; fileless attacks on Linux IoT devices |
| 2022 | Dos and Don'ts of ML in security (Arp et al., 2022) | Catalogue of pitfalls such as sampling bias and data snooping |
| 2023 | shelLM (Sladić et al., 2023); chatbot honeypots (McKee and Noever, 2023); LLM pentesting (Happe and Cito, 2023) | LLMs used both to fake a shell and to attack one |
| 2024 | PentestGPT (Deng et al., 2024); HoneyGPT (Wang et al., 2024); web-hacking agents (Fang et al., 2024b) | LLM agents and LLM honeypots become research tools |
| 2025 | Cybench (Zhang et al., 2025); open frontier models (DeepSeek-AI, 2025; Yang et al., 2025) | Standard benchmarks for offensive agents; strong open-weight models |
| 2026 | This project | First measurement of whether agent-generated honeypot sessions transfer to real traffic |

Two threads run through this history. One is about **collecting** better data (from Stoll's notebook to public honeynet datasets). The other is about **simulating** data, and every generation of simulated data has eventually been criticised for not looking like the real thing (McHugh, 2000; Tavallaee et al., 2009; Engelen, Rimmer and Joosen, 2021). LLM agents are the newest entry in the simulation thread, and this project asks the same old question of them.

## 2.2 Bibliometric Analysis

To see the shape of the field, we treated the 122 sources reviewed for this project as a small corpus and counted them by publication period, publication type and theme. This is a bibliometric description of *our reviewed set*, not of the whole field; we chose the set by following citations outward from the core papers on honeypots, LLM agents and dataset shift.

![Reviewed works by publication period and by type (n = 122).](images/c15_biblio_period_type.png){#fig:biblio-period}

![Reviewed works by theme, split into works published before 2020 and from 2020 onwards.](images/c16_biblio_theme.png){#fig:biblio-theme}

[@fig:biblio-period] shows two bursts. The first, from 2000 to 2019, is the classic honeypot and intrusion-detection literature: books, journal surveys and conference papers. The second starts in 2023 and is driven almost entirely by LLMs; a large share of it is still in preprint form, which is normal for a field that moves this fast but also means many results have not yet been peer reviewed. [@fig:biblio-theme] shows the same split by theme. Honeypot work and statistical methods are mostly older and stable, while everything involving LLMs, whether as attackers, as honeypots or as annotators, is recent. Crucially, the two bursts barely cite each other: LLM-agent papers measure whether the agent succeeds, and honeypot papers describe what real attackers do, but we found no work that compares the two directly.

Table: Reviewed literature by theme, with representative works. {#tab:biblio widths=5,2,9}

| Theme | Works | Representative works |
|---|---|---|
| Honeypots and deception | 20 | Spitzner (2003a); Provos (2004); Oosterhof (2015); Pa et al. (2015); Franco et al. (2021) |
| Foundation models and LLM safety | 18 | Vaswani et al. (2017); Brown et al. (2020); Ouyang et al. (2022); Bai et al. (2022) |
| Statistics and ML methods | 14 | Breiman (2001); Lin (1991); Efron and Tibshirani (1993); Fawcett (2006) |
| Synthetic data and dataset shift | 12 | Quiñonero-Candela et al. (2009); Rabanser, Günnemann and Lipton (2019); Shumailov et al. (2024) |
| IDS data and ML pitfalls | 11 | McHugh (2000); Sommer and Paxson (2010); Arp et al. (2022) |
| Tools and reproducibility | 10 | Pedregosa et al. (2011); Harris et al. (2020); Gebru et al. (2021) |
| LLM agents for offence | 9 | Happe and Cito (2023); Deng et al. (2024); Zhang et al. (2025) |
| Botnets and threat landscape | 8 | Antonakakis et al. (2017); Herwig et al. (2019); Trend Micro (2018) |
| LLM annotation and agreement | 8 | Cohen (1960); Landis and Koch (1977); Gilardi, Alizadeh and Kubli (2023) |
| Ethics and regulation | 7 | Dittrich and Kenneally (2012); CERT-In (2022); European Union (2024) |
| LLM-based honeypots | 5 | McKee and Noever (2023); Sladić et al. (2023); Otal and Canbaz (2024) |

## 2.3 Honeypots: Concepts and Taxonomy

### 2.3.1 What a honeypot is

Spitzner (2003a) defines a honeypot as an information system resource whose value lies in unauthorised or illicit use of that resource. Because a honeypot has no legitimate users, it produces very little noise compared with a normal intrusion detection system: almost everything it sees is worth looking at. Surveys group honeypots by how much an attacker can do inside them, by their purpose (research or production) and by where they are deployed (Bringer, Chelmecki and Fujinoki, 2012; Nawrocki et al., 2016; Fan et al., 2018; Franco et al., 2021).

Table: Honeypot interaction levels. {#tab:interaction widths=3,5,4,4}

| Level | What the attacker gets | Strengths | Weaknesses |
|---|---|---|---|
| Low interaction | A few emulated services or banners (for example Honeyd) | Safe, cheap, scales to thousands of IPs | Little detail on post-login behaviour; easy to fingerprint |
| Medium interaction | An emulated shell and file system (Kippo, Cowrie) | Records full command sequences and downloads with low risk | Emulation gaps can be detected (Vetterl and Clayton, 2018) |
| High interaction | A real operating system, usually a VM | Most realistic behaviour | Expensive; risk of the honeypot being used to attack others |
| LLM-backed (adaptive) | A shell whose replies are written by an LLM | Can answer any command, adapts on the fly | Hallucinated state, latency, cost (Sladić et al., 2023; Wang et al., 2024) |

### 2.3.2 Notable honeypot systems

[@tab:honeypots] compares the systems most relevant to our work. Cowrie is the natural choice for SSH research: it is mature, widely deployed, logs to structured JSON and, in recent versions, can delegate command output to an LLM.

Table: Comparison of honeypot systems. {#tab:honeypots widths=3,3,4,6}

| System | Type | Protocols | Notes relevant to this project |
|---|---|---|---|
| Honeyd (Provos, 2004) | Low interaction, virtual | Many (TCP/UDP personalities) | Showed that many virtual hosts can run on one machine |
| Honeycomb (Kreibich and Crowcroft, 2004) | Signature generator | Network | Derived IDS signatures automatically from honeypot traffic |
| Kippo (Tamminen, 2009) | Medium interaction | SSH | Fake file system, session replay; development moved to Cowrie |
| Cowrie (Oosterhof, 2015) | Medium interaction | SSH, Telnet | JSON event logs, file download capture, optional LLM backend; used here |
| IoTPOT (Pa et al., 2015) | IoT honeypot + sandbox | Telnet | Captured many DDoS malware families across CPU architectures |
| HoneyCloud (Dang et al., 2019) | Hardware + software IoT honeypots | SSH, Telnet | Studied fileless attacks over twelve months |
| T-Pot (Deutsche Telekom Security, n.d.) | Multi-honeypot platform | Many | Bundles Cowrie and others with dashboards; popular in practice |
| shelLM (Sladić et al., 2023) | LLM-generated shell | SSH | LLM writes responses; humans often could not tell it was fake |
| HoneyGPT (Wang et al., 2024) | LLM-generated shell | SSH | Targets the trade-off between flexibility, interaction depth and deception |
| LLM Honeypot (Otal and Canbaz, 2024) | Fine-tuned LLM shell | SSH | Fine-tuned an open model on attacker commands and responses |

### 2.3.3 Honeypots under scrutiny

Honeypots are not invisible. Vetterl and Clayton (2018) showed that low- and medium-interaction honeypots can be fingerprinted with a single packet because their network libraries differ subtly from real servers, and they found thousands of honeypot instances on the internet, many of them badly maintained. Barron and Nikiforakis (2017) ran 102 honeypots for four months and found that bots behave the same way regardless of the environment, while human attackers react to what they find, for example running more commands when the file system looks realistic. Both findings matter here: if real traffic is mostly bots that ignore their surroundings, then making an agent's environment more realistic (our LLM backend) may not make the agent behave more like those bots.

## 2.4 What Real Honeypot Data Looks Like

### 2.4.1 Public datasets

Few honeypot datasets with full command sequences are public. The CyberLab honeynet dataset (Sedlar et al., 2020) is one of the best: it contains daily Cowrie logs from a research honeynet, with source IPs replaced by hashed identifiers and released under a CC BY 4.0 licence. The HoneyCloud authors also published their SSH and Telnet logs (Dang et al., 2019). Darknet sensors such as the Internet Motion Sensor (Bailey et al., 2005) see much more traffic, but only connection attempts, not what happens after login.

### 2.4.2 Repetition and skew

A recurring observation is that honeypot traffic is dominated by a few automated campaigns. IoTPOT saw a handful of malware families account for most Telnet compromises (Pa et al., 2015). Mirai alone infected hundreds of thousands of devices by trying default credentials (Antonakakis et al., 2017), and its successors such as Hajime keep evolving their exploits (Herwig et al., 2019). This skew is good news for a defender who wants to block the common case, but it is a trap for a machine learning researcher: a random train/test split puts copies of the same bot script on both sides, and the classifier looks far better than it is. We return to this point in Chapter 3, where we group cross-validation folds by behaviour template.

## 2.5 The Threat Landscape Inside Honeypot Traffic

Understanding *who* produces real honeypot traffic explains much of our final result.

- **Scanners and brute-forcers.** Fast internet-wide scanners make it cheap to find every open SSH port (Durumeric, Wustrow and Halderman, 2013). Dictionary attacks with default credentials follow.
- **IoT botnets.** Mirai and its relatives log in with default passwords, fingerprint the device (often with `/bin/busybox` probes) and download a binary for the right CPU architecture (Antonakakis et al., 2017; Kolias et al., 2017; Herwig et al., 2019).
- **Cryptomining groups.** The Outlaw group brute-forces SSH, changes the password, installs a miner and an SSH scanner and moves on (Trend Micro, 2018). As we show in Chapter 4, one Outlaw-style "dota" template accounts for 62% of all interactive sessions in our real data.
- **Fileless and living-off-the-land attacks.** Some attacks avoid writing files entirely and use built-in tools (Dang et al., 2019).
- **Rare human intruders.** Skilled humans and targeted attacks are rare, but they are what defenders fear most; zero-day attacks, for example, can stay undetected for months (Bilge and Dumitraş, 2012).

Frameworks such as the intrusion kill chain (Hutchins, Cloppert and Amin, 2011) and MITRE ATT&CK (Strom et al., 2018) give a shared language for these behaviours. We use ATT&CK tactics such as *discovery*, *credential access*, *persistence* and *resource hijacking* to describe sessions in this project.

## 2.6 Datasets and Machine Learning for Intrusion Detection

### 2.6.1 The long shadow of synthetic benchmarks

The intrusion detection community has been burned by synthetic data before. The DARPA 1998/1999 evaluations generated background traffic synthetically, and McHugh (2000) showed that the result did not match real networks. The derived KDD Cup 99 dataset was later found to contain huge numbers of duplicates and other artefacts (Tavallaee et al., 2009). Newer datasets such as UNSW-NB15 (Moustafa and Slay, 2015) and CIC-IDS2017 (Sharafaldin, Lashkari and Ghorbani, 2018) improved realism, yet CIC-IDS2017 itself turned out to contain labelling and feature-extraction errors (Engelen, Rimmer and Joosen, 2021). The lesson is that a dataset is only as good as the process that produced it, and synthetic processes tend to leave fingerprints.

Table: Intrusion datasets and known issues. {#tab:ids-datasets widths=4,4,8}

| Dataset | How it was produced | Known issues |
|---|---|---|
| DARPA 1998/99 (McHugh, 2000) | Synthetic background + scripted attacks | Traffic statistics unlike real networks |
| KDD Cup 99 / NSL-KDD (Tavallaee et al., 2009) | Features from DARPA data | Massive redundancy; biased evaluation |
| UNSW-NB15 (Moustafa and Slay, 2015) | Testbed with traffic generator | Still a lab environment |
| CIC-IDS2017 (Sharafaldin, Lashkari and Ghorbani, 2018) | Testbed with profiled users | Labelling and flow-extraction errors (Engelen, Rimmer and Joosen, 2021) |
| CyberLab (Sedlar et al., 2020) | Real Cowrie honeynet | Small, repetitive; one network; hashed IPs |

### 2.6.2 Why ML-based detection is hard

Sommer and Paxson (2010) gave several reasons why machine learning works well for spam or image recognition but struggles in intrusion detection: attacks are rare, errors are expensive, the gap between what the model outputs and what an operator can act on is wide, and evaluation is hard because good data is scarce. Buczak and Guven (2016) surveyed hundreds of ML methods for intrusion detection and noted the same dependence on a few old datasets. Arp et al. (2022) went further and listed ten common pitfalls in security ML papers, including sampling bias, label inaccuracy, data snooping and inappropriate baselines. Kapoor and Narayanan (2023) showed that data leakage of this kind has caused a reproducibility crisis across ML-based science.

Two related problems from malware classification are directly relevant. Pendlebury et al. (2019) showed that random splits that ignore time inflate scores, and proposed evaluating "across space and time". Jordaney et al. (2017) showed that real data drifts and that detectors need ways to notice when inputs stop looking like the training data. Our use of template-grouped folds and label-free shift measures follows from these papers.

### 2.6.3 Methods we rely on

Our classifiers are deliberately simple and well understood. Text features come from TF-IDF weighting (Spärck Jones, 1972; Salton and Buckley, 1988), and the main classifier is a random forest (Breiman, 2001) with balanced class weights, which is a common and robust response to class imbalance (He and Garcia, 2009); resampling methods such as SMOTE (Chawla et al., 2002) are an alternative we did not need. We report macro-averaged F1, which treats rare classes as seriously as common ones (Sokolova and Lapalme, 2009), together with accuracy and majority-class baselines. All of this is implemented with scikit-learn (Pedregosa et al., 2011).

## 2.7 Synthetic Data for Security

Generative models have been used to create network traffic for a decade. Generative adversarial networks, or GANs (Goodfellow et al., 2014), can produce realistic-looking flow records (Ring et al., 2019), and IDSGAN modified attack records so that they slipped past detectors (Lin, Shi and Xue, 2022). These methods need a lot of real data to learn from, which is exactly what is missing in the honeypot setting.

Robotics offers a different idea. Domain randomisation trains a model on many randomised simulations so that the real world looks like just another variation (Tobin et al., 2017). This only works if the simulations cover the real behaviour; a simulator that always produces the same kind of scene will not transfer. Our single-persona design is, in this sense, a simulator with no randomisation, and our results show the consequence.

A newer concern is what happens when models are trained on model-generated data. Shumailov et al. (2024) showed that models trained recursively on generated data gradually lose the tails of the real distribution ("model collapse"). Honeypot traffic is all tails: rare commands from rare campaigns. Synthetic data that captures only the most typical behaviour would be particularly harmful here.

## 2.8 Large Language Models and Agents

### 2.8.1 The models

Modern LLMs are built on the transformer architecture (Vaswani et al., 2017) and trained on very large text corpora. Scaling them up produced strong few-shot abilities (Brown et al., 2020), and instruction tuning with human feedback made them follow instructions reliably (Ouyang et al., 2022). Safety training, for example with a written constitution (Bai et al., 2022), makes models refuse clearly harmful requests, which is one reason why research harnesses must frame tasks carefully and why we record refusals as a separate outcome. Bommasani et al. (2021) describe these models as "foundation models" whose behaviour is hard to predict from their training alone, and Weidinger et al. (2021) catalogue the social and ethical risks they bring.

The four models used in this project come from four different vendors and span a wide size range: DeepSeek-V3.2 (DeepSeek-AI, 2025), Gemma 3 at 4 billion parameters (Gemma Team, 2025), gpt-oss-120b (OpenAI, 2025) as attackers, and Qwen3-32B (Yang et al., 2025) as the LLM honeypot backend.

### 2.8.2 Agents, reasoning and their failure modes

An LLM becomes an *agent* when it is placed in a loop: it observes the environment, decides on an action, sees the result and decides again. Chain-of-thought prompting (Wei et al., 2022) and the ReAct pattern of interleaved reasoning and acting (Yao S. et al., 2023) made such loops effective. Agents also inherit LLM weaknesses. They hallucinate facts (Ji et al., 2023), they can be steered by malicious text in their inputs (Greshake et al., 2023) and they can leak memorised training data (Carlini et al., 2021). In our setting a related problem appeared: one model leaked its own chat-format control tokens and private reasoning into the shell, as Chapter 4 describes.

### 2.8.3 Surveys of LLMs in security

Two recent surveys map the use of LLMs in cybersecurity. Xu H. et al. (2024) systematically reviewed over a hundred papers on LLMs for security tasks, and Yao Y. et al. (2024) grouped the literature into beneficial uses, offensive uses and vulnerabilities of LLMs themselves. Neither survey reports a study that checks whether agent-generated attack data resembles real attack data.

## 2.9 LLM Agents for Offensive Security

Table: LLM agents for offensive security. {#tab:agents widths=4,5,7}

| Work | What the agent does | Main finding |
|---|---|---|
| Happe and Cito (2023) | GPT-3.5 plans attacks and proposes commands run over SSH on a vulnerable VM | LLMs are useful "sparring partners" for penetration testers |
| Happe, Kaplan and Cito (2023) | hackingBuddyGPT attempts Linux privilege escalation on benchmark VMs | Strong models exploit many single-vulnerability machines; small local models far fewer |
| Deng et al. (2024) | PentestGPT splits work into reasoning, generation and parsing modules | Modular design improves task completion on benchmarks |
| Fang et al. (2024b) | GPT-4 agent attacks test websites | Agents can find and exploit web vulnerabilities without human help |
| Fang et al. (2024a) | Agent exploits known (one-day) CVEs given their descriptions | High success when the vulnerability description is available |
| Xu J. et al. (2024) | AutoAttacker automates post-breach steps | LLMs can chain post-exploitation actions |
| Shao et al. (2024) | NYU CTF Bench: 200 capture-the-flag challenges | Standard benchmark for offensive LLM evaluation |
| Zhang et al. (2025) | Cybench: professional-level CTF tasks | Measures capabilities and risks of LLM agents |

All of these works ask the same question: *can the agent succeed?* None of them asks whether the agent's footprints look like those of real intruders, which is the question that matters if the footprints are to be used as training data. The term "red teaming" is also used for a different activity, testing LLMs themselves with adversarial prompts (Perez et al., 2022; Ganguli et al., 2022); in this report, "red-team agent" always means an LLM that plays the attacker against our honeypot.

## 2.10 LLM-Based Honeypots

LLMs can also sit on the defender's side. McKee and Noever (2023) showed that ChatGPT can imitate Linux, Mac and Windows terminals well enough to be a honeypot interface. Sladić et al. (2023) built shelLM, an LLM-generated SSH shell, and found that many human testers could not tell it apart from a real system. HoneyGPT (Wang et al., 2024) aimed to balance flexibility, interaction depth and deception. Otal and Canbaz (2024) fine-tuned an open model on attacker commands and responses for a more faithful shell, and Weber, Feger and Pilgermann (2024) proposed a unified way to evaluate such honeypots.

Table: LLM-based honeypots. {#tab:llm-honeypots widths=4,5,7}

| Work | Approach | Evaluation |
|---|---|---|
| McKee and Noever (2023) | Prompted ChatGPT to act as terminals and tools | Ten feasibility tasks |
| Sladić et al. (2023) | shelLM: LLM writes every response | Human testers judged realism |
| Wang et al. (2024) | HoneyGPT shell architecture | Compared with existing honeypots on engagement |
| Otal and Canbaz (2024) | Fine-tuned open model on Cowrie-style command/response pairs | Similarity metrics and live deployment |
| Weber, Feger and Pilgermann (2024) | Unified evaluation for LLM honeypots | Evaluated GPT-3.5 on datasets of varying difficulty |

These papers judge an LLM honeypot by how well it deceives. We use one differently: as a *target* for an LLM attacker, to see whether a richer, adaptive environment changes the agent's behaviour enough to look more like real traffic.

## 2.11 Dataset Shift and Two-Sample Testing

When a model is trained on one distribution and tested on another, the situation is called dataset shift (Quiñonero-Candela et al., 2009). Moreno-Torres et al. (2012) organised the many kinds of shift into a unifying framework: covariate shift (the inputs change), prior or label shift (the class balance changes) and concept shift (the meaning of a label changes). Ben-David et al. (2010) proved that the error on the target domain is bounded by the error on the source domain plus a measure of how distinguishable the two domains are. That theory gives a practical rule: if a classifier can easily tell the two domains apart, transfer is in trouble. Lipton, Wang and Smola (2018) showed how to detect and correct label shift with black-box predictors.

Several tools measure shift without labels. Rabanser, Günnemann and Lipton (2019) compared them and found that simple methods based on two-sample tests work well. The classifier two-sample test (C2ST) of Lopez-Paz and Oquab (2017) trains a classifier to separate the two samples; an AUC near 0.5 means they are indistinguishable. Kernel methods such as the maximum mean discrepancy offer an alternative (Gretton et al., 2012). For discrete distributions such as command frequencies, the Jensen-Shannon divergence (Lin, 1991) is a natural choice: it is symmetric, bounded between 0 and 1 in base 2, and its square root is a true metric (Endres and Schindelin, 2003). It is built from the Kullback-Leibler divergence (Kullback and Leibler, 1951). Set overlap can be summarised by the Jaccard index (Jaccard, 1912), and uncertainty on any of these statistics can be estimated with the bootstrap (Efron and Tibshirani, 1993).

Table: Methods for detecting dataset shift. {#tab:shift-methods widths=4,6,6}

| Method | Idea | Use in this project |
|---|---|---|
| Jensen-Shannon divergence (Lin, 1991) | Symmetric distance between two distributions | Distance between synthetic and real verb distributions |
| Bootstrap CI (Efron and Tibshirani, 1993) | Resample to estimate uncertainty | 95% confidence interval for every JSD value |
| Jaccard index (Jaccard, 1912) | Overlap between two sets | Overlap of the two verb vocabularies |
| C2ST (Lopez-Paz and Oquab, 2017) | Train a classifier to tell samples apart | AUC of synthetic vs real, on commands and on verbs only |
| MMD (Gretton et al., 2012) | Kernel distance between samples | Considered; C2ST preferred for interpretability |
| Label-shift correction (Lipton, Wang and Smola, 2018) | Estimate and reweight class priors | Not applicable: the label sets barely overlap |

## 2.12 LLMs as Annotators and Measuring Agreement

Labelling sessions by hand is slow, and LLMs are increasingly used as annotators. Gilardi, Alizadeh and Kubli (2023) found that ChatGPT beat crowd workers on several text annotation tasks, and Törnberg (2023) reported similar results for political tweets. Ziems et al. (2024) tested 13 models on 25 social science benchmarks and concluded that LLMs are useful zero-shot annotators but do not replace careful human work. In the evaluation of chat assistants, Zheng et al. (2023) showed that strong LLMs agree with human preferences most of the time when used as judges, while also documenting biases such as favouring their own outputs.

Agreement between annotators is measured with chance-corrected statistics. Cohen's kappa (Cohen, 1960) handles two annotators; Fleiss' kappa (Fleiss, 1971) generalises it to many. Landis and Koch (1977) proposed the widely used verbal scale in which values above 0.81 indicate "almost perfect" agreement, and Artstein and Poesio (2008) discuss the pitfalls of these measures in detail. We use two blind LLM annotators from one provider, which makes kappa meaningful but also means they may share biases. Chapter 4 discusses this limitation openly.

## 2.13 Reproducible and Responsible Research

Reproducibility means that someone else can rerun our analysis and get the same numbers (Peng, 2011). Data should be findable, accessible, interoperable and reusable (Wilkinson et al., 2016), and datasets and models should come with documentation of how they were made and what they should not be used for (Gebru et al., 2021; Mitchell et al., 2019). Our work uses open, widely tested libraries (Harris et al., 2020; Virtanen et al., 2020; Hunter, 2007; Pedregosa et al., 2011) and containers for deployment (Merkel, 2014), and our charts use a colour-blind-friendly palette (Okabe and Ito, 2008).

Ethically, security research involving real systems and people is guided by the Menlo Report's principles of respect for persons, beneficence, justice and respect for law (Dittrich and Kenneally, 2012) and by professional codes such as the ACM Code of Ethics (ACM, 2018). In India, the Information Technology Act 2000 and the DPDP Act 2023 set the legal frame (Government of India, 2000; 2023). Our design choices, such as attacking only our own honeypot and using only hashed public data, follow from these principles.

## 2.14 Summary of Solutions Proposed by Different Researchers

[@tab:solutions] gathers the most relevant proposed solutions in one place, with the limitation of each that matters for our problem.

Table: Proposed solutions by different researchers and their limitations for this problem. {#tab:solutions widths=4,5,4,5}

| Researchers | Proposed solution | Data used | Limitation for our problem |
|---|---|---|---|
| Spitzner (2003a); Provos (2004) | Deploy honeypots to collect real attacker data | Live deployments | Slow, small, repetitive data |
| Pa et al. (2015); Dang et al. (2019) | Large IoT honeypot ecosystems | Months of real traffic | Expensive; still dominated by a few families |
| Sedlar et al. (2020) | Publish a real honeynet dataset | Real Cowrie logs | One network; few interactive sessions |
| Kreibich and Crowcroft (2004) | Generate signatures automatically from honeypot traffic | Honeypot captures | Signatures, not intent labels |
| Sharafaldin, Lashkari and Ghorbani (2018) | Build a testbed with profiled synthetic users | Lab traffic | Lab artefacts and labelling errors |
| Ring et al. (2019); Lin, Shi and Xue (2022) | Generate traffic with GANs | Existing flow datasets | Needs large real datasets; flows, not shell sessions |
| Tobin et al. (2017) | Randomise simulations so reality is "one more variation" | Simulated robotics scenes | Requires wide, randomised coverage |
| Happe and Cito (2023); Deng et al. (2024) | LLM agents for penetration testing | Vulnerable VMs, benchmarks | Measure success, not realism |
| Sladić et al. (2023); Wang et al. (2024) | LLM-generated honeypot shells | Human or agent attackers | Measure deception, not data quality |
| Lopez-Paz and Oquab (2017); Rabanser, Günnemann and Lipton (2019) | Detect shift with two-sample tests | Generic ML data | Never applied to agent vs real honeypot traffic |
| Gilardi, Alizadeh and Kubli (2023); Ziems et al. (2024) | Use LLMs as annotators | Text corpora | Not tested on shell sessions |
| Arp et al. (2022); Pendlebury et al. (2019) | Rules for sound security ML evaluation | Many security datasets | General guidance, not a transfer study |

## 2.15 Research Gap Analysis

[@tab:gap] crosses the main capabilities a study would need against the most relevant prior works. A tick means the work provides that capability.

Table: Research gap matrix (✓ = provided, – = not provided). {#tab:gap widths=5,2,2,2,2,2,2}

| Work | Real shell sessions | LLM attacker | LLM honeypot | Label-free shift test | Transfer test | Open pipeline |
|---|---|---|---|---|---|---|
| Barron and Nikiforakis (2017) | ✓ | – | – | – | – | – |
| Sedlar et al. (2020) | ✓ | – | – | – | – | ✓ |
| Happe, Kaplan and Cito (2023) | – | ✓ | – | – | – | ✓ |
| Deng et al. (2024) | – | ✓ | – | – | – | ✓ |
| Sladić et al. (2023) | – | – | ✓ | – | – | ✓ |
| Wang et al. (2024) | – | – | ✓ | – | – | – |
| Otal and Canbaz (2024) | ✓ | – | ✓ | – | – | – |
| Rabanser, Günnemann and Lipton (2019) | – | – | – | ✓ | – | ✓ |
| **This project** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

The gap is clear: honeypot studies describe real attackers, agent studies measure attack success, LLM-honeypot studies measure deception and shift-detection studies use generic data. No prior work puts an LLM attacker against both a static and an LLM-backed honeypot, compares its sessions with real honeypot sessions without labels, and then tests whether a model trained on one transfers to the other.

## 2.16 Summary Linking the Literature to This Project

The literature gives us both the motivation and the method. The honeypot and botnet papers tell us what real traffic is made of: a few automated campaigns that do not adapt to their environment. The intrusion-dataset papers warn that synthetic data has repeatedly failed to look real, and they teach us how to avoid inflated evaluations. The LLM-agent papers show that agents can act like intruders, and the LLM-honeypot papers show that a honeypot can talk back intelligently. The dataset-shift papers give us tools to measure the gap without labels, and the annotation papers give us a way to obtain labels when human time is limited, together with a way to measure how much to trust them. This project combines these pieces to answer a question none of them answers alone.

## 2.17 Problem Definition

Let $S$ be the set of synthetic sessions produced by LLM attackers against our honeypot, and $R$ the set of real interactive sessions in the CyberLab data. Each session is a sequence of shell commands. Let $f$ be a classifier that maps a session to one of eight intent labels. The project must:

1. measure, **without labels**, how far the distribution of $S$ is from that of $R$, with uncertainty estimates;
2. obtain **trustworthy intent labels** for both sets without circular keyword rules;
3. estimate the performance of $f$ when it is **trained on $S$ and tested on $R$**, and compare it with training on $R$ and with training on $R ∪ S$, using an evaluation that does not leak repeated templates between training and test data; and
4. explain any gap in terms that a defender can act on.

## 2.18 Goals and Objectives

The **goal** of the project is to give defenders an evidence-based answer to the question "can LLM red-team agents generate realistic honeypot training data?".

The **objectives** are written with the action verbs of Bloom's revised taxonomy (Bloom, 1956; Anderson and Krathwohl, 2001), so that each one states the level of thinking it demands, from *apply* up to *create*. The project will:

1. **O1 (Create).** *Design and build* a reliable testbed in which several LLM attackers interact with Cowrie under two backends, with complete per-turn logging and automatic recovery from honeypot freezes.
2. **O2 (Apply).** *Implement* a correct parser for the CyberLab real data and *apply* one normalisation to both corpora, reducing them to comparable behaviour templates.
3. **O3 (Analyse).** *Compare* the synthetic and real corpora without labels and *differentiate* them by structure, tactics and command verbs, using JSD with bootstrap confidence intervals, Jaccard overlap, coverage and a classifier two-sample test.
4. **O4 (Evaluate).** *Judge* the reliability of blind, independent intent labels by measuring their agreement, *resolve* disagreements transparently and *verify* the most influential labels.
5. **O5 (Evaluate).** *Assess* whether a classifier trained on synthetic sessions transfers to real sessions, and *critique* the result with template-grouped folds, de-duplicated tests, majority baselines and sensitivity checks.
6. **O6 (Create).** *Produce* and *publish* complete documentation of the code, data provenance, design decisions and limitations, as a research paper, this report and open project documentation.

Table: Objectives with their Bloom level, research questions and where they are reported. {#tab:objectives widths=2,5,2,3,4}

| Objective | Summary | Bloom level | Research question | Reported in |
|---|---|---|---|---|
| O1 | Design and build the testbed and harness | Create | RQ1, RQ4 | Sections 3.7, 4.1, 4.4 |
| O2 | Implement parsing and normalisation | Apply | RQ2 | Sections 3.7, 4.3 |
| O3 | Compare the corpora without labels | Analyse | RQ2, RQ4 | Section 4.6 |
| O4 | Judge and verify blind dual-LLM labels | Evaluate | RQ3 | Section 4.7 |
| O5 | Assess transfer between corpora | Evaluate | RQ3 | Sections 4.8, 4.9 |
| O6 | Produce and publish documentation | Create | All | Sections 3.8, 4.14, Appendices |
