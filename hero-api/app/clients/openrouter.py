import os
import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterError(Exception):
    pass

async def generate_hero_post(name: str, stats: dict, model: str = "openai/gpt-4o-mini") -> str:
    if not OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    prompt = (
        f"Сделай короткий пост (2-4 предложения) о герое {name} по его характеристикам: "
        f"intelligence={stats.get('intelligence')}, strength={stats.get('strength')}, "
        f"speed={stats.get('speed')}, power={stats.get('power')}. Пиши дружелюбно и на русском."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Ты пишешь краткие посты о супергероях."},
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise OpenRouterError(f"Bad OpenRouter response: {data}") from exc


