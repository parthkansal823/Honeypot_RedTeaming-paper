# 5 Conclusion and Future Work

## 5.1 Conclusion

We set out to answer a practical question: can LLM red-team agents generate honeypot sessions that are good enough to train a defender's intent classifier? Under the conditions we tested, a single "explore the system" persona, three attacker models and two honeypot backends, the answer is no.

The evidence points the same way from every angle. Without any labels, the synthetic and real corpora are almost perfectly separable: their command-verb distributions have a Jensen-Shannon divergence of 0.700, and a simple classifier tells them apart with an AUC of 1.000, still 0.996 when it sees only verbs. With blind dual-LLM labels that agree well (Cohen's κ = 0.898), a classifier trained on synthetic sessions reaches a macro-F1 of only 0.205 on real sessions (0.071 when each real behaviour is counted once), against 0.983 for a classifier trained on real data. Adding the synthetic sessions to real training data gives no gain (0.981). Changing the most influential label does not change this picture.

The reason is intent, not vocabulary. The agents know the right commands (their vocabulary covers 82% of real verb occurrences), but they use them to explore files and hunt for credentials, as a penetration tester would. The real traffic on our sample day came mostly from bots that profiled the CPU, took over the account and ran a cryptominer kit: one such script alone produced 1,038 of 1,672 interactive sessions. The LLM-backed honeypot made only the smallest attacker look a little more realistic and made all attackers hunt more for credentials. Along the way we found that one attacker model leaked its chat-format control tokens and private reasoning into the shell in 18 of 40 sessions, a contamination problem that any similar pipeline has to filter.

These results do not mean that LLM agents are useless for honeypot research. They mean that *what the agent is asked to be* matters more than *which agent* it is or *how clever the honeypot* is, and that synthetic security data must be checked against real data before it is trusted. The label-free tests used here are cheap and need no annotation, so they can be run before anyone spends money on labelling synthetic data.

## 5.2 Deviation from Expected Results

Several outcomes differed from what we expected when the project began. [@tab:deviation] lists them with our explanation.

Table: Expected versus actual results. {#tab:deviation widths=5,5,6}

| Expectation at the start | What actually happened | Explanation |
|---|---|---|
| Agent sessions would be "somewhat" realistic, with moderate JSD | JSD 0.700 and AUC 1.000: almost no overlap | The agents pursued a different goal from the dominant real population |
| An LLM-backed honeypot would make every agent more realistic | Only Gemma-3-4B moved closer; credential hunting rose for all | A richer environment changes how a curious agent explores, not whether it behaves like a bot |
| Synthetic data would at least help when mixed with real data | Q4 (0.981) ≈ Q2 (0.983); no consistent gain | Synthetic labels and behaviours barely overlap with real ones |
| Larger models would look more realistic than small ones | No clear size ordering; the 4B model was the one that moved most | Persona dominates model size |
| Refusals would be a major problem | One refusal in 120 sessions | The research framing in the prompt worked; leakage was the bigger problem |
| A standard Cowrie parser would read the public data | It read zero sessions without any error | The CyberLab export uses a different structure |
| Keyword rules would be good enough as labels | They mislabelled bot behaviour and were circular | Led to the switch to blind dual-LLM labels |

## 5.3 Lessons Learned

1. **Measure before you label.** Label-free tests (JSD, C2ST) showed the core result before a single label existed, at almost no cost.
2. **Group by behaviour, not by session.** With 1,672 sessions but only 22 templates, random splits would have given meaningless scores.
3. **Silent failures are the dangerous ones.** The parser that read zero sessions and the model that leaked its reasoning both produced plausible-looking output.
4. **Keep failed sessions.** Connection losses and LLM errors told us as much about the setup as the completed sessions.
5. **Write the rubric first.** Agreeing on definitions before labelling made the disagreements few and easy to discuss.

## 5.4 Future Work

The limitations in Section 4.12 point directly to the next steps, summarised in [@tab:future].

Table: Future work. {#tab:future widths=4,7,5}

| Direction | What to do | Expected benefit |
|---|---|---|
| Bot-like personas | Prompt agents as a dropper, a cryptominer, a credential stuffer and a Mirai-style scanner, then rerun the transfer matrix | Tests whether persona design can close the intent gap |
| Persona randomisation | Vary goals, skill and style across sessions, in the spirit of domain randomisation (Tobin et al., 2017) | Wider coverage of real behaviour |
| More real data | More days of CyberLab and other honeynets, including HoneyCloud-style IoT data (Dang et al., 2019) | Less dependence on one day and one campaign |
| Independent human audit | Two security analysts outside the author team label the same 184 items | Measures human–human and human–LLM agreement (Design C) |
| Better LLM honeypots | Fine-tuned or state-tracking shells (Otal and Canbaz, 2024) evaluated with a unified protocol (Weber, Feger and Pilgermann, 2024) | Separates backend quality from attacker behaviour |
| Stronger agents and benchmarks | Agents from CTF benchmarks (Shao et al., 2024; Zhang et al., 2025) and exploit-capable agents (Fang et al., 2024a; Happe, Kaplan and Cito, 2023) | Tests whether capability changes footprints |
| Generative baselines | Compare agent data with GAN-style generators where enough real data exists (Ring et al., 2019; Lin, Shi and Xue, 2022) | Puts agent data in context with other synthetic methods |
| Sequence models | Classifiers that use command order, not just bags of tokens | May capture behaviour beyond vocabulary |
| Contamination checks as standard | Report chat-token leak rates and C2ST AUC with every synthetic honeypot dataset | Makes synthetic data quality visible |
| Datasheets | Publish a datasheet for the synthetic corpus (Gebru et al., 2021) | Responsible reuse |

## 5.5 Final Remarks

The idea that AI agents can manufacture realistic attack data is attractive, and it may yet work. This project shows that it does not work automatically. An agent asked to "explore the system" behaves like an explorer, and the internet's honeypots are visited mostly by bots that do not explore at all. Training data has to come from, or be checked against, the population we actually want to defend against. We hope that the open pipeline, the label-free tests and the documentation in this report make that check easy for the next team that tries.
