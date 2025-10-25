import os
import time
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # load .env in local development if present
except Exception:
    # python-dotenv not installed in this environment; skip loading .env
    pass

try:
    from fastapi import FastAPI, HTTPException, Query
    _HAS_FASTAPI = True
except Exception:
    # allow module import in environments where fastapi isn't installed (tests or linting)
    FastAPI = None
    HTTPException = Exception
    def Query(*args, **kwargs):
        return None
    _HAS_FASTAPI = False

if _HAS_FASTAPI:
    app = FastAPI(title="ISDA Soil API Proxy")
else:
    # lightweight placeholder so tests that import the module can access `app`
    class _PlaceholderApp:
        pass

    app = _PlaceholderApp()

BASE_URL = os.getenv("ISDA_BASE_URL", "https://api.isda-africa.com")
# default token TTL (seconds) used for local in-memory caching; upstream token ~60min
TOKEN_TTL = int(os.getenv("ISDA_TOKEN_TTL_SECONDS", str(3500)))

# Simple in-memory token cache for serverless cold-starts in the same container
_token_cache = {"token": None, "expires_at": 0}


async def _login(client, username: str, password: str) -> str:
    payload = {"username": username, "password": password}
    r = await client.post(f"{BASE_URL}/login", data=payload, timeout=10.0)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Login to upstream API failed")
    token = r.json().get("access_token")
    if not token:
        raise HTTPException(status_code=502, detail="No access token returned from upstream API")
    return token


async def _get_token(client, username: str, password: str) -> str:
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now:
        return _token_cache["token"]
    token = await _login(client, username, password)
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + TOKEN_TTL
    return token


async def fetch_property(client, token: str, lat: float, lon: float, prop: str, depth: str):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"lat": lat, "lon": lon, "property": prop, "depth": depth}
    r = await client.get(f"{BASE_URL}/isdasoil/v2/soilproperty", headers=headers, params=params, timeout=10.0)
    if r.status_code != 200:
        return {"error": f"upstream returned status {r.status_code}", "raw_text": r.text}
    return r.json()


async def soil_properties(
    lat: float,
    lon: float,
    depth: str = "0-20",
    properties: Optional[List[str]] = Query(None, description="Comma separated list of properties to fetch."),
):
    """Fetch one or more soil properties from the ISDA upstream API and return a combined JSON result.

    Required environment variables (for deployment):
    - ISDA_USERNAME
    - ISDA_PASSWORD
    - ISDA_BASE_URL (optional)
    """

    username = os.getenv("ISDA_USERNAME")
    password = os.getenv("ISDA_PASSWORD")
    if not username or not password:
        raise HTTPException(status_code=400, detail="ISDA_USERNAME and ISDA_PASSWORD environment variables are required")
git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
    default_props = [
        "ph",
        "aluminium_extractable",
        "nitrogen_total",
        "phosphorous_extractable",
        "potassium_extractable",
        "magnesium_extractable",
        "iron_extractable",
        "calcium_extractable",
        "zinc_extractable",
        "sulphur_extractable",
        "carbon_total",
        "carbon_organic",
        "bulk_density",
        "stone_content",
        "silt_content",
        "clay_content",
        "sand_content",
        "texture_class",
    ]

    props = properties or default_props

    # import httpx only when the endpoint is actually called (avoids import-time dependency during tests)
    import httpx

    async with httpx.AsyncClient() as client:
        token = await _get_token(client, username, password)

        results = {}
        # fetch properties sequentially to avoid hammering upstream login limits; can be parallelized if needed
        for p in props:
            data = await fetch_property(client, token, lat, lon, p, depth)
            try:
                prop_obj = data.get("property", {}).get(p)
                if prop_obj and isinstance(prop_obj, list) and len(prop_obj) > 0:
                    value = prop_obj[0].get("value", {}).get("value")
                    uncertainty = prop_obj[0].get("uncertainty")
                    results[p] = {"value": value, "uncertainty": uncertainty}
                else:
                    results[p] = {"raw": data}
            except Exception:
                results[p] = {"raw": data}

    return {"lat": lat, "lon": lon, "depth": depth, "properties": results}


if _HAS_FASTAPI:
    # register the path operation only when FastAPI is available
    app.get("/soil")(soil_properties)
