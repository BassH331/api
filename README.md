# ISDA Soil API Proxy (Vercel-ready)

This small project wraps the ISDA soil endpoints and exposes a single HTTP API that is Vercel-deployable.

Environment variables (required):
- `ISDA_USERNAME` - your ISDA API username (do not commit secrets into source control)
- `ISDA_PASSWORD` - your ISDA API password
- `ISDA_BASE_URL` - optional, defaults to `https://api.isda-africa.com`

Run locally:

```bash
python -m pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000
```

Example request once running locally:

```bash
curl "http://127.0.0.1:8000/soil?lat=-0.7196&lon=35.2400&depth=0-20&properties=ph,nitrogen_total"
```

Deploy to Vercel:

1. Add your environment variables in the Vercel dashboard (ISDA_USERNAME, ISDA_PASSWORD).
2. Push to a git branch connected to your Vercel project. Vercel will detect `vercel.json` and install dependencies from `requirements.txt` and expose `api/index.py` as a serverless function.
