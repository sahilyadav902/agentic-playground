import os
import subprocess
import datetime
import psutil
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
open_router_api_key = os.environ.get('OPEN_ROUTER_API_KEY')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=open_router_api_key,
    http_client=httpx.Client(verify=False)
)

# --- Basic action functions ---
def open_app(app_name):
    app_map = {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe"
    }
    if app_name.lower() in app_map:
        subprocess.Popen(app_map[app_name.lower()])
        return f"Opening {app_name}..."
    else:
        return f"I don’t know how to open {app_name} yet."

def get_system_info():
    battery = psutil.sensors_battery()
    return f"Battery: {battery.percent}% | Plugged in: {battery.power_plugged}"

def get_time():
    return datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

# --- LLM call ---
def ask_llm(prompt):
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[
            {"role": "system", "content": "You are a helpful Windows desktop assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# --- Intent recognition via LLM ---
def parse_intent(user_input):
    system_prompt = """
    You are an intent classifier for a Windows assistant.
    Given a user command, return one of:
    ["open_app", "get_time", "get_system_info", "chat"]
    If 'open_app', also include the app name.
    Respond in JSON only.
    """
    resp = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return resp.choices[0].message.content

# --- Main loop ---
def run_agent():
    print("🤖 AI Assistant ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        intent_json = parse_intent(user_input)
        print(f"[DEBUG] Intent: {intent_json}")

        if "open_app" in intent_json:
            app_name = None
            for a in ["chrome", "notepad", "calculator", "explorer"]:
                if a in user_input.lower():
                    app_name = a
            if app_name:
                print(open_app(app_name))
            else:
                print("I couldn’t identify the app.")
        elif "get_time" in intent_json:
            print(get_time())
        elif "get_system_info" in intent_json:
            print(get_system_info())
        else:
            print(ask_llm(user_input))

if __name__ == "__main__":
    run_agent()
