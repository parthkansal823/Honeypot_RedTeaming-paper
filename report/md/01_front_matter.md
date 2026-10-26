# ACKNOWLEDGEMENT

This project would not have been possible without the help of many people, and we are glad to thank them here.

We are deeply grateful to our supervisor, [Name of the Supervisor], for steady guidance, honest feedback and for always asking the uncomfortable question "how do you know that number is right?". That single question shaped the whole method of this work. We also thank [Name of the Head of the Department], Head of the Department, and all faculty members of the [Department of Computer Science and Engineering], Chandigarh University, for providing the academic environment, the laboratory time and the encouragement we needed.

We thank the maintainers of the Cowrie honeypot and the authors of the CyberLab honeynet dataset. Their decision to release software and data openly made this study possible. Our thanks also go to the many open-source communities whose tools we used every day: Python, scikit-learn, SciPy, NumPy, Matplotlib, Paramiko, Docker, LaTeX and draw.io.

Finally, we thank our families and friends for their patience during the long evenings spent watching log files scroll past, and each other, for the arguments that made the work better.

Keshav, Anshul Sharma, Parth Kansal and Virain Nayar

\newpage

# ABSTRACT

Labelled attack data is scarce, so it is tempting to let LLM "red-team" agents attack a honeypot we own and train on what they do. We tested whether this works. Three LLM attackers (DeepSeek-V3.2, Gemma-3-4B, GPT-OSS-120B) each ran 20 sessions against a static Cowrie honeypot and one whose replies were written by Qwen3-32B. We compared these 120 sessions with 1,672 real interactive sessions (22 behaviour templates) from one day of the public CyberLab honeynet.

Without labels, the two sets are almost perfectly separable: verb distributions diverge strongly (Jensen-Shannon divergence 0.700) and a simple classifier tells them apart (AUC 1.000). The reason is intent: the agents explored files and hunted credentials, while 1,038 real sessions ran one cryptominer dropper. With blind dual-LLM intent labels (Cohen's κ 0.898), a classifier trained on synthetic sessions scored a macro-F1 of 0.205 on real sessions, against 0.983 when trained on real data; adding synthetic data gave no gain (0.981). GPT-OSS-120B also leaked chat-format tokens into the shell in 18 of 40 sessions.

With a single "explore the system" persona, LLM-agent sessions are not a substitute for real honeypot traffic.

**Keywords:** honeypot; Cowrie; large language models; red teaming; synthetic data; dataset shift; intrusion detection

\newpage

# GRAPHICAL ABSTRACT {landscape}

![Graphical abstract. Two attacker conditions produce 120 synthetic sessions that are compared with 1,672 real CyberLab sessions, first without labels and then with a four-quadrant transfer test.](images/d02_graphical_abstract.png){#fig:graphical-abstract nonumber landscape}


# ABBREVIATIONS

Table: List of abbreviations used in this report. {#tab:abbrev nonumber widths=3,12}

| Abbreviation | Full form |
|---|---|
| ACM | Association for Computing Machinery |
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| ATT&CK | Adversarial Tactics, Techniques and Common Knowledge (MITRE knowledge base) |
| AUC | Area Under the (ROC) Curve |
| AWS | Amazon Web Services |
| C2 | Command and Control |
| C2ST | Classifier Two-Sample Test |
| CI | Confidence Interval |
| CLI | Command-Line Interface |
| CPU | Central Processing Unit |
| CSV | Comma-Separated Values |
| CTF | Capture The Flag |
| CV | Cross-Validation |
| CVD | Colour Vision Deficiency |
| DPDP | Digital Personal Data Protection (Act, India, 2023) |
| DOI | Digital Object Identifier |
| F1 | Harmonic mean of precision and recall |
| GAN | Generative Adversarial Network |
| HTTPS | Hypertext Transfer Protocol Secure |
| IDS | Intrusion Detection System |
| IoT | Internet of Things |
| IP | Internet Protocol |
| JSD | Jensen-Shannon Divergence |
| JSON | JavaScript Object Notation |
| JSONL | JSON Lines (one JSON object per line) |
| KL | Kullback-Leibler (divergence) |
| LLM | Large Language Model |
| LNNS | Lecture Notes in Networks and Systems (Springer) |
| ML | Machine Learning |
| NIST | National Institute of Standards and Technology |
| PNG | Portable Network Graphics |
| Q1–Q4 | Quadrants 1 to 4 of the transfer experiment |
| RF | Random Forest |
| ROC | Receiver Operating Characteristic |
| SOC | Security Operations Centre |
| SSH | Secure Shell |
| SUID | Set User ID (Unix permission bit) |
| TF-IDF | Term Frequency – Inverse Document Frequency |
| TTP | Tactics, Techniques and Procedures |
| UTC | Coordinated Universal Time |
| VM | Virtual Machine |


# SYMBOLS

Table: List of symbols used in equations and tables. {#tab:symbols nonumber widths=3,12}

| Symbol | Meaning |
|---|---|
| P, Q | Two probability distributions (for example, synthetic and real verb frequencies) |
| M | Mixture distribution, M = ½(P + Q) |
| D_KL(P‖Q) | Kullback-Leibler divergence of P from Q |
| JSD(P‖Q) | Jensen-Shannon divergence between P and Q (base 2, range 0 to 1) |
| H(P) | Shannon entropy of distribution P |
| J(A, B) | Jaccard index of sets A and B |
| A ∩ B, A ∪ B | Intersection and union of sets |
| \|A\| | Number of elements in set A |
| N | Number of documents (sessions) |
| tf(t, d) | Frequency of token t in document d |
| df(t) | Number of documents that contain token t |
| w(t, d) | TF-IDF weight of token t in document d |
| κ | Cohen's kappa (chance-corrected agreement) |
| p_o, p_e | Observed and chance-expected agreement |
| P_c, R_c | Precision and recall for class c |
| F1_c | F1 score for class c |
| C_test | Set of classes present in the test set |
| B | Number of bootstrap resamples (500 in this work) |
| n_train, n_test | Training and test set sizes |
| Δ | Relative change, for example in latency |
| θ̂ | An estimated statistic (for example a JSD value) |
| 1[·] | Indicator function (1 if the condition is true, else 0) |
| s_i | Classifier score for item i |
