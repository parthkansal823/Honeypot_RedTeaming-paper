# 3 Installation and Setup

## 3.1 Requirements

Table: Software requirements. {#tab:doc-req widths=4,3,9}

| Requirement | Version | Needed for |
|---|---|---|
| Python | 3.11 | Everything |
| pip packages | `requirements.txt` | paramiko, boto3, anthropic, openai, requests, scikit-learn, scipy, numpy, pandas |
| Git | any | Getting the code |
| Docker Desktop | any recent | Running the honeypot (optional for analysis only) |
| Microsoft Word | 365 / 2019+ | Building the report (optional) |
| matplotlib, python-docx | recent | Building the report figures and the Word file (optional) |

## 3.2 Steps

```powershell
git clone https://github.com/parthkansal823/Honeypot_RedTeaming-paper.git
cd Honeypot_RedTeaming-paper
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3.3 The real dataset

Download `cyberlab_2019-11-15.json.gz` from Zenodo (DOI 10.5281/zenodo.3687527) into the project root and extract it so that `cyberlab_2019-11-15.json/cowrie_2019-11-15.json` exists. The file is about 600 MB uncompressed; the parser streams it, so a normal laptop is enough.

## 3.4 API keys

Keys are read from environment variables and are never stored in files:

Table: Environment variables. {#tab:doc-env widths=5,11}

| Variable | Used by |
|---|---|
| `BEDROCK_API_KEY` | Attacker models and the Qwen3-32B honeypot backend through the OpenAI-compatible Bedrock endpoint |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | Optional alternative providers |

You only need keys to generate *new* synthetic sessions. The 120 sessions used in the study are already in `logs/`.

## 3.5 Checking the installation

```powershell
python -c "import paramiko, sklearn, scipy, numpy; print('ok')"
python domain_shift.py      # should print the label-free tables
```
