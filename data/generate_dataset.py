import os, json, time, hashlib
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

# 1.  ENV + client ----------------------------------------------------
load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "google/gemini-2.5-flash-preview"      # or gemini-flash-2.0

# 2.  PROMPTS ---------------------------------------------------------
SYSTEM_MSG = """You are a data generator for training a voice-assistant NLU model.
Output exactly ONE compact JSON object per reply, no markdown, no prose."""
USER_TEMPLATE = """
Return ONE example following:
{{"input":"natural user request",
  "output":{{"intent":"<add_task|get_weather|send_email>",
             "task":"", "schedule":"", "location":"", "datetime":"",
             "recipient":"", "subject":"", "body":""}}}}
Guidelines:
• vary phrasing 
• mix relative and absolute times
• email bodies ≤ 60 words
• no duplicates
Generate now."""

SEED_EMAIL = {
    "input": "Email Tom at tom.fox@gmail.com – subject 'Slides', body 'Hi Tom, slides attached.'",
    "output": {
        "intent": "send_email",
        "recipient": "tom.fox@gmail.com",
        "subject": "Slides",
        "body": "Hi Tom, slides attached."
    }
}

SEED_WEATHER = {
    "input": "Will it rain in Manchester this weekend?",
    "output": {
        "intent": "get_weather",
        "location": "Manchester",
        "datetime": "this weekend"
    }
}

SEED_TASK = {
    "input": "Remind me to water the plants at 7 pm",
    "output": {
        "intent": "add_task",
        "task": "water the plants",
        "schedule": "today 19:00"
    }
}

INTENTS = ["add_task", "get_weather", "send_email"]

def generate_user_prompt(intent: str) -> str:
    return f"""
Generate ONE *new* example, following the same JSON schema, with the intent: **{intent}**

Rules:
• Vary phrasing
• The user input should be given in speech to text format.
• Mix relative (‘tomorrow’, ‘next Friday’) and absolute times (‘2025-06-03 14:30’).
• For send_email: always include recipient, subject, body (≤ 40 words).
• For add_task: include both task and schedule.
• For get_weather: include location (or ‘current_location’) and datetime.
Return only the JSON object—no extra text.
"""

# 3.  GENERATOR -------------------------------------------------------
def ask_model(intent: str):
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=1.0,
        top_p=0.95,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "assistant", "content": json.dumps(SEED_EMAIL)},
            {"role": "assistant", "content": json.dumps(SEED_WEATHER)},
            {"role": "assistant", "content": json.dumps(SEED_TASK)},
            {"role": "user", "content": generate_user_prompt(intent)},
        ]
    )
    return resp.choices[0].message.content.strip()

def normalise(js):
    """Remove whitespace keys with empty strings."""
    js["output"] = {k:v for k,v in js["output"].items() if v}
    return js

def main(n=100, batch_size=10, outfile="data/task_dataset.jsonl"):
    os.makedirs("data", exist_ok=True)
    seen, idx = set(), 0
    print(f"Generating {n} examples")
    print(f"Batch size: {batch_size}")

    # Resume support: load already-generated examples if file exists
    if os.path.exists(outfile):
        with open(outfile, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    key = hashlib.sha1(data["input"].encode()).hexdigest()
                    seen.add(key)
                except Exception:
                    continue
        print(f"Resuming from {len(seen)} existing examples.")

    while len(seen) < n:
        batch_target = min(batch_size, n - len(seen))
        with open(outfile, "a") as f:
            batch_start = len(seen)
            while len(seen) < batch_start + batch_target:

                target = INTENTS[idx % len(INTENTS)]
                idx += 1
                try:
                    raw = ask_model(target)
                    data = json.loads(raw)
                    key = hashlib.sha1(data["input"].encode()).hexdigest()
                    if key in seen:
                        continue
                    seen.add(key)
                    data = normalise(data)
                    f.write(json.dumps(data) + "\n")
                except RateLimitError as e:
                    wait = random.uniform(10, 20)
                    print(f"Rate limit hit. Waiting {wait:.1f} seconds...")
                    time.sleep(wait)
                except Exception as e:
                    print("skip:", e)
                    time.sleep(1)
            print(f"Checkpoint: {len(seen)} examples written.")
            resp = input("Continue to next batch? (y/n): ").strip().lower()
            if resp not in ("y", "yes", ""):
                print("Exiting at user request.")
                return

if __name__ == "__main__":
    main(n=1200, batch_size=100)
