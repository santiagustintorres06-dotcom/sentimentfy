"""
services/spotify_service.py — Busca canciones usando las playlists curadas de Sentimentfy.
"""

import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


def _get_client():
    credentials = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=credentials)


PLAYLISTS = {
    "chill":        "2SU8LmHm7PQA5bVeh02acF",
    "nostalgic":    "28z3JU7lOtrJfphkDJf1ra",
    "motivated":    "7HHXNKXVid1Qs8yYQT9tru",
    "happy":        "074qDJ7rg4u2jHOFRTNPys",
    "sad":          "1FG0U3HBiCwSw7AVzJC8Cq",
    "anti_anxious": "68l7UYuoc78xFxS1JgPvRN",
}

PLAYLIST_NAMES = {
    "sad":          "Sad Mood 😢",
    "anti_anxious": "Anti Anxious Mood 🌿",
    "happy":        "Happy Mood ☀️",
    "motivated":    "Motivated Mood 🔥",
    "nostalgic":    "Nostalgic Mood 🌙",
    "chill":        "Chill Mood 💙",
}

# ─── Normalización de emociones ───────────────────────────────────────────────
# Todos los sinónimos en inglés y español apuntan a una categoría base

EMOTION_NORMALIZER = {
    # TRISTEZA
    "sadness": "sad", "sad": "sad", "tristeza": "sad", "triste": "sad",
    "bajón": "sad", "bajon": "sad", "bajoneado": "sad", "melancholy": "sad",
    "melancolía": "sad", "melancolia": "sad", "heartbreak": "sad",
    "desamor": "sad", "grief": "sad", "duelo": "sad", "llorando": "sad",
    "crying": "sad", "depressed": "sad", "depresión": "sad", "depresion": "sad",
    "hopeless": "sad", "sin esperanza": "sad", "sorrow": "sad", "dolor": "sad",

    # ANSIEDAD
    "anxiety": "anti_anxious", "anxious": "anti_anxious", "ansiedad": "anti_anxious",
    "ansioso": "anti_anxious", "stress": "anti_anxious", "stressed": "anti_anxious",
    "estrés": "anti_anxious", "estres": "anti_anxious", "estresado": "anti_anxious",
    "nervioso": "anti_anxious", "nervous": "anti_anxious", "worry": "anti_anxious",
    "preocupado": "anti_anxious", "worried": "anti_anxious", "panic": "anti_anxious",
    "pánico": "anti_anxious", "panico": "anti_anxious", "overwhelmed": "anti_anxious",
    "abrumado": "anti_anxious", "fear": "anti_anxious", "miedo": "anti_anxious",

    # ENOJO
    "anger": "motivated", "angry": "motivated", "enojo": "motivated",
    "enojado": "motivated", "frustration": "motivated", "frustrado": "motivated",
    "frustrated": "motivated", "bronca": "motivated", "rage": "motivated",
    "rabia": "motivated", "irritado": "motivated", "irritated": "motivated",
    "molesto": "motivated", "annoyed": "motivated",

    # ALEGRÍA
    "joy": "happy", "happy": "happy", "alegría": "happy", "alegria": "happy",
    "alegre": "happy", "feliz": "happy", "excited": "happy", "emocionado": "happy",
    "contento": "happy", "content": "happy", "euphoria": "happy", "euforia": "happy",
    "great": "happy", "genial": "happy", "wonderful": "happy", "maravilloso": "happy",

    # MOTIVACIÓN
    "motivation": "motivated", "motivated": "motivated", "motivado": "motivated",
    "motivación": "motivated", "motivacion": "motivated", "energized": "motivated",
    "energético": "motivated", "energetico": "motivated", "pumped": "motivated",
    "focused": "motivated", "enfocado": "motivated", "determined": "motivated",
    "determinado": "motivated", "empowered": "motivated",

    # NOSTALGIA
    "nostalgia": "nostalgic", "nostalgic": "nostalgic", "nostálgico": "nostalgic",
    "nostalgico": "nostalgic", "extrañando": "nostalgic", "missing": "nostalgic",
    "añoranza": "nostalgic", "longing": "nostalgic", "bittersweet": "nostalgic",
    "agridulce": "nostalgic",

    # SOLEDAD
    "loneliness": "sad", "lonely": "sad", "soledad": "sad", "solo": "sad",
    "alone": "sad", "isolated": "sad", "aislado": "sad",

    # CANSANCIO / CHILL
    "exhaustion": "chill", "exhausted": "chill", "agotado": "chill",
    "agotamiento": "chill", "tired": "chill", "cansado": "chill",
    "cansancio": "chill", "burnt out": "chill", "quemado": "chill",
    "drained": "chill", "sin energía": "chill", "sin energia": "chill",
    "chill": "chill", "relaxed": "chill", "relajado": "chill",
    "calm": "chill", "tranquilo": "chill", "peaceful": "chill",
    "neutral": "chill", "apathy": "chill", "apatía": "chill", "apatia": "chill",
}

# ─── Tabla de decisión match/flip ─────────────────────────────────────────────

EMOTION_MAP = {
    "sad":          {"match": "sad",         "flip": "motivated"},
    "anti_anxious": {"match": "anti_anxious","flip": "chill"},
    "motivated":    {"match": "motivated",   "flip": "chill"},
    "happy":        {"match": "happy",       "flip": "chill"},
    "nostalgic":    {"match": "nostalgic",   "flip": "happy"},
    "chill":        {"match": "chill",       "flip": "motivated"},
}

# ─── Queries de búsqueda por mood y acción ────────────────────────────────────

SEARCH_QUERIES = {
    "sad": {
        "match": "sad heartbreak emotional indie folk Phoebe Bridgers Sufjan Stevens",
        "flip":  "uplifting happy feel good pop Bruno Mars Pharrell Williams",
    },
    "anti_anxious": {
        "match": "calm peaceful anxiety relief piano ambient",
        "flip":  "chill relaxing lofi bedroom pop",
    },
    "happy": {
        "match": "happy upbeat feel good pop Bruno Mars Harry Styles",
        "flip":  "chill relaxing mellow wind down music",
    },
    "motivated": {
        "match": "pump up energetic motivational hip hop Kendrick Lamar",
        "flip":  "chill calm wind down lofi music",
    },
    "nostalgic": {
        "match": "2010s throwback pop hits Katy Perry One Direction Adele",
        "flip":  "happy upbeat current pop hits",
    },
    "chill": {
        "match": "chill relaxing lofi bedroom pop Rex Orange County",
        "flip":  "energetic upbeat motivated pump up music",
    },
}


def _normalize_emotion(emotion: str) -> str:
    """Convierte cualquier variante de emoción a la categoría base."""
    cleaned = emotion.lower().strip()
    return EMOTION_NORMALIZER.get(cleaned, "chill")  # default: chill


def _get_playlist_key(emotion: str, match_mood: bool) -> str:
    base = _normalize_emotion(emotion)
    mapping = EMOTION_MAP.get(base, {"match": "chill", "flip": "happy"})
    return mapping["match"] if match_mood else mapping["flip"]


def _fetch_recommendations(emotion_data: dict, match_mood: bool) -> list[dict]:
    sp = _get_client()

    emotion = emotion_data.get("emotion", "neutral")
    playlist_key = _get_playlist_key(emotion, match_mood)

    print(f"DEBUG → emoción: '{emotion}' → normalizada: '{_normalize_emotion(emotion)}' → playlist: '{playlist_key}' → match: {match_mood}")

    query_set = SEARCH_QUERIES.get(playlist_key, SEARCH_QUERIES["chill"])
    query = query_set["match"] if match_mood else query_set["flip"]

    search_results = sp.search(q=query, type="track", limit=10)
    tracks = search_results.get("tracks", {}).get("items", [])

    if not tracks:
        return []

    selected = random.sample(tracks, min(5, len(tracks)))

    return [
        {
            "name": t["name"],
            "artist": t["artists"][0]["name"],
            "url": t["external_urls"]["spotify"],
            "playlist": PLAYLIST_NAMES[playlist_key],
        }
        for t in selected
    ]


async def get_recommendations(emotion_data: dict, match_mood: bool = True) -> list[dict]:
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_recommendations, emotion_data, match_mood)
