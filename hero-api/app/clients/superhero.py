import os
from urllib.parse import quote
import httpx

TOKEN = os.getenv("SUPERHERO_TOKEN")

class SuperheroNotFound(Exception): ...

def _to_int(v) -> int | None:
    try:
        return int(v)
    except Exception:
        return None

async def fetch_powerstats_by_name(name: str) -> dict:
    if not TOKEN:
        raise RuntimeError("SUPERHERO_TOKEN is not set")

    url = f"https://superheroapi.com/api/{TOKEN}/search/{quote(name)}"
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    if data.get("response") != "success" or not data.get("results"):
        raise SuperheroNotFound(name)

    results = data["results"]
    match = next((x for x in results if (x.get("name") or "").lower() == name.lower()), results[0])

    ps = match.get("powerstats") or {}
    return {
        "name": match.get("name") or name,
        "intelligence": _to_int(ps.get("intelligence")),
        "strength": _to_int(ps.get("strength")),
        "speed": _to_int(ps.get("speed")),
        "power": _to_int(ps.get("power")),
    }


