"""
cogs/sentimentfy.py — El corazón del bot.

"""

import discord
from discord.ext import commands
from discord import app_commands
from services.claude_service import chat_with_sentiment
from services.spotify_service import get_recommendations

active_sessions = {}


# ─── Botones de selección de idioma ──────────────────────────────────────────

class LanguageView(discord.ui.View):

    def __init__(self, user_id: int):
        super().__init__(timeout=60)  # Los botones desaparecen en 60 segundos
        self.user_id = user_id

    @discord.ui.button(label="Español 🇦🇷", style=discord.ButtonStyle.primary)
    async def spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._start_session(interaction, "es")

    @discord.ui.button(label="English 🇺🇸", style=discord.ButtonStyle.secondary)
    async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._start_session(interaction, "en")

    async def _start_session(self, interaction: discord.Interaction, language: str):
        """Inicializa la sesión del usuario con el idioma elegido."""
        active_sessions[self.user_id] = {
            "language": language,
            "history": [],  
            "stage": "chatting"  # Etapas: chatting → music_choice → done
        }

        self.stop()  # Desactivamos los botones

        if language == "es":
            msg = (
                "¡Hola! Soy Sentimentfy 🎵\n\n"
                "Estoy acá para escucharte. Podés contarme cómo te sentís, "
                "qué está pasando, o simplemente desahogarte.\n\n"
                "Todo lo que me cuentes es privado. ¿Cómo estás hoy? 💙"
            )
        else:
            msg = (
                "Hey! I'm Sentimentfy 🎵\n\n"
                "I'm here to listen. You can tell me how you're feeling, "
                "what's going on, or just vent.\n\n"
                "Everything you share here is private. How are you doing today? 💙"
            )

        await interaction.response.edit_message(content=msg, view=None)


# ─── Botones de elección musical ─────────────────────────────────────────────

class MusicChoiceView(discord.ui.View):
    """
    Muestra dos opciones de música:
    - Música que acompaña el estado de ánimo actual
    - Música para cambiar/mejorar el estado de ánimo
    """

    def __init__(self, user_id: int, emotion_data: dict):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.emotion_data = emotion_data
        language = active_sessions.get(user_id, {}).get("language", "es")
        self.language = language

    @discord.ui.button(label="🎵 Música para acompañarme", style=discord.ButtonStyle.secondary)
    async def match_mood(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._get_music(interaction, match=True)

    @discord.ui.button(label="✨ Música para cambiar mi mood", style=discord.ButtonStyle.success)
    async def change_mood(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._get_music(interaction, match=False)

    async def _get_music(self, interaction: discord.Interaction, match: bool):
        self.stop()
        lang = self.language

        thinking = "🔍 Buscando canciones..." if lang == "es" else "🔍 Finding songs..."
        await interaction.response.edit_message(content=thinking, view=None)

        try:
            print(f"DEBUG emotion_data: {self.emotion_data}")
            tracks = await get_recommendations(self.emotion_data, match_mood=match)
        except Exception as e:
            msg = "⚠️ Hubo un error buscando canciones. Intentá de nuevo." if lang == "es" else "⚠️ Error finding songs. Try again."
            await interaction.edit_original_response(content=msg)
            return

        if not tracks:
            msg = "😕 No encontré canciones. Intentá de nuevo." if lang == "es" else "😕 Couldn't find songs. Try again."
            await interaction.edit_original_response(content=msg)
            return

        playlist_name = tracks[0].get("playlist", "")

        if lang == "es":
            header = f"🎶 *{playlist_name}* — música para acompañarte:" if match else f"🌟 *{playlist_name}* — música para cambiar tu energía:"
        else:
            header = f"🎶 *{playlist_name}* — music to be with you:" if match else f"🌟 *{playlist_name}* — music to shift your energy:"

        response = f"{header}\n\n"
        for i, track in enumerate(tracks, 1):
            response += f"{i}. **{track['name']}** — {track['artist']}\n🔗 {track['url']}\n\n"

        footer = "Espero que te haga bien 💙 Cuando quieras volver a hablar, usá `/sentimentfy`." if lang == "es" \
            else "Hope this helps 💙 Whenever you want to talk again, use `/sentimentfy`."
        response += footer

        active_sessions.pop(self.user_id, None)  # Limpiamos la sesión
        await interaction.edit_original_response(content=response)


# ─── Cog principal ────────────────────────────────────────────────────────────

class SentimentfyCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sentimentfy", description="Talk to Sentimentfy about how you feel 🎵")
    async def sentimentfy(self, interaction: discord.Interaction):
        """
        Slash command /sentimentfy — punto de entrada del bot.
        Manda un DM al usuario y arranca la conversación.
        """
        user = interaction.user

        # Le respondemos en el servidor para no dejar la interacción colgada
        await interaction.response.send_message(
            "📩 Te mandé un mensaje privado. ¡Hablamos ahí! / I sent you a DM. Let's talk there!",
            ephemeral=True  # Solo lo ve el usuario que usó el comando
        )

        # Abrimos el DM y mandamos la selección de idioma
        try:
            dm = await user.create_dm()
            await dm.send(
                "👋 **Welcome to Sentimentfy** / **Bienvenido a Sentimentfy**\n\nChoose your language / Elegí tu idioma:",
                view=LanguageView(user.id)
            )
        except discord.Forbidden:
            # Si el usuario tiene los DMs desactivados
            await interaction.followup.send(
                "⚠️ No pude mandarte un DM. Habilitá los mensajes privados en tu configuración de Discord.",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Escucha todos los mensajes privados (DMs) que recibe el bot.
        Si el usuario tiene una sesión activa, procesa su mensaje con Claude.
        """
        # Ignoramos mensajes del propio bot y mensajes en servidores (no DMs)
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.DMChannel):
            return

        user_id = message.author.id
        session = active_sessions.get(user_id)

        # Si no hay sesión activa, le recordamos cómo empezar
        if not session:
            await message.channel.send(
                "Usá `/sentimentfy` en un servidor para empezar una nueva conversación 🎵\n"
                "Use `/sentimentfy` in a server to start a new conversation 🎵"
            )
            return

        if session["stage"] != "chatting":
            return

        # Procesamos el mensaje con Claude
        async with message.channel.typing():  # Muestra "escribiendo..." mientras Claude responde
            result = await chat_with_sentiment(
                user_message=message.content,
                history=session["history"],
                language=session["language"]
            )

        # Actualizamos el historial con el mensaje del usuario y la respuesta
        session["history"].append({"role": "user", "content": message.content})
        session["history"].append({"role": "assistant", "content": result["response"]})

        await message.channel.send(result["response"])

        # Si Claude indica que es momento de ofrecer música
        if result.get("offer_music"):
            session["stage"] = "music_choice"
            lang = session["language"]

            music_prompt = (
                "¿Querés que te recomiende música? 🎵"
                if lang == "es" else
                "Would you like me to recommend some music? 🎵"
            )

            await message.channel.send(
                music_prompt,
                view=MusicChoiceView(user_id, result["emotion_data"])
            )


async def setup(bot):
    """discord.py llama a esta función para cargar el cog."""
    await bot.add_cog(SentimentfyCog(bot))
