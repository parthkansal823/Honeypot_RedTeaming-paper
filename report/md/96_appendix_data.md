## Appendix 6: Catalogue of the Real Behaviour Templates

The 1,672 interactive real sessions collapse to 22 behaviour templates after normalisation (Section 3.7.8). The table lists every template with its size, its share of the interactive sessions, the running total, its length, its final intent label and the descriptive tactics its commands touch.

Table: The real behaviour templates, largest first. {#tab:templates widths=1,2,2,2,2,3,6}

| # | Sessions | Share | Cumulative | Commands | Final label | Tactics touched |
|---|---|---|---|---|---|---|
| 1 | 1,038 | 62.1% | 62.1% | 23 | Resource hijacking | account manipulation, discovery, execution, resource hijacking |
| 2 | 429 | 25.7% | 87.7% | 19 | Persistence | account manipulation, discovery, execution, resource hijacking |
| 3 | 63 | 3.8% | 91.5% | 6 | Recon | execution |
| 4 | 43 | 2.6% | 94.1% | 10 | Recon | discovery, execution |
| 5 | 36 | 2.2% | 96.2% | 2 | Malware drop | execution, ingress tool transfer |
| 6 | 16 | 1.0% | 97.2% | 6 | Recon | execution |
| 7 | 8 | 0.5% | 97.7% | 1 | Persistence | account manipulation, credential access, defense evasion, discovery |
| 8 | 6 | 0.4% | 98.0% | 1 | Recon | discovery |
| 9 | 6 | 0.4% | 98.4% | 50 | Malware drop | account manipulation, credential access, defense evasion, ingress tool transfer, persistence |
| 10 | 5 | 0.3% | 98.7% | 46 | Malware drop | account manipulation, credential access, defense evasion, ingress tool transfer |
| 11 | 4 | 0.2% | 98.9% | 8 | Recon | discovery |
| 12 | 3 | 0.2% | 99.1% | 13 | Persistence | account manipulation, discovery, execution |
| 13 | 3 | 0.2% | 99.3% | 1 | Malware drop | discovery, execution, ingress tool transfer |
| 14 | 2 | 0.1% | 99.4% | 14 | Persistence | account manipulation, discovery, execution |
| 15 | 2 | 0.1% | 99.5% | 1 | Recon | discovery |
| 16 | 2 | 0.1% | 99.6% | 6 | Recon | execution |
| 17 | 1 | 0.1% | 99.7% | 22 | Resource hijacking | account manipulation, discovery, execution, resource hijacking |
| 18 | 1 | 0.1% | 99.8% | 48 | Malware drop | account manipulation, credential access, defense evasion, ingress tool transfer |
| 19 | 1 | 0.1% | 99.8% | 21 | Persistence | account manipulation, discovery, execution, resource hijacking |
| 20 | 1 | 0.1% | 99.9% | 2 | Malware drop | execution, resource hijacking |
| 21 | 1 | 0.1% | 99.9% | 27 | Resource hijacking | account manipulation, defense evasion, discovery, execution, ingress tool transfer, privilege escalation |
| 22 | 1 | 0.1% | 100.0% | 6 | Recon | execution |

The two largest templates alone contain 1,467 of 1,672 sessions. Both begin with the same CPU fingerprinting and differ mainly in whether a payload kit is unpacked afterwards, which is why one is labelled resource hijacking and the other persistence.

## Appendix 7: Adjudicated Annotation Disagreements

The two blind annotators disagreed on 12 of 184 items. A separate blind adjudicator chose the final label using the rubric and wrote a one-line reason. The source column comes from the hidden key file and was not visible to anyone during labelling or adjudication.

Table: Every disagreement, the final label and the adjudicator's reason. {#tab:disagreements widths=2,4,3,3,3,7}

| Item | Source | Annotator A | Annotator B | Final | Adjudicator's reason |
|---|---|---|---|---|---|
| A003 | Gemma-3-4B / Dynamic Qwen-32B | Privilege escalation | Recon | Recon | Dominated by recon: whoami, ls, cat passwd, sudo -l (recon); nano edits interactive and unconfirmed, no write committed. |
| A011 | GPT-OSS-120B / Static Cowrie | Persistence | Credential access | Persistence | Heavy credential harvesting, but attacker writes @reboot root reverse-shell cron entry; persistence outranks credential_access. |
| A019 | GPT-OSS-120B / Dynamic Qwen-32B | Credential access | Persistence | Persistence | Steals shadow/keys/databases then installs reverse-shell cron via crontab; persistence outranks credential_access in tie-break. |
| A036 | real template (1 sessions) | Resource hijacking | Malware drop | Resource hijacking | Dota campaign: repeated CPU profiling plus miner/bot download and execution; resource_hijacking outranks malware_drop. |
| A042 | Gemma-3-4B / Dynamic Qwen-32B | Recon | Credential access | Credential access | Recon plus grep for password in bashrc; searching for secrets makes credential_access outrank recon. |
| A052 | real template (1 sessions) | Persistence | Malware drop | Resource hijacking | Dota miner campaign: CPU profiling, chpasswd, miner download; resource_hijacking outranks persistence and malware_drop. |
| A058 | Gemma-3-4B / Static Cowrie | Recon | Credential access | Credential access | Reads /etc/shadow content via strings/grep for hashes; credential_access outranks surrounding recon. |
| A064 | Gemma-3-4B / Static Cowrie | Recon | Credential access | Credential access | Directly cats /etc/shadow to steal hashes; credential_access outranks recon despite apt noise. |
| A073 | Gemma-3-4B / Dynamic Qwen-32B | Credential access | Privilege escalation | Privilege escalation | Reads shadow then sudo cat and sudo -i to gain root shell; privilege_escalation outranks credential_access. |
| A079 | DeepSeek-V3.2 / Dynamic Qwen-32B | Recon | Credential access | Credential access | Reads shadow hashes and SSH authorized_keys; credential harvesting outranks recon and unused SUID hunt. |
| A093 | GPT-OSS-120B / Dynamic Qwen-32B | Malware drop | Persistence | Persistence | Appends attacker SSH key and installs payload cron; persistence achieved in-session, outranks credential_access. |
| A155 | real template (1038 sessions) | Resource hijacking | Malware drop | Resource hijacking | Dota miner campaign identical to A052: CPU profiling, chpasswd, miner download; resource_hijacking wins. |

## Appendix 8: Summary of All Synthetic Sessions

This appendix lists every one of the 120 synthetic sessions with its cell, start time (UTC), how it ended, how many commands it issued and the final intent label it received. Sessions are numbered within each cell in the order they were run.

### DeepSeek-V3.2 against Dynamic Qwen-32B

Table: Synthetic sessions of DeepSeek-V3.2 against Dynamic Qwen-32B. {#tab:syn-deepseek-dynamic widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-27 13:03:59 | completed | 6 | Credential access |
| 2 | 2026-09-27 13:10:48 | completed | 18 | Credential access |
| 3 | 2026-09-27 13:12:30 | completed | 25 | Credential access |
| 4 | 2026-09-27 13:14:59 | completed | 14 | Credential access |
| 5 | 2026-09-27 13:28:05 | completed | 19 | Credential access |
| 6 | 2026-09-27 13:30:36 | completed | 20 | Credential access |
| 7 | 2026-09-27 13:33:11 | completed | 17 | Credential access |
| 8 | 2026-09-27 13:35:29 | completed | 20 | Credential access |
| 9 | 2026-09-27 13:38:19 | completed | 13 | Credential access |
| 10 | 2026-09-27 17:21:00 | completed | 15 | Credential access |
| 11 | 2026-09-27 17:22:33 | completed | 21 | Credential access |
| 12 | 2026-09-27 17:24:38 | completed | 14 | Credential access |
| 13 | 2026-09-27 17:26:08 | completed | 23 | Credential access |
| 14 | 2026-09-27 17:29:18 | completed | 16 | Credential access |
| 15 | 2026-09-27 17:31:04 | completed | 21 | Credential access |
| 16 | 2026-09-27 17:33:10 | completed | 9 | Credential access |
| 17 | 2026-09-27 17:34:21 | completed | 9 | Recon |
| 18 | 2026-09-27 17:36:43 | completed | 23 | Credential access |
| 19 | 2026-09-27 17:39:09 | completed | 16 | Credential access |
| 20 | 2026-09-27 17:40:32 | completed | 18 | Credential access |

### DeepSeek-V3.2 against Static Cowrie

Table: Synthetic sessions of DeepSeek-V3.2 against Static Cowrie. {#tab:syn-deepseek-static widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-24 07:26:49 | attacker refused | 7 | Credential access |
| 2 | 2026-09-24 23:08:00 | completed | 13 | Recon |
| 3 | 2026-09-24 23:15:07 | completed | 8 | Credential access |
| 4 | 2026-09-24 23:51:40 | completed | 22 | Recon |
| 5 | 2026-09-24 23:53:43 | completed | 12 | Credential access |
| 6 | 2026-09-24 23:54:40 | completed | 12 | Credential access |
| 7 | 2026-09-27 00:42:35 | completed | 23 | Malware drop |
| 8 | 2026-09-27 00:44:38 | completed | 21 | Credential access |
| 9 | 2026-09-27 01:29:06 | completed | 13 | Credential access |
| 10 | 2026-09-27 01:45:31 | completed | 13 | Credential access |
| 11 | 2026-09-27 01:46:33 | completed | 9 | Credential access |
| 12 | 2026-09-27 01:47:16 | completed | 18 | Credential access |
| 13 | 2026-09-27 02:00:24 | completed | 11 | Credential access |
| 14 | 2026-09-27 02:05:01 | completed | 15 | Credential access |
| 15 | 2026-09-27 02:06:16 | completed | 9 | Credential access |
| 16 | 2026-09-27 02:07:00 | completed | 9 | Credential access |
| 17 | 2026-09-27 02:10:13 | completed | 18 | Recon |
| 18 | 2026-09-27 02:11:50 | completed | 9 | Credential access |
| 19 | 2026-09-27 02:12:35 | completed | 18 | Credential access |
| 20 | 2026-09-27 02:15:02 | completed | 10 | Credential access |

### GPT-OSS-120B against Dynamic Qwen-32B

Table: Synthetic sessions of GPT-OSS-120B against Dynamic Qwen-32B. {#tab:syn-gpt-dynamic widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-27 18:10:05 | llm error | 9 | Credential access |
| 2 | 2026-09-27 18:13:01 | llm error | 20 | Credential access |
| 3 | 2026-09-27 18:15:42 | llm error | 14 | Credential access |
| 4 | 2026-09-27 18:52:25 | llm error | 11 | Credential access |
| 5 | 2026-09-27 19:46:28 | completed | 11 | Credential access |
| 6 | 2026-09-27 19:57:03 | connection lost | 22 | Credential access |
| 7 | 2026-09-27 20:00:40 | llm error | 18 | Credential access |
| 8 | 2026-09-27 20:04:43 | connection lost | 15 | Credential access |
| 9 | 2026-09-27 20:08:33 | connection lost | 14 | Credential access |
| 10 | 2026-09-27 20:12:18 | connection lost | 17 | Credential access |
| 11 | 2026-09-29 16:48:59 | completed | 14 | Persistence |
| 12 | 2026-09-29 17:13:11 | connection lost | 22 | Persistence |
| 13 | 2026-09-29 17:17:02 | connection lost | 16 | Credential access |
| 14 | 2026-09-29 17:21:26 | connection lost | 10 | Credential access |
| 15 | 2026-09-29 17:25:57 | connection lost | 20 | Credential access |
| 16 | 2026-09-29 17:30:02 | connection lost | 21 | Credential access |
| 17 | 2026-09-29 17:33:45 | llm error | 17 | Credential access |
| 18 | 2026-09-29 17:38:05 | completed | 16 | Persistence |
| 19 | 2026-09-29 17:41:51 | connection lost | 16 | Persistence |
| 20 | 2026-09-29 17:45:35 | completed | 22 | Credential access |

### GPT-OSS-120B against Static Cowrie

Table: Synthetic sessions of GPT-OSS-120B against Static Cowrie. {#tab:syn-gpt-static widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-27 04:47:23 | completed | 15 | Credential access |
| 2 | 2026-09-27 05:36:51 | max turns reached | 25 | Persistence |
| 3 | 2026-09-27 05:39:26 | max turns reached | 25 | Credential access |
| 4 | 2026-09-27 05:42:12 | completed | 12 | Credential access |
| 5 | 2026-09-27 05:47:59 | max turns reached | 20 | Credential access |
| 6 | 2026-09-27 09:47:11 | max turns reached | 20 | Credential access |
| 7 | 2026-09-27 09:49:26 | max turns reached | 20 | Persistence |
| 8 | 2026-09-27 09:51:25 | max turns reached | 20 | Credential access |
| 9 | 2026-09-27 09:54:07 | completed | 13 | Credential access |
| 10 | 2026-09-27 10:05:25 | max turns reached | 20 | Credential access |
| 11 | 2026-09-27 10:18:09 | max turns reached | 20 | Credential access |
| 12 | 2026-09-27 10:20:49 | max turns reached | 20 | Credential access |
| 13 | 2026-09-27 10:27:02 | max turns reached | 20 | Credential access |
| 14 | 2026-09-27 10:38:09 | max turns reached | 20 | Credential access |
| 15 | 2026-09-27 10:40:30 | max turns reached | 20 | Credential access |
| 16 | 2026-09-27 10:56:45 | max turns reached | 20 | Persistence |
| 17 | 2026-09-27 11:07:33 | max turns reached | 20 | Persistence |
| 18 | 2026-09-27 11:12:41 | max turns reached | 20 | Credential access |
| 19 | 2026-09-27 11:16:04 | max turns reached | 20 | Credential access |
| 20 | 2026-09-27 11:22:30 | max turns reached | 20 | Credential access |

### Gemma-3-4B against Dynamic Qwen-32B

Table: Synthetic sessions of Gemma-3-4B against Dynamic Qwen-32B. {#tab:syn-gemma-dynamic widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-27 19:12:09 | completed | 7 | Credential access |
| 2 | 2026-09-27 19:13:21 | completed | 19 | Malware drop |
| 3 | 2026-09-27 19:14:42 | completed | 19 | Malware drop |
| 4 | 2026-09-27 19:16:29 | max turns reached | 25 | Recon |
| 5 | 2026-09-27 19:19:00 | completed | 13 | Persistence |
| 6 | 2026-09-27 19:19:50 | completed | 15 | Credential access |
| 7 | 2026-09-27 19:21:21 | completed | 22 | Recon |
| 8 | 2026-09-27 19:22:53 | completed | 15 | Credential access |
| 9 | 2026-09-27 19:24:12 | completed | 16 | Privilege escalation |
| 10 | 2026-09-27 19:25:53 | completed | 11 | Credential access |
| 11 | 2026-09-27 19:27:29 | completed | 24 | Persistence |
| 12 | 2026-09-27 19:29:25 | completed | 22 | Persistence |
| 13 | 2026-09-27 19:31:18 | completed | 19 | Credential access |
| 14 | 2026-09-27 19:32:44 | completed | 22 | Recon |
| 15 | 2026-09-27 19:34:51 | completed | 19 | Credential access |
| 16 | 2026-09-27 19:37:06 | completed | 18 | Credential access |
| 17 | 2026-09-27 19:38:49 | completed | 17 | Privilege escalation |
| 18 | 2026-09-27 19:41:08 | completed | 17 | Credential access |
| 19 | 2026-09-27 19:42:12 | completed | 25 | Credential access |
| 20 | 2026-09-27 19:43:54 | max turns reached | 25 | Malware drop |

### Gemma-3-4B against Static Cowrie

Table: Synthetic sessions of Gemma-3-4B against Static Cowrie. {#tab:syn-gemma-static widths=1,5,4,2,4}

| # | Started (UTC) | Status | Commands | Final label |
|---|---|---|---|---|
| 1 | 2026-09-27 02:39:32 | completed | 22 | Credential access |
| 2 | 2026-09-27 02:42:41 | completed | 18 | Credential access |
| 3 | 2026-09-27 02:44:14 | max turns reached | 25 | Recon |
| 4 | 2026-09-27 02:46:32 | completed | 15 | Credential access |
| 5 | 2026-09-27 02:54:26 | max turns reached | 25 | Recon |
| 6 | 2026-09-27 02:56:28 | max turns reached | 25 | Recon |
| 7 | 2026-09-27 02:58:22 | completed | 24 | Credential access |
| 8 | 2026-09-27 03:01:17 | completed | 20 | Credential access |
| 9 | 2026-09-27 03:02:52 | completed | 16 | Recon |
| 10 | 2026-09-27 03:04:03 | timed out | 16 | Credential access |
| 11 | 2026-09-27 03:31:33 | max turns reached | 25 | Recon |
| 12 | 2026-09-27 03:33:33 | max turns reached | 25 | Recon |
| 13 | 2026-09-27 03:54:55 | max turns reached | 25 | Credential access |
| 14 | 2026-09-27 03:56:58 | completed | 20 | Credential access |
| 15 | 2026-09-27 04:01:58 | completed | 18 | Credential access |
| 16 | 2026-09-27 04:03:22 | max turns reached | 25 | Recon |
| 17 | 2026-09-27 04:05:25 | completed | 12 | Malware drop |
| 18 | 2026-09-27 04:09:58 | completed | 22 | Malware drop |
| 19 | 2026-09-27 04:17:38 | max turns reached | 25 | Credential access |
| 20 | 2026-09-27 04:24:59 | completed | 17 | Credential access |

## Appendix 9: Configuration Files

These are the configuration files used to run the testbed. API keys and other secrets are never stored in them; where a key field exists it is shown as `<redacted>`.

### Cowrie honeypot configuration (cowrie_etc/cowrie.cfg)

```
# Cowrie Honeypot Configuration for Research Paper Testbed

[honeypot]
hostname = svr04
log_path = var/log/cowrie
download_path = var/lib/cowrie/downloads
contents_path = honeyfs
txtcmds_path = txtcmds
ttylog = true
interactive_timeout = 300
authentication_timeout = 120

[ssh]
enabled = true
listen_endpoints = tcp:2222:interface=0.0.0.0
version = SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5

[telnet]
enabled = false

# ==============================================================================
# BACKEND CONFIGURATION
# Set backend to 'shell' for Condition A (Static Honeypot Baseline)
# Set backend to 'llm' for Condition B (Dynamic LLM-driven Honeypot)
# ==============================================================================
backend = shell

[shell]
filesystem = share/cowrie/fs.pickle
arch = linux-x64-lsb
kernel_version = 5.4.0-42-generic
kernel_build_string = #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020

# If switching to backend = llm, configure the LLM endpoint below:
[llm]
model = qwen.qwen3-32b
base_url = https://bedrock-mantle.us-east-1.api.aws/v1
api_key = <redacted>
temperature = 0.7
max_tokens = 512
```

### Docker Compose file (docker-compose.yml)

```
version: '3.8'

services:
  # ==============================================================================
  # Cowrie Honeypot Service (Isolated Target Environment)
  # ==============================================================================
  cowrie:
    image: cowrie/cowrie:latest
    container_name: cowrie-honeypot
    ports:
      - "2222:2222"
    volumes:
      - ./cowrie_etc/cowrie.cfg:/cowrie/cowrie-git/etc/cowrie.cfg:ro
      - cowrie-data:/cowrie/cowrie-git/var
      - ./var/log/cowrie:/cowrie/cowrie-git/var/log/cowrie
    environment:
      - BEDROCK_API_KEY=${BEDROCK_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
    restart: unless-stopped
    networks:
      - honeypot-net

  # ==============================================================================
  # AI Attacker & Evaluation Pipeline Service
  # ==============================================================================
  attacker:
    build:
      context: .
      dockerfile: Dockerfile.attacker
    container_name: ai-attacker-evaluator
    depends_on:
      - cowrie
    volumes:
      - ./logs:/app/logs
      - ./normalized:/app/normalized
      - ./results:/app/results
      - ./var/log/cowrie:/app/var/log/cowrie:ro
      - .:/app
    environment:
      - BEDROCK_API_KEY=${BEDROCK_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
    networks:
      - honeypot-net
    command: python generate_paper_tables.py

networks:
  honeypot-net:
    driver: bridge

volumes:
  cowrie-data:
```

### Analysis container (Dockerfile.attacker)

```
# Base image for AI Attacker & Evaluation Pipeline
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (SSH utilities, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Default entrypoint
CMD ["python", "generate_paper_tables.py"]
```

### Python dependencies (requirements.txt)

```
paramiko>=3.4.0
boto3>=1.34.0
anthropic>=0.40.0
openai>=1.50.0
requests>=2.31.0
scikit-learn>=1.4.0
scipy>=1.12.0
numpy>=1.26.0
pandas>=2.2.0
```

## Appendix 10: Source Code of the Analysis Scripts

This appendix reproduces the analysis code that produced the reported results, so that every method described in Chapter 3 can be checked line by line. The full repository, including the testbed scripts, is available on GitHub.

### Normalisation, verbs, tactic tags and templates (session_features.py)

```
"""
Shared command normalization and descriptive ATT&CK-tactic tagging, used by
domain_shift.py, train_eval_classifier.py and make_annotation_sheet.py so all
three see sessions the same way.

The tactic tagger is DESCRIPTIVE (what share of sessions touch each tactic).
It is deliberately not used as a training label for the reported numbers -
that would be the circular weak-labeling problem described in
honeypot_research_paper_plan.md.
"""

import json
import re

_URL = re.compile(r"\b(?:https?|ftp|tftp)://\S+", re.I)
_IP = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")
_QUOTED = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'")
_HEX = re.compile(r"\b[0-9a-f]{16,}\b", re.I)
_RANDTOK = re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{8,}\b")
_NUM = re.compile(r"\b\d+\b")
# Mirai-family bots echo a random 5-letter tag via `/bin/busybox ABCDE` to fingerprint
# the shell; mask it (but keep real applet names) so variants collapse to one template.
_BUSYBOX_APPLETS = {"wget", "tftp", "ftpget", "chmod", "cat", "echo", "ps", "rm", "cp", "mv",
                    "mkdir", "sh", "ls", "nc", "dd", "kill", "killall", "mount", "uname", "sleep",
                    "touch", "ln", "grep", "head", "tail", "ifconfig", "ip", "id", "telnetd",
                    "httpd", "chown", "find", "top", "free", "df", "ping", "route", "netstat",
                    "hostname", "awk", "sed", "tar", "gzip", "unzip", "whoami", "passwd"}
_BUSYBOX_TAG = re.compile(r"\bbusybox ([a-z]{3,12})\b")
_SPLIT = re.compile(r"\|\||&&|[;|&\n]|\$\(|`")

# Command-level tactic patterns, matched against a normalized segment.
TACTIC_PATTERNS = {
    "discovery": r"^(uname|whoami|id|hostname|ifconfig|ip|ps|netstat|ss|ls|pwd|w|who|uptime|df|free|"
                 r"lscpu|nproc|top|env|which|lsb_release|dmesg|mount|arp|route|last)\b|/proc/(cpuinfo|meminfo|version)"
                 r"|^cat /etc/(os-release|issue|hostname)|^crontab -l|^find\b(?!.*-perm)|^(wget|tftp|curl|ftpget)$",
    "credential_access": r"/etc/shadow|/etc/passwd\b(?!.*chpasswd)|\.ssh|id_rsa|\.bash_history|^history\b|"
                         r"password|passwd\.|secret|credential|\.aws|\.my\.cnf|wp-config",
    "account_manipulation": r"chpasswd|^passwd\b|\|\s*passwd|useradd|adduser|usermod|authorized_keys",
    "persistence": r"^crontab (?!-l)|/etc/cron|systemctl enable|rc\.local|>>?\s*\S*\.(bashrc|profile)|/etc/init\.d",
    "privilege_escalation": r"^sudo\b|^su\b|-perm -[42]000|getcap|pkexec|/etc/sudoers",
    "defense_evasion": r"history -c|unset hist|histfile|rm .*(\.bash_history|/var/log)|chattr|^iptables|"
                       r"^pkill|^kill(all)?\b|ufw disable|setenforce",
    # Bare `wget`/`tftp` with no argument is Mirai's capability probe, not a download.
    "ingress_tool_transfer": r"^(wget|curl|tftp|ftpget|scp|nc|ncat)\s+\S|busybox (wget|tftp)\s+\S",
    "execution": r"chmod \+?[0-7]*x|^\./|^(sh|bash)\b|base64 (-d|--decode)|^nohup\b|^perl\b|^python",
    "resource_hijacking": r"xmrig|minerd|stratum|cryptonight|\bminer\b|\.rsync/|dota",
}
_TACTIC_RE = {t: re.compile(p, re.I) for t, p in TACTIC_PATTERNS.items()}
TACTICS = list(TACTIC_PATTERNS)


def load_jsonl(path):
    with open(path, encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def has_chat_leak(cmd):
    """GPT-OSS sometimes emitted harmony-format tokens plus its own reasoning
    ("<|channel|>analysis<|message|>...") into the shell command."""
    return "<|" in cmd


def strip_chat_leak(cmd):
    return cmd.split("<|", 1)[0]


def normalize_cmd(cmd):
    """Mask session-specific values (URLs, IPs, quoted args, random passwords) so
    the same bot script run from different IPs normalizes to one template."""
    c = strip_chat_leak(cmd).strip().lower()
    c = _URL.sub("<url>", c)
    c = _IP.sub("<ip>", c)
    c = _QUOTED.sub("<str>", c)
    c = _HEX.sub("<hex>", c)
    c = _RANDTOK.sub("<tok>", c)
    c = _NUM.sub("<n>", c)
    c = _BUSYBOX_TAG.sub(lambda m: m.group(0) if m.group(1) in _BUSYBOX_APPLETS else "busybox <tag>", c)
    return re.sub(r"\s+", " ", c)


def segments(cmd):
    """Split a normalized command line into its chained/piped sub-commands."""
    return [s.strip() for s in _SPLIT.split(normalize_cmd(cmd)) if s.strip()]


def verb(segment):
    toks = [t for t in segment.split() if "=" not in t]  # drop VAR=x prefixes
    return toks[0].rsplit("/", 1)[-1] if toks else None


def session_verbs(session):
    return [v for c in session.get("commands") or [] for v in map(verb, segments(c)) if v]


def session_tactics(session):
    found = set()
    for c in session.get("commands") or []:
        for seg in segments(c):
            found.update(t for t, rx in _TACTIC_RE.items() if rx.search(seg))
    return found


def template_key(session):
    return tuple(normalize_cmd(c) for c in session.get("commands") or [])
```

### CyberLab parser (parse_cyberlab.py)

```
"""
Parse the CyberLab Cowrie dataset (Zenodo DOI 10.5281/zenodo.3687527) into the
same per-session JSONL schema that train_eval_classifier.py consumes.

The CyberLab export is NOT Cowrie's native JSON-lines log, so
cowrie_session_parser.py silently parses 0 sessions from it:
  - the file is one big JSON array, one `{"<session_id>": [events...]},` per line
  - IPs are replaced by `src_ip_identifier` hashes
  - command text lives in `message` as "CMD: <command>" (there is no `input` field)

Streams line-by-line, so the 600 MB file never has to fit in memory.

Usage:
    python parse_cyberlab.py [--in cyberlab_2019-11-15.json/cowrie_2019-11-15.json]
                             [--out normalized/real_organic.jsonl]
"""

import argparse
import json
from collections import Counter, defaultdict

from cowrie_session_parser import flag_findings

DEFAULT_IN = "cyberlab_2019-11-15.json/cowrie_2019-11-15.json"
DEFAULT_OUT = "normalized/real_organic.jsonl"


def iter_session_blocks(path):
    """Yield (session_id, events) from the array-of-single-key-objects format."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip().lstrip("[").rstrip(",").rstrip("]")
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            for sid, events in obj.items():
                yield sid, events


def new_session(sid):
    return {
        "session_id": sid, "source": "cyberlab_2019-11-15", "src_ip": None,
        "country": None, "protocol": None, "start": None, "end": None,
        "duration_s": None, "login_attempts": [], "login_success": False,
        "commands": [], "downloads": [], "client_version": None,
    }


def apply_event(s, ev):
    s["src_ip"] = s["src_ip"] or ev.get("src_ip_identifier")
    geo = ev.get("geolocation_data") or {}
    s["country"] = s["country"] or geo.get("country_code2")
    ts = ev.get("timestamp")
    if ts:
        s["start"] = ts if s["start"] is None or ts < s["start"] else s["start"]
        s["end"] = ts if s["end"] is None or ts > s["end"] else s["end"]

    eid = ev.get("eventid", "")
    if eid == "cowrie.session.connect":
        s["protocol"] = ev.get("protocol")
    elif eid in ("cowrie.login.success", "cowrie.login.failed"):
        success = eid.endswith("success")
        s["login_attempts"].append({"username": ev.get("username"),
                                    "password": ev.get("password"), "success": success})
        s["login_success"] = s["login_success"] or success
    elif eid == "cowrie.command.input":
        msg = ev.get("input") or ev.get("message") or ""
        s["commands"].append(msg[5:] if msg.startswith("CMD: ") else msg)
    elif eid in ("cowrie.session.file_download", "cowrie.session.file_upload"):
        s["downloads"].append({"url": ev.get("url"), "shasum": ev.get("shasum"),
                               "outfile": ev.get("outfile")})
    elif eid == "cowrie.client.version":
        s["client_version"] = ev.get("ssh_client_version") or ev.get("version")
    elif eid == "cowrie.session.closed":
        s["duration_s"] = ev.get("duration")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", default=DEFAULT_IN)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    # A session can be split across several array entries, so merge by id.
    sessions = {}
    for sid, events in iter_session_blocks(args.inp):
        s = sessions.setdefault(sid, new_session(sid))
        for ev in sorted(events, key=lambda e: e.get("timestamp") or ""):
            apply_event(s, ev)

    stats = Counter()
    with open(args.out, "w", encoding="utf-8") as out:
        for s in sessions.values():
            s["findings"] = flag_findings(s)
            s["command_count"] = len(s["commands"])
            s["login_attempt_count"] = len(s["login_attempts"])
            stats["sessions"] += 1
            stats["with_login_success"] += s["login_success"]
            stats["with_commands"] += s["command_count"] > 0
            stats["with_downloads"] += bool(s["downloads"])
            stats[f"proto_{s['protocol']}"] += 1
            out.write(json.dumps(s) + "\n")

    print(f"Parsed {stats['sessions']} sessions -> {args.out}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
```

### Label-free comparison (domain_shift.py)

```
"""
Label-free comparison of synthetic LLM-attacker sessions vs real CyberLab
honeypot sessions. Needs no annotation, so it is immune to the circular
weak-label problem and is the paper's primary evidence on realism.

Measures:
  1. corpus structure (effective number of distinct behaviors after template dedup)
  2. ATT&CK tactic coverage per corpus
  3. command-verb distributions: Jensen-Shannon divergence, vocabulary overlap
  4. classifier two-sample test (C2ST): can a simple model tell the corpora apart?
  5. per attacker x backend condition: which synthetic source is closest to real?

Usage:
    python domain_shift.py [--synthetic normalized/all_synthetic_120.jsonl]
                           [--real normalized/real_organic.jsonl]
Writes results/domain_shift.md and results/domain_shift.json.
"""

import argparse
import json
import random
import statistics
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold

from session_features import (TACTICS, has_chat_leak, load_jsonl, normalize_cmd, segments,
                              session_tactics, session_verbs, template_key)

SEED = 42
N_BOOT = 500


def dedup_by_template(sessions):
    seen, out = set(), []
    for s in sessions:
        k = template_key(s)
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


def corpus_stats(sessions):
    cmds = [c for s in sessions for c in s["commands"]]
    templates = Counter(map(template_key, sessions))
    return {
        "sessions": len(sessions),
        "distinct_templates": len(templates),
        "top5_template_share": sum(n for _, n in templates.most_common(5)) / len(sessions),
        "median_cmds_per_session": statistics.median(len(s["commands"]) for s in sessions),
        "mean_chars_per_cmd": statistics.mean(len(c) for c in cmds),
        "pct_cmds_chained": sum(len(segments(c)) > 1 for c in cmds) / len(cmds),
    }


def tactic_shares(sessions):
    counts = Counter(t for s in sessions for t in session_tactics(s))
    return {t: counts[t] / len(sessions) for t in TACTICS}


def verbs_of(session):
    """session_verbs() is regex-heavy; cache it on the session for the bootstrap."""
    if "_verbs" not in session:
        session["_verbs"] = Counter(session_verbs(session))
    return session["_verbs"]


def jsd(a_sessions, b_sessions):
    a, b = Counter(), Counter()
    for s in a_sessions:
        a.update(verbs_of(s))
    for s in b_sessions:
        b.update(verbs_of(s))
    vocab = sorted(a.keys() | b.keys())
    pa = np.array([a[v] for v in vocab], dtype=float)
    pb = np.array([b[v] for v in vocab], dtype=float)
    return float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2))


def jsd_with_ci(a_sessions, b_sessions, rng):
    point = jsd(a_sessions, b_sessions)
    boots = sorted(jsd(rng.choices(a_sessions, k=len(a_sessions)), b_sessions) for _ in range(N_BOOT))
    return point, boots[int(0.025 * N_BOOT)], boots[int(0.975 * N_BOOT)]


def c2st_auc(synthetic, real, text_fn):
    """5x5 repeated stratified CV AUC of a logistic regression separating the two
    corpora. 0.5 = indistinguishable, 1.0 = trivially separable."""
    docs = [text_fn(s) for s in synthetic + real]
    y = np.array([1] * len(synthetic) + [0] * len(real))
    aucs = []
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
    for tr, te in cv.split(docs, y):
        vec = TfidfVectorizer(token_pattern=r"[^\s]+", min_df=1)
        X_tr = vec.fit_transform([docs[i] for i in tr])
        X_te = vec.transform([docs[i] for i in te])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X_tr, y[tr])
        aucs.append(roc_auc_score(y[te], clf.predict_proba(X_te)[:, 1]))
    return float(np.mean(aucs)), float(np.std(aucs))


def fmt_pct(x):
    return f"{100 * x:.1f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--synthetic", default="normalized/all_synthetic_120.jsonl")
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--out-dir", default="results")
    args = ap.parse_args()
    rng = random.Random(SEED)

    synthetic = [s for s in load_jsonl(args.synthetic) if s.get("commands")]
    real_all = load_jsonl(args.real)
    real = [s for s in real_all if s.get("commands")]
    real_dedup = dedup_by_template(real)

    res = {"n_real_total": len(real_all), "n_real_interactive": len(real),
           "n_real_templates": len(real_dedup), "n_synthetic": len(synthetic)}
    res["structure"] = {"synthetic": corpus_stats(synthetic), "real": corpus_stats(real)}
    res["tactics"] = {"synthetic": tactic_shares(synthetic), "real": tactic_shares(real),
                      "real_dedup": tactic_shares(real_dedup)}

    syn_v = Counter(v for s in synthetic for v in session_verbs(s))
    real_v = Counter(v for s in real for v in session_verbs(s))
    res["verbs"] = {
        "top_synthetic": syn_v.most_common(10),
        "top_real": real_v.most_common(10),
        "jaccard": len(set(syn_v) & set(real_v)) / len(set(syn_v) | set(real_v)),
        "real_mass_covered_by_synthetic_vocab": sum(n for v, n in real_v.items() if v in syn_v) / sum(real_v.values()),
        "jsd_vs_real": jsd_with_ci(synthetic, real, rng),
        "jsd_vs_real_dedup": jsd_with_ci(synthetic, real_dedup, rng),
    }

    res["c2st"] = {
        "normalized_commands": c2st_auc(synthetic, real_dedup,
                                        lambda s: " ".join(normalize_cmd(c) for c in s["commands"])),
        "verbs_only": c2st_auc(synthetic, real_dedup, lambda s: " ".join(session_verbs(s))),
    }

    conditions = sorted({(s["attacker_model"], s["honeypot_backend"]) for s in synthetic})
    res["per_condition"] = []
    for model, backend in conditions:
        sub = [s for s in synthetic if (s["attacker_model"], s["honeypot_backend"]) == (model, backend)]
        point, lo, hi = jsd_with_ci(sub, real_dedup, rng)
        shares = tactic_shares(sub)
        res["per_condition"].append({
            "attacker": model, "backend": backend, "n": len(sub),
            "sessions_with_chat_leak": sum(any(has_chat_leak(c) for c in x["commands"]) for x in sub),
            "jsd_vs_real_dedup": [point, lo, hi],
            "tactics_matching_real": sum(1 for t in TACTICS if (shares[t] > 0) == (res["tactics"]["real_dedup"][t] > 0)),
        })

    out = Path(args.out_dir)
    out.mkdir(exist_ok=True)
    (out / "domain_shift.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    (out / "domain_shift.md").write_text(render_md(res), encoding="utf-8")
    print(render_md(res))


def render_md(r):
    s, rl = r["structure"]["synthetic"], r["structure"]["real"]
    L = ["# Label-free domain-shift analysis: synthetic vs. real\n",
         f"Real: {r['n_real_total']:,} sessions, {r['n_real_interactive']:,} with >=1 command, "
         f"{r['n_real_templates']} distinct normalized templates. Synthetic: {r['n_synthetic']} sessions.\n",
         "## Table 4a: Corpus structure\n",
         "| Metric | Synthetic | Real (interactive) |", "| :--- | ---: | ---: |",
         f"| Sessions | {s['sessions']} | {rl['sessions']:,} |",
         f"| Distinct behavior templates | {s['distinct_templates']} | {rl['distinct_templates']} |",
         f"| Share of top-5 templates | {fmt_pct(s['top5_template_share'])} | {fmt_pct(rl['top5_template_share'])} |",
         f"| Median commands / session | {s['median_cmds_per_session']} | {rl['median_cmds_per_session']} |",
         f"| Mean chars / command | {s['mean_chars_per_cmd']:.1f} | {rl['mean_chars_per_cmd']:.1f} |",
         f"| Commands with chaining/pipes | {fmt_pct(s['pct_cmds_chained'])} | {fmt_pct(rl['pct_cmds_chained'])} |",
         "\n## Table 4b: Share of sessions touching each ATT&CK tactic\n",
         "| Tactic | Synthetic | Real | Real (template-dedup) |", "| :--- | ---: | ---: | ---: |"]
    for t in TACTICS:
        L.append(f"| {t} | {fmt_pct(r['tactics']['synthetic'][t])} | {fmt_pct(r['tactics']['real'][t])} | "
                 f"{fmt_pct(r['tactics']['real_dedup'][t])} |")
    v = r["verbs"]
    L += ["\n## Table 4c: Command-verb distribution\n",
          f"- JSD(synthetic, real) = {v['jsd_vs_real'][0]:.3f} (95% bootstrap CI {v['jsd_vs_real'][1]:.3f}-{v['jsd_vs_real'][2]:.3f}); "
          f"vs. template-dedup real = {v['jsd_vs_real_dedup'][0]:.3f} ({v['jsd_vs_real_dedup'][1]:.3f}-{v['jsd_vs_real_dedup'][2]:.3f}). "
          "Range 0 (identical) to 1 (disjoint).",
          f"- Verb vocabulary Jaccard = {v['jaccard']:.3f}; synthetic vocabulary covers "
          f"{fmt_pct(v['real_mass_covered_by_synthetic_vocab'])} of real verb occurrences.",
          f"- Top synthetic verbs: {', '.join(f'{w} ({n})' for w, n in v['top_synthetic'])}",
          f"- Top real verbs: {', '.join(f'{w} ({n})' for w, n in v['top_real'])}",
          "\n## Table 4d: Classifier two-sample test (synthetic vs. template-dedup real)\n",
          "| Features | AUC (mean +/- sd, 5x5 CV) |", "| :--- | ---: |"]
    for name, (m, sd) in r["c2st"].items():
        L.append(f"| {name.replace('_', ' ')} | {m:.3f} +/- {sd:.3f} |")
    L += ["\nAUC 0.5 = indistinguishable; 1.0 = perfectly separable.\n",
          "## Table 4e: Per attacker x backend distance to real (template-dedup)\n",
          "| Attacker | Backend | n | JSD vs real [95% CI] | Tactics present/absent as in real (of 9) | Sessions with chat-format leak |",
          "| :--- | :--- | ---: | :--- | ---: | ---: |"]
    for c in r["per_condition"]:
        p, lo, hi = c["jsd_vs_real_dedup"]
        L.append(f"| {c['attacker']} | {c['backend']} | {c['n']} | {p:.3f} [{lo:.3f}, {hi:.3f}] | "
                 f"{c['tactics_matching_real']} | {c['sessions_with_chat_leak']} |")
    L.append("\nLeaked chat-format tokens and the reasoning text after them are stripped before all "
             "analyses; commands the model concatenated without separators cannot be recovered.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
```

### Blind annotation sheets (make_annotation_sheet.py)

```
"""Build blind annotation sheets: all distinct real templates (>=1 command) + all synthetic sessions."""
import argparse, csv, os, random
from collections import defaultdict
from session_features import load_jsonl, strip_chat_leak, template_key

MAXCMD, MAXLEN = 30, 200


def render(cmds):
    # Drop the synthetic attackers' "DONE" stop token: it is not a shell command and would identify the source.
    cmds = [strip_chat_leak(c).strip().replace("\r", " ").replace("\n", " ") for c in cmds]
    while cmds and cmds[-1] == "DONE":
        cmds.pop()
    cmds = [c for c in cmds if c]
    shown = [c if len(c) <= MAXLEN else c[:MAXLEN] + "..." for c in cmds[:MAXCMD]]
    s = " ;; ".join(shown)
    if len(cmds) > MAXCMD:
        s += f" ;; [+{len(cmds) - MAXCMD} more]"
    return len(cmds), s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--synthetic", default="normalized/all_synthetic_120.jsonl")
    ap.add_argument("--out", default="annotation")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    groups = defaultdict(list)
    for s in load_jsonl(a.real):
        if s.get("commands"):
            groups[template_key(s)].append(s)
    items = []
    for k, ss in groups.items():
        rep = min(ss, key=lambda s: s["session_id"])
        items.append((rep, "real", "", "", len(ss)))
    for s in load_jsonl(a.synthetic):
        items.append((s, "synthetic", s.get("attacker_model", ""), s.get("honeypot_backend", ""), 1))
    items.sort(key=lambda t: t[0]["session_id"])
    random.Random(a.seed).shuffle(items)

    os.makedirs(a.out, exist_ok=True)
    rows, key = [], []
    for i, (s, src, model, be, n) in enumerate(items, 1):
        iid = f"A{i:03d}"
        nc, cmds = render(s["commands"])
        rows.append((iid, nc, cmds))
        key.append((iid, s["session_id"], src, model, be, n))
    for name in ("sheet_annotator1.csv", "sheet_annotator2.csv"):
        with open(os.path.join(a.out, name), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["item_id", "n_commands", "commands", "label", "confidence", "notes"])
            for r in rows:
                w.writerow([*r, "", "", ""])
    with open(os.path.join(a.out, "annotation_sheet.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "commands"])
        for r in rows:
            w.writerow([r[0], r[2]])
    with open(os.path.join(a.out, "key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "session_id", "source", "attacker_model", "honeypot_backend", "template_size"])
        w.writerows(key)
    nr = sum(k[2] == "real" for k in key)
    print(f"{len(key)} items: {nr} real, {len(key) - nr} synthetic -> {a.out}/")


if __name__ == "__main__":
    main()
```

### Agreement and final labels (agreement.py)

```
"""Inter-annotator agreement + final label table.
Usage: python agreement.py [--dir annotation] [--a1 F] [--a2 F] [--llm F] [--adj F] [--key F]
                           [--real normalized/real_organic.jsonl] [--md results/annotation_agreement.md]
"""
import argparse
import csv
import os
import sys
from collections import Counter

from sklearn.metrics import cohen_kappa_score

from session_features import load_jsonl, template_key

LABELS = ["recon", "credential_access", "privilege_escalation", "persistence",
          "malware_drop", "resource_hijacking", "defense_evasion", "other"]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def labels_of(path, name, bad):
    out = {}
    for r in read_csv(path):
        v = (r.get("label") or "").strip().lower().replace(" ", "_")
        if not v:
            continue
        if v not in LABELS:
            bad.append((name, r["item_id"], v))
            continue
        out[r["item_id"]] = v
    return out


def kappa(x, y, ids):
    ids = sorted(ids)
    if len(ids) < 2:
        return None
    a, b = [x[i] for i in ids], [y[i] for i in ids]
    if len(set(a) | set(b)) < 2:
        return 1.0 if a == b else None
    return cohen_kappa_score(a, b, labels=LABELS)


def fmt(k):
    return "n/a" if k is None else f"{k:.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="annotation")
    ap.add_argument("--a1")
    ap.add_argument("--a2")
    ap.add_argument("--llm")
    ap.add_argument("--adj")
    ap.add_argument("--key")
    ap.add_argument("--real", default="normalized/real_organic.jsonl")
    ap.add_argument("--md", default="results/annotation_agreement.md")
    ap.add_argument("--out-labels")
    ap.add_argument("--out-disagree")
    a = ap.parse_args()
    D = a.dir

    def p(v, n):
        return v or os.path.join(D, n)

    a1p, a2p, keyp = p(a.a1, "sheet_annotator1.csv"), p(a.a2, "sheet_annotator2.csv"), p(a.key, "key.csv")
    llmp, adjp = p(a.llm, "labels_llm.csv"), p(a.adj, "adjudicated.csv")
    for f in (a1p, a2p, keyp):
        if not os.path.exists(f):
            sys.exit(f"Missing {f}. Run make_annotation_sheet.py first.")
    bad = []
    l1, l2 = labels_of(a1p, "annotator1", bad), labels_of(a2p, "annotator2", bad)
    if not l1 or not l2:
        sys.exit(f"Sheets are still blank (annotator1 labels: {len(l1)}, annotator2: {len(l2)}). "
                 f"Fill the 'label' column in {a1p} and {a2p} (see annotation/RUBRIC.md), then rerun.")
    key = {r["item_id"]: r for r in read_csv(keyp)}
    both = sorted(set(l1) & set(l2))
    if len(both) < 2:
        sys.exit("Fewer than 2 items labeled by both annotators; finish labeling first.")
    llm = labels_of(llmp, "llm", bad) if os.path.exists(llmp) else {}
    adj = labels_of(adjp, "adjudicated", bad) if os.path.exists(adjp) else {}

    L = ["# Annotation agreement\n",
         f"Items labeled by both annotators: {len(both)} of {len(key)} "
         f"(annotator1 {len(l1)}, annotator2 {len(l2)}).\n"]
    if bad:
        L.append(f"Invalid labels ignored ({len(bad)}): " + ", ".join(f"{n}:{i}={v}" for n, i, v in bad[:20]) + "\n")
    L.append("## Cohen's kappa (annotator1 vs annotator2)\n")
    L.append("| subset | n | raw agreement | kappa |\n|---|---|---|---|")
    for name, f in (("all", lambda i: True), ("real", lambda i: key[i]["source"] == "real"),
                    ("synthetic", lambda i: key[i]["source"] == "synthetic")):
        ids = [i for i in both if f(i)]
        agr = sum(l1[i] == l2[i] for i in ids) / len(ids) if ids else None
        L.append(f"| {name} | {len(ids)} | {fmt(agr)} | {fmt(kappa(l1, l2, ids))} |")
    cm = Counter((l1[i], l2[i]) for i in both)
    used = [lab for lab in LABELS if any(lab in k for k in cm)]
    L.append("\n## Confusion (rows annotator1, columns annotator2)\n")
    L.append("| a1 / a2 | " + " | ".join(used) + " |\n|---|" + "---|" * len(used))
    for r in used:
        L.append(f"| {r} | " + " | ".join(str(cm[(r, c)]) for c in used) + " |")
    if llm:
        L.append("\n## LLM pre-labels vs humans (kappa)\n\n| pair | n | raw agreement | kappa |\n|---|---|---|---|")
        for nm, h in (("LLM vs annotator1", l1), ("LLM vs annotator2", l2)):
            ids = sorted(set(llm) & set(h))
            agr = sum(llm[i] == h[i] for i in ids) / len(ids) if ids else None
            L.append(f"| {nm} | {len(ids)} | {fmt(agr)} | {fmt(kappa(llm, h, ids))} |")

    dis = [i for i in both if l1[i] != l2[i]]
    dpath = a.out_disagree or os.path.join(D, "disagreements.csv")
    rows1, rows2 = read_csv(a1p), read_csv(a2p)
    n1 = {r["item_id"]: (r.get("notes") or "").strip() for r in rows1}
    n2 = {r["item_id"]: (r.get("notes") or "").strip() for r in rows2}
    cmds = {r["item_id"]: r["commands"] for r in rows1}
    with open(dpath, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "label_annotator1", "label_annotator2", "notes1", "notes2", "commands", "label_final"])
        for i in dis:
            w.writerow([i, l1[i], l2[i], n1.get(i, ""), n2.get(i, ""), cmds.get(i, ""), adj.get(i, "")])

    # final per-item labels: agreed, else adjudicated, else excluded
    final, n_agree, n_adj, excluded = {}, 0, 0, []
    for i in key:
        if i in l1 and i in l2 and l1[i] == l2[i]:
            final[i] = l1[i]
            n_agree += 1
        elif i in adj:
            final[i] = adj[i]
            n_adj += 1
        else:
            excluded.append(i)

    # broadcast real item labels to every real session sharing the template
    rows = []
    n_real = 0
    if os.path.exists(a.real):
        real = load_jsonl(a.real)
        by_sid = {s["session_id"]: s for s in real}
        tkey_label = {}
        for i, k in key.items():
            if k["source"] == "real" and i in final and k["session_id"] in by_sid:
                tkey_label[template_key(by_sid[k["session_id"]])] = final[i]
        for s in real:
            if s.get("commands"):
                lab = tkey_label.get(template_key(s))
                if lab:
                    rows.append((s["session_id"], lab, "real"))
                    n_real += 1
    else:
        print(f"WARNING: {a.real} not found; real sessions not broadcast", file=sys.stderr)
    for i, k in key.items():
        if k["source"] == "synthetic" and i in final:
            rows.append((k["session_id"], final[i], "synthetic"))
    lpath = a.out_labels or os.path.join(D, "labels_final.csv")
    with open(lpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["session_id", "label", "source"])
        w.writerows(rows)

    L.append("\n## Final labels\n")
    L.append(f"- Items agreed: {n_agree}; adjudicated: {n_adj}; excluded (disagreement not adjudicated, "
             f"or unlabeled by an annotator): {len(excluded)} of {len(key)} items "
             f"({len(dis)} disagreements).")
    L.append(f"- Real sessions labeled via template broadcast: {n_real}; "
             f"synthetic: {sum(r[2] == 'synthetic' for r in rows)}.")
    for src in ("real", "synthetic"):
        c = Counter(r[1] for r in rows if r[2] == src)
        L.append(f"- {src} label counts: " + ", ".join(f"{lab}={c[lab]}" for lab in LABELS if c[lab]))
    os.makedirs(os.path.dirname(a.md) or ".", exist_ok=True)
    with open(a.md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nWrote {a.md}, {dpath}, {lpath}")


if __name__ == "__main__":
    main()
```

### Four-quadrant transfer experiment (train_eval_classifier.py)

```
"""
4-quadrant transfer experiment: synthetic vs real training data -> synthetic vs real test data.

Q1 synth->synth (StratifiedKFold), Q2 real->real (GroupKFold by command template),
Q3 synth->real, Q4 real+synth->real (same folds as Q2).

Labels: rule_label() (same function for both domains) unless --real-labels /
--synthetic-labels CSVs (session_id,label) are supplied. Rule labels are built from
the same keywords as the features -> PLUMBING CHECK only, not a paper result.

Usage:
  python train_eval_classifier.py --synthetic normalized/all_synthetic_120.jsonl \
      --real normalized/real_organic.jsonl [--real-labels CSV] [--synthetic-labels CSV]
"""
import argparse
import csv
import json
import os
from collections import Counter

import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold, StratifiedKFold

from session_features import load_jsonl, normalize_cmd, session_tactics, template_key

LABELS = ["recon", "credential_access", "privilege_escalation", "persistence",
          "malware_drop", "resource_hijacking", "defense_evasion", "other"]
SEED = 42


def rule_label(s):
    t = session_tactics(s)
    if "resource_hijacking" in t:
        return "resource_hijacking"
    if "ingress_tool_transfer" in t:
        return "malware_drop"
    if "persistence" in t or "account_manipulation" in t:
        return "persistence"
    if "privilege_escalation" in t:
        return "privilege_escalation"
    if "credential_access" in t:
        return "credential_access"
    if "defense_evasion" in t:
        return "defense_evasion"
    if "discovery" in t:
        return "recon"
    return "other"


def load_labels(path):
    with open(path, encoding="utf-8-sig") as f:
        return {r["session_id"]: r["label"] for r in csv.DictReader(f)}


def text_of(sessions):
    return [" ".join(normalize_cmd(c) for c in s["commands"]) for s in sessions]


def numeric(sessions):
    rows = []
    for s in sessions:
        cmds = s["commands"]
        lens = [len(normalize_cmd(c)) for c in cmds]
        chained = [any(x in c for x in ("&&", ";", "|")) for c in cmds]
        rows.append([len(cmds), float(np.mean(lens)), float(np.mean(chained))])
    return np.array(rows)


def fit_predict(train, test, ytr):
    vec = TfidfVectorizer(token_pattern=r"[^\s]+", max_features=2000)
    Xtr = hstack([vec.fit_transform(text_of(train)), csr_matrix(numeric(train))]).tocsr()
    Xte = hstack([vec.transform(text_of(test)), csr_matrix(numeric(test))]).tocsr()
    clf = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                 random_state=SEED, n_jobs=-1)
    clf.fit(Xtr, ytr)
    return list(clf.predict(Xte))


def majority(ytr, n):
    return [Counter(ytr).most_common(1)[0][0]] * n


def row(qid, train, test, yt, yp, ym, ntr):
    # Average F1 over classes that occur in the test set only; otherwise a predicted
    # class with zero support adds a 0 to the mean and fakes a drop.
    present = sorted(set(yt))
    return {"id": qid, "train": train, "test": test,
            "macro_f1": float(f1_score(yt, yp, labels=present, average="macro", zero_division=0)),
            "accuracy": float(accuracy_score(yt, yp)),
            "predicted": dict(Counter(yp)),
            "majority_macro_f1": float(f1_score(yt, ym, labels=present, average="macro", zero_division=0)),
            "majority_accuracy": float(accuracy_score(yt, ym)),
            "n_train": int(ntr), "n_test": int(len(yt))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", required=True)
    ap.add_argument("--real", required=True)
    ap.add_argument("--real-labels")
    ap.add_argument("--synthetic-labels")
    ap.add_argument("--label-source", default="human",
                    help="Provenance name reported when label CSVs are given, e.g. 'llm-dual'.")
    ap.add_argument("--out-dir", default="results")
    a = ap.parse_args()

    syn = [s for s in load_jsonl(a.synthetic) if s.get("commands")]
    real = [s for s in load_jsonl(a.real) if s.get("commands")]
    for ss, path in ((syn, a.synthetic_labels), (real, a.real_labels)):
        hl = load_labels(path) if path else {}
        for s in ss:
            s["label"] = hl.get(s["session_id"]) or rule_label(s)
    src = a.label_source if (a.real_labels or a.synthetic_labels) else "rule"
    for s in real:
        s["tpl"] = template_key(s)
    ys = [s["label"] for s in syn]
    yr = [s["label"] for s in real]
    tpl_ids = {t: i for i, t in enumerate(dict.fromkeys(s["tpl"] for s in real))}
    groups = [tpl_ids[s["tpl"]] for s in real]
    print(f"synthetic n={len(syn)}, real n={len(real)}, templates={len(tpl_ids)}")

    # Q1
    k = max(2, min(5, min(Counter(ys).values())))
    yp, ym, yt = [], [], []
    for tr, te in StratifiedKFold(k, shuffle=True, random_state=SEED).split(syn, ys):
        ytr = [ys[i] for i in tr]
        yp += fit_predict([syn[i] for i in tr], [syn[i] for i in te], ytr)
        ym += majority(ytr, len(te))
        yt += [ys[i] for i in te]
    q1 = row("Q1", "synthetic", "synthetic", yt, yp, ym, len(syn) * (k - 1) // k)

    # Q2 / Q4 on identical template-grouped folds
    p2, p4, m2, yt2, ntr = [], [], [], [], []
    for tr, te in GroupKFold(5).split(real, yr, groups):
        a_ = [real[i] for i in tr]
        b_ = [real[i] for i in te]
        ytr = [yr[i] for i in tr]
        p2 += fit_predict(a_, b_, ytr)
        m2 += majority(ytr, len(te))
        p4 += fit_predict(a_ + syn, b_, ytr + ys)
        yt2 += [yr[i] for i in te]
        ntr.append(len(tr))
    n2 = int(np.mean(ntr))
    q2 = row("Q2", "real", "real", yt2, p2, m2, n2)
    q4 = row("Q4", "real+synthetic", "real", yt2, p4, m2, n2 + len(syn))

    # Q3
    p3 = fit_predict(syn, real, ys)
    m3 = majority(ys, len(real))
    q3 = row("Q3", "synthetic", "real", yr, p3, m3, len(syn))
    first = {}
    for i, s in enumerate(real):
        first.setdefault(s["tpl"], i)
    idx = list(first.values())
    q3d = row("Q3_dedup", "synthetic", "real_dedup", [yr[i] for i in idx],
              [p3[i] for i in idx], [m3[i] for i in idx], len(syn))
    f1c = f1_score(yr, p3, labels=LABELS, average=None, zero_division=0)
    q3pc = {l: float(f) for l, f in zip(LABELS, f1c)}

    dc = {"synthetic": Counter(ys), "real": Counter(yr),
          "real_dedup": Counter(yr[i] for i in idx)}
    dist = {d: {l: int(c.get(l, 0)) for l in LABELS} for d, c in dc.items()}
    quads = [q1, q2, q3, q3d, q4]
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "table3_transfer.json"), "w") as f:
        json.dump({"label_source": src, "label_distribution": dist, "quadrants": quads,
                   "q3_per_class_f1": q3pc}, f, indent=2)

    md = ["# Table 3: transfer between synthetic and real training data", ""]
    if src == "rule":
        md += ["> **PLUMBING CHECK - labels derived from same keywords as features.** Labels come "
               "from `rule_label()` (ATT&CK-tactic keyword rules in `session_features.py`), the "
               "same keywords that drive the TF-IDF features. These numbers are NOT a paper "
               "result; re-run with `--real-labels` / `--synthetic-labels` human labels.", ""]
    md += [f"Label source: **{src}**. Sessions with >=1 command only. TF-IDF (normalized "
           "commands) + 3 numeric features, RandomForest(300, balanced, seed 42). "
           f"Q1: stratified {k}-fold; Q2/Q4: GroupKFold(5) by command template; Q3_dedup: one "
           "session per template. CV metrics pooled over folds. Majority baseline predicts the "
           "training-set majority class.", "",
           "| Quadrant | Train | Test | n_train | n_test | Macro-F1 | Accuracy | "
           "Majority macro-F1 | Majority acc |",
           "|---|---|---|---|---|---|---|---|---|"]
    for q in quads:
        md.append(f"| {q['id']} | {q['train']} | {q['test']} | {q['n_train']} | {q['n_test']} | "
                  f"{q['macro_f1']:.3f} | {q['accuracy']:.3f} | {q['majority_macro_f1']:.3f} | "
                  f"{q['majority_accuracy']:.3f} |")
    md += ["", "## Label distribution", "",
           "| Label | Synthetic | Real (sessions) | Real (dedup templates) |", "|---|---|---|---|"]
    for l in LABELS:
        md.append(f"| {l} | {dist['synthetic'][l]} | {dist['real'][l]} | {dist['real_dedup'][l]} |")
    md.append("| **total** | " + " | ".join(str(sum(dist[d].values())) for d in dist) + " |")
    md += ["", "## Q3 per-class F1 (synthetic -> real, session-weighted)", "",
           "| Label | F1 |", "|---|---|"]
    md += [f"| {l} | {q3pc[l]:.3f} |" for l in LABELS]
    md += ["", "## Predicted label counts per quadrant", "",
           "| Quadrant | " + " | ".join(LABELS) + " |", "|---|" + "---|" * len(LABELS)]
    md += [f"| {q['id']} | " + " | ".join(str(q["predicted"].get(l, 0)) for l in LABELS) + " |"
           for q in quads]
    md += ["", "Macro-F1 averages only over classes present in the test set. Real labels are "
           f"broadcast from templates, so the effective real sample size is {len(idx)} templates."]
    with open(os.path.join(a.out_dir, "table3_transfer.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
```

