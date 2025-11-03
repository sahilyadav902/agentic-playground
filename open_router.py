from dotenv import load_dotenv
import os
from openai import OpenAI
import httpx
from datetime import datetime
import json

# -------------------------
# 1. Setup
# -------------------------
load_dotenv()
open_router_api_key = os.environ.get("OPEN_ROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=open_router_api_key,
    http_client=httpx.Client(verify=False)
)

# -------------------------
# 2. Define conversation
# -------------------------
model_name = "meta-llama/llama-3.3-8b-instruct:free"

messages = [
    # {"role": "system", "content": "You are a wise philosopher assistant."},
    # {"role": "user", "content": "What is the meaning of life?"},
    {"role": "user", "content": "Write a Python function that checks if a number is a palindrome. Then explain the logic briefly."}
]

# -------------------------
# 3. Make API call
# -------------------------
completion = client.chat.completions.create(
    model=model_name,
    messages=messages,
    # response_format={"type": "json_object"}
)

# Extract just the final response text
response_text = completion.choices[0].message.content
print("Model Response:\n", response_text)

# -------------------------
# 4. Build log entry
# -------------------------
safe_model_name = model_name.replace("/", "_").replace(":", "_")
log_filename = f"llm_log_{safe_model_name}.jsonl"

log_entry = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "model": model_name,
    # Store full message list (system, user, assistant)
    "messages": messages,
    # Store extracted assistant reply for quick viewing
    "assistant_response": response_text,
    # Store the entire raw API response for inspection/debugging
    "full_response": completion.model_dump()  # serialize the entire OpenAI response object
}

# -------------------------
# 5. Save to log file (append mode)
# -------------------------
os.makedirs("logs", exist_ok=True)
file_path = os.path.join("logs", log_filename)

with open(file_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

print(f"\n✅ Full response logged to: {file_path}")
