# Research Paper Empirical Tables: Synthetic Attack Dataset

## Table 1: Attacker Model Behavioral Comparison (Static Honeypot Baseline)

| Attacker Model | Sessions | Mean Turns | Total Cmds | Unique Cmds | Recon (%) | Credential (%) | PrivEsc (%) | Mean Latency (s) | Sessions w/ chat leak |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemma-3-4B** | 20 | 21.0 | 420 | 158 | 57.4% | 11.0% | 6.9% | 4.43s | 0 |
| **DeepSeek-V3.2** | 20 | 13.5 | 270 | 124 | 44.4% | 27.4% | 0.7% | 4.40s | 0 |
| **GPT-OSS-120B** | 20 | 19.5 | 390 | 280 | 54.9% | 48.5% | 13.8% | 4.42s | 11 |

## Table 2: Static vs. Dynamic (LLM Qwen-32B) Honeypot Interaction

| Attacker Model | Honeypot Backend | Mean Turns | Total Cmds | Recon (%) | Credential (%) | Mean Latency (s) | Latency Overhead | Chat-leak sessions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DeepSeek-V3.2** | Static Cowrie | 13.5 | 270 | 44.4% | 27.4% | 4.40s | Baseline | 0 |
| **DeepSeek-V3.2** | Dynamic (Qwen-32B) | 16.9 | 337 | 46.3% | 34.4% | 3.65s | -17.1% | 0 |
| **Gemma-3-4B** | Static Cowrie | 21.0 | 420 | 57.4% | 11.0% | 4.43s | Baseline | 0 |
| **Gemma-3-4B** | Dynamic (Qwen-32B) | 18.5 | 370 | 47.8% | 20.0% | 2.38s | -46.3% | 0 |
| **GPT-OSS-120B** | Static Cowrie | 19.5 | 390 | 54.9% | 48.5% | 4.42s | Baseline | 11 |
| **GPT-OSS-120B** | Dynamic (Qwen-32B) | 16.2 | 325 | 39.4% | 65.2% | 5.51s | +24.8% | 7 |

## Session status counts

| Condition | completed | max_turns_reached | connection_lost | llm_error | attacker_refused | timed_out | other |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| DeepSeek-V3.2 / Static | 19 | 0 | 0 | 0 | 1 | 0 | 0 |
| DeepSeek-V3.2 / Dynamic (Qwen-32B) | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gemma-3-4B / Static | 11 | 8 | 0 | 0 | 0 | 1 | 0 |
| Gemma-3-4B / Dynamic (Qwen-32B) | 18 | 2 | 0 | 0 | 0 | 0 | 0 |
| GPT-OSS-120B / Static | 3 | 17 | 0 | 0 | 0 | 0 | 0 |
| GPT-OSS-120B / Dynamic (Qwen-32B) | 4 | 0 | 10 | 6 | 0 | 0 | 0 |