import os
import discord
import requests
from datetime import datetime
from dotenv import load_dotenv
import pytz

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_timezone_from_region(region: str):
    tz_map = {
        "europe": "Europe/Paris",        # EUW, EUNE
        "americas": "America/New_York",  # NA, LAN
        "asia": "Asia/Seoul",            # KR, JP
    }
    return pytz.timezone(tz_map.get(region, "UTC"))


def get_today_play_time(summoner_name: str, tag: str, region: str):
    # 1. Get summoner PUUID
    account_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    res = requests.get(account_url, headers=headers).json()
    print("Réponse de l'API Account:", res)

    if "puuid" not in res:
        raise ValueError("PUUID introuvable")

    puuid = res['puuid']

    # 2. Get today's matches
    tz = get_timezone_from_region(region)
    now = datetime.now(tz)
    start_of_day = int(datetime(now.year, now.month, now.day, tzinfo=tz).timestamp())

    match_region_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "startTime": start_of_day,
        "start": 0,
        "count": 20
    }
    match_ids = requests.get(match_region_url, headers=headers, params=params).json()

    total_minutes = 0
    for match_id in match_ids:
        match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        match_data = requests.get(match_url, headers=headers).json()
        duration = match_data['info']['gameDuration']
        total_minutes += duration / 60

    return round(total_minutes), len(match_ids)

@client.event
async def on_ready():
    print(f'{client.user} connecté !')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('loltime'):
        print(f"Commande reçue de {message.author.name} dans {message.channel.name}")
        try:
            args = message.content.split()

            # Commande : loltime -help
            if len(args) > 1 and args[1] == "-help":
                help_msg = (
                    "**Commandes disponibles :**\n"
                    "`loltime` : Affiche le temps de jeu de Sheep Vibes#WOLF (défaut)\n"
                    "`loltime -help` : Affiche ce message d’aide\n"
                    "`loltime <RÉGION> <Nom#Tag>` : Affiche le temps de jeu du joueur donné\n"
                    "Ex : `loltime EUW ViennoiseChoco#EUW`, `loltime NA Sheep Vibes#WOLF`\n"
                )
                await message.channel.send(help_msg)
                return

            thinking_msg = await message.channel.send("⏳ Récupération du temps de jeu...")

            # Commande : loltime (par défaut)
            if len(args) == 1:
                summoner_name = "Sheep Vibes"
                tag = "WOLF"
                api_region = "americas"
                minutes, games = get_today_play_time(summoner_name, tag, api_region)

            # Commande personnalisée
            elif len(args) == 3:
                region = args[1].lower()
                region_map = {
                    "euw": "europe",
                    "eune": "europe",
                    "na": "americas",
                    "kr": "asia",
                    "jp": "asia"
                }
                if region not in region_map:
                    await message.channel.send("❌ Région invalide. Exemples valides : EUW, NA, KR, JP...")
                    return

                name_tag = args[2].split("#")
                if len(name_tag) != 2:
                    await message.channel.send("❌ Format incorrect. Utilise `Nom#Tag`.")
                    return

                summoner_name, tag = name_tag
                api_region = region_map[region]
                minutes, games = get_today_play_time(summoner_name, tag, api_region)

            else:
                await message.channel.send("❌ Format de commande incorrect. Utilise `loltime -help` pour voir les options.")
                return

            heures = minutes // 60
            minutes_restantes = minutes % 60

            await message.channel.send(
                f"🕹️ {summoner_name} a joué : {heures}h {minutes_restantes}min, soit {games} games aujourd'hui !"
            )

            await thinking_msg.delete()

        except Exception as e:
            await message.channel.send("❌ Une erreur est survenue.")
            print(e)

client.run(DISCORD_TOKEN)
