"""
Sanitized placeholder for the original `main.py`.

The original file contained hard-coded credentials which have been removed for security.
Use the FastAPI server in `api/index.py` and set the required environment variables for credentials:

- ISDA_USERNAME
- ISDA_PASSWORD
- ISDA_BASE_URL (optional)

For local development copy `.env.example` to `.env` and fill in values.
"""

from pathlib import Path


def info():
    p = Path(__file__).absolute()
    print(f"This repository contains a Vercel-ready FastAPI handler at 'api/index.py'.")
    print(f"If you need the original ad-hoc script, check your backups — it contained secrets and must not be committed.")


if __name__ == "__main__":
    info()
