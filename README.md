# 🎵 Sentimentfy

Bot de Discord que te escucha, te acompaña emocionalmente y te recomienda música según cómo te sentís.

## ¿Qué hace?

1. El usuario usa `/sentimentfy` en cualquier servidor
2. El bot abre un **DM privado**
3. El usuario elige idioma (Español / English)
4. Sentimentfy **escucha y acompaña** con empatía
5. Sugiere **técnicas concretas** (respiración, grounding, mindfulness)
6. Pregunta si quiere música para **acompañar** su mood o para **cambiarlo**
7. Recomienda canciones reales de Spotify con links directos

## Tecnologías

- **Python 3.10+**
- **discord.py** — Interfaz con Discord
- **Anthropic Claude API** — Inteligencia emocional y empatía
- **Spotify Web API** — Recomendaciones musicales reales
- **pytest** — Testing

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/sentimentfy.git
cd sentimentfy
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar credenciales
```bash
cp .env.example .env
```
Completá el `.env` con tus tokens:
- **Discord**: [discord.com/developers](https://discord.com/developers) → New App → Bot → Reset Token
- **Spotify**: [developer.spotify.com](https://developer.spotify.com) → Create App
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com) → API Keys

### 4. Correr el bot
```bash
python bot.py
```

## Tests
```bash
pytest tests/ -v
```

## Estructura
```
sentimentfy/
├── bot.py                    # Punto de entrada
├── config.py                 # Variables de entorno
├── cogs/
│   └── sentimentfy.py        # Comandos y flujo de conversación
├── services/
│   ├── claude_service.py     # Inteligencia emocional con Claude
│   └── spotify_service.py    # Recomendaciones de Spotify
├── tests/
│   └── test_services.py      # Tests unitarios
├── .env.example
├── .gitignore
└── requirements.txt
```

## ⚠️ Disclaimer
Sentimentfy no reemplaza la atención de un profesional de salud mental.
Si estás en crisis, comunicate con una línea de ayuda profesional.
- 🇦🇷 Argentina: **135** (Centro de Asistencia al Suicida, gratuito 24hs)
- 🌎 Internacional: [findahelpline.com](https://findahelpline.com)

## Autor
Tu nombre — [GitHub](https://github.com/tu-usuario)
