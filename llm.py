import os
import json
import time
import requests
from google import genai
from google.genai import types

_client = None
_use_thinking_level = True
_used_up = set()


def client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")
        _client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=120000))
    return _client


def model_name():
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()


def models():
    backups = os.getenv("GEMINI_BACKUP_MODELS", "gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite")
    out = [model_name()]
    for m in backups.split(","):
        m = m.strip()
        if m and m not in out and m not in _used_up:
            out.append(m)
    return [m for m in out if m not in _used_up] or out


def busy(error):
    text = str(error)
    return any(code in text for code in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded", "high demand"))


def clean(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()


def config(as_json):
    settings = {
        "temperature": 0.3,
        "response_mime_type": "application/json" if as_json else "text/plain",
    }
    if _use_thinking_level:
        settings["thinking_config"] = types.ThinkingConfig(thinking_level="LOW")
    return types.GenerateContentConfig(**settings)


def ask_groq(prompt, as_json):
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("no GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "reasoning_effort": "low",
        "include_reasoning": False,
    }
    if as_json:
        body["response_format"] = {"type": "json_object"}
    start = time.time()
    print(f"[groq] {model} call", flush=True)
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json=body,
        timeout=120,
    )
    if res.status_code != 200:
        raise RuntimeError(f"Groq error {res.status_code}: {res.text[:200]}")
    text = clean(res.json()["choices"][0]["message"]["content"] or "")
    print(f"[groq] answered in {time.time() - start:.1f}s", flush=True)
    return json.loads(text) if as_json else text


def ask(prompt, as_json=False, tries=2, rounds=3):
    if os.getenv("PRIMARY_AI", "gemini").strip().lower() == "groq" and os.getenv("GROQ_API_KEY", "").strip():
        try:
            return ask_groq(prompt, as_json)
        except Exception as e:
            print(f"[groq] failed: {str(e)[:200]}, trying Gemini", flush=True)
            return ask_gemini(prompt, as_json, tries, 1)
    try:
        return ask_gemini(prompt, as_json, tries, 1 if os.getenv("GROQ_API_KEY", "").strip() else rounds)
    except Exception as gemini_error:
        if not os.getenv("GROQ_API_KEY", "").strip():
            raise
        print("[llm] Gemini unavailable, switching to Groq", flush=True)
        try:
            return ask_groq(prompt, as_json)
        except Exception as e:
            print(f"[groq] failed: {str(e)[:200]}", flush=True)
            try:
                return ask_groq(prompt, as_json)
            except Exception as e2:
                raise RuntimeError(f"Both Gemini and Groq failed. Gemini: {str(gemini_error)[:150]} Groq: {str(e2)[:150]}")


def ask_gemini(prompt, as_json=False, tries=2, rounds=3):
    global _use_thinking_level
    c = client()
    last = None
    for round_no in range(1, rounds + 1):
        for model in models():
            attempt = 0
            while attempt < tries:
                attempt += 1
                start = time.time()
                print(f"[gemini] {model}, try {attempt}", flush=True)
                try:
                    res = c.models.generate_content(model=model, contents=prompt, config=config(as_json))
                    text = clean(res.text or "")
                    print(f"[gemini] {model} answered in {time.time() - start:.1f}s", flush=True)
                    if not text:
                        raise RuntimeError("The model returned an empty answer.")
                    return json.loads(text) if as_json else text
                except Exception as e:
                    last = e
                    print(f"[gemini] {model} failed after {time.time() - start:.1f}s: {str(e)[:120]}", flush=True)
                    if _use_thinking_level and "thinking" in str(e).lower():
                        _use_thinking_level = False
                        attempt -= 1
                        continue
                    if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                        _used_up.add(model)
                    if busy(e):
                        break
                    time.sleep(5)
        if not busy(last) or round_no == rounds:
            break
        pause = 20 * round_no
        print(f"[gemini] all models busy, waiting {pause}s before trying again", flush=True)
        time.sleep(pause)
    if busy(last):
        raise RuntimeError("Every Gemini model is busy or has used its free daily limit. Wait a minute and click again.")
    raise RuntimeError(f"Gemini failed: {str(last)[:300]}")
