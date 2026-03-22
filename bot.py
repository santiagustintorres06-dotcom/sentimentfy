"""
bot.py — Punto de entrada de Sentimentfy.

Acá se inicializa el bot de Discord y se cargan
todos los comandos (llamados 'cogs' en discord.py).
"""

import discord
from discord.ext import commands
import logging
from config import DISCORD_TOKEN

# Logging: nos muestra en consola todo lo que hace el bot
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Intents: le decimos a Discord qué permisos necesita el bot.
# Message content = leer mensajes
# DMs = hablar en privado con usuarios
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

# Creamos el bot. El prefix "!" es para comandos tipo !help,
# pero Sentimentfy usa slash commands (/)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Se ejecuta cuando el bot se conecta exitosamente a Discord."""
    await bot.load_extension("cogs.sentimentfy")  # Cargamos los comandos
    await bot.tree.sync()  # Sincronizamos los slash commands con Discord
    print(f"✅ Sentimentfy está online como {bot.user}")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
