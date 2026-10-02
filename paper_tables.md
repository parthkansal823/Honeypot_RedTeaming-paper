# Empirical Findings: AI Red-Team Honeypot Datasets

This document presents the complete empirical statistics extracted from the 120 experimental attacker-vs-honeypot sessions across three distinct model families (DeepSeek-V3.2, Google Gemma-3-4B-IT, OpenAI GPT-OSS-120B) and two honeypot architectural conditions (Static Cowrie Shell vs. Dynamic LLM Qwen-32B).

## Table 1: Attacker Model Behavioral Comparison (Static Baseline)

| Attacker Model | Sessions | Mean Turns | Total Commands | Unique Commands | Reconnaissance (%) | Credential Hunting (%) | PrivEsc (%) | Mean Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemma-3-4B** | 20 | 21 | 420 | 158 | 57.9% | 11% | 6.9% | 4.43s |
| **DeepSeek-V3.2** | 20 | 13.5 | 270 | 124 | 51.9% | 27.4% | 0.7% | 4.4s |
| **GPT-OSS-120B** | 20 | 19.5 | 390 | 283 | 71.5% | 49% | 14.6% | 4.42s |

## Table 2: Static Cowrie vs. Dynamic (LLM Qwen-32B) Honeypot Interaction

| Attacker Model | Honeypot Backend | Mean Turns | Total Commands | Recon (%) | Credential (%) | Mean Latency | Latency Overhead |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DeepSeek-V3.2** | Static Cowrie | 13.5 | 270 | 51.9% | 27.4% | 4.4s | Baseline |
| **DeepSeek-V3.2** | Dynamic (Qwen-32B) | 16.8 | 337 | 57.6% | 34.4% | 3.65s | +-17% |
| **Gemma-3-4B** | Static Cowrie | 21 | 420 | 57.9% | 11% | 4.43s | Baseline |
| **Gemma-3-4B** | Dynamic (Qwen-32B) | 18.5 | 370 | 47.8% | 20% | 2.38s | +-46.3% |
| **GPT-OSS-120B** | Static Cowrie | 19.5 | 390 | 71.5% | 49% | 4.42s | Baseline |
| **GPT-OSS-120B** | Dynamic (Qwen-32B) | 16.2 | 325 | 66.5% | 66.8% | 5.51s | +24.7% |

## Key Qualitative Research Findings for the Paper

1. **Attacker Model Sophistication:**
   - **Gemma-3-4B-IT:** Demonstrates strict single-command adherence but remains largely trapped in basic file exploration (ls, pwd, /etc/passwd).
   - **DeepSeek-V3.2:** Shows advanced attack strategies, executing complex piped multi-clause commands (ind / -type f ... | head -30) targeting .ssh keys, backups, and databases.
   - **GPT-OSS-120B:** Tends to generate multi-command shell script blocks rather than single commands, leading to command concatenation artifacts in raw shell sessions.

2. **Honeypot Backend Deception & Overhead:**
   - The dynamic LLM backend (Qwen-32B) successfully responds to arbitrary shell exploration with plausible Linux file systems and configs.
   - However, the LLM backend incurs significant latency overhead compared to static emulation, which can trigger timeout disconnects if idle-drain thresholds are too aggressive.
