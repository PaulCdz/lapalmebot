import os
import discord
from dotenv import load_dotenv

from loltime import handle_loltime
from help import handle_help
from git_eta import handle_git_eta, get_repos, start_watcher

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} connecté !', flush=True)
    print("[Git-ETA] Surveillance démarrée.", flush=True)
    start_watcher(client)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await handle_loltime(message)
    await handle_git_eta(client, message)
    await handle_help(message)

client.run(DISCORD_TOKEN)
