import subprocess
import json
import os

OLLAMA_PATH = r"C:\Users\arman\AppData\Local\Programs\Ollama\ollama.exe"
MEMORY_FILE = "user_memory.json"


def load_user_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_user_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def handle_memory_command(question: str) -> str | None:
    memory = load_user_memory()
    q = question.lower()
    updated = False
    responses = []

    if "remember" in q and ("my name is" in q or "i am" in q):
        if "my name is" in q:
            name = question.split("my name is")[-1].strip()
        else:
            name = question.split("i am")[-1].replace("remember me", "").strip()

        if name:
            memory["name"] = name
            updated = True
            responses.append(f"I’ll remember your name is {name}.")

    if "call me" in q:
        name = question.split("call me")[-1].strip()
        if name:
            memory["name"] = name
            updated = True
            responses.append(f"I’ll call you {name}.")

    if "remember" in q and ("flirty" in q or "friendly" in q):
        memory["tone"] = "flirty"
        updated = True
        responses.append("I’ll keep a friendly tone.")

    if "forget my name" in q:
        memory.pop("name", None)
        updated = True
        responses.append("I’ve forgotten your name.")

    if "forget memory" in q:
        memory.clear()
        updated = True
        responses.append("All personal memory cleared.")

    if updated:
        save_user_memory(memory)
        return " ".join(responses)

    return None


def ask_llm(context: str, question: str, history: list[dict]) -> str:
    user_memory = load_user_memory()

    name = user_memory.get("name")
    tone = user_memory.get("tone", "neutral")

    memory_block = ""
    if name:
        memory_block += f"The user's name is {name}.\n"
    if tone == "flirty":
        memory_block += "Use a light, friendly tone.\n"

    conversation = ""
    for msg in history[-6:]:
        conversation += f"{msg['role'].capitalize()}: {msg['content']}\n"

    prompt = f"""
You are an AI assistant.

Rules:
- Use the document context strictly.
- If information is missing, say you don't know.
- Do not hallucinate.

{memory_block}

Conversation so far:
{conversation}

Document Context:
{context}

User Question:
{question}
"""
    print("LLM PROMPT SIZE:", len(prompt))

    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", "mistral"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:
            return "LLM error."

        output = result.stdout.strip()
        return output if output else "I couldn’t find that information in the document."

    except Exception:
        return "LLM error."

import subprocess

def stream_llm(prompt: str):
    process = subprocess.Popen(
        ["ollama", "run", "mistral"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    process.stdin.write(prompt)
    process.stdin.close()

    for line in process.stdout:
        yield line