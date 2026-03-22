"""
config.py — Configuración central del proyecto.

"""

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

required = {
    "DISCORD_TOKEN": DISCORD_TOKEN,
    "SPOTIFY_CLIENT_ID": SPOTIFY_CLIENT_ID,
    "SPOTIFY_CLIENT_SECRET": SPOTIFY_CLIENT_SECRET,
    "GROQ_API_KEY": GROQ_API_KEY,
}

for name, value in required.items():
    if not value:
        raise ValueError(f"❌ Falta la variable de entorno: {name}. Revisá tu archivo .env")
