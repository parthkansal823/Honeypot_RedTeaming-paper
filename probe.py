import os, requests
k = os.environ["BEDROCK_API_KEY"]
for m in ["openai.gpt-oss-20b", "openai.gpt-oss-120b", "google.gemma-3-4b-it", "qwen.qwen3-32b", "deepseek.v3.2", "anthropic.claude-haiku-4-5"]:
    r = requests.post("https://bedrock-mantle.us-east-1.api.aws/v1/chat/completions",
        headers={"Authorization": "Bearer " + k},
        json={"model": m, "messages": [{"role": "user", "content": "Say hello"}]})
    print(m, r.status_code, r.text[:150])