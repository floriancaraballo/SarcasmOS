import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configuración propia
from config import PREFIX

# Cargar variables de entorno (.env)
#load_dotenv()
#TOKEN = os.getenv("DISCORD_TOKEN")

TOKEN = os.getenv("DISCORD_TOKEN")

#if TOKEN is None:
    #raise ValueError("❌ No se ha encontrado DISCORD_TOKEN en el archivo .env")
if not TOKEN:
    raise ValueError("❌ No se ha encontrado DISCORD_TOKEN. Añádelo como variable de entorno en Railway")
# Intents (permisos del bot)
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Evento: bot listo
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")

# Cargar cogs automáticamente
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

# Hook de inicio (forma moderna y correcta)
@bot.event
async def setup_hook():
    await load_cogs()

# Arrancar el bot
bot.run(TOKEN)
