import aiohttp
import asyncio
import json
from discord.ext import tasks

REPO_FILE = "git_eta/repos.json"
CHECK_INTERVAL = 300  # secondes

repos = {}

def load_repos():
    try:
        with open(REPO_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_repos(data):
    with open(REPO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def start_watcher(bot, repo_data=None):
    if not check_updates.is_running():
        check_updates.start(bot)
        print("[Git-ETA] Boucle check_updates lancée.", flush=True)



@tasks.loop(seconds=CHECK_INTERVAL)
async def check_updates(bot):
    print("[Git-ETA] Vérification automatique des dépôts...", flush=True)
    dynamic_repos = load_repos()
    await check_all(bot, dynamic_repos)

async def check_all(bot, repo_data, response_channel=None):
    async with aiohttp.ClientSession() as session:
        for name, data in repo_data.items():
            url = data["url"]
            channel_id = int(data["channel_id"])
            last_sha = data.get("last_sha")

            owner_repo = extract_github_repo(url)
            if not owner_repo:
                continue

            api_url = f"https://api.github.com/repos/{owner_repo}/commits"

            try:
                async with session.get(api_url) as resp:
                    if resp.status != 200:
                        msg = f"❌ Impossible de vérifier `{name}` ({resp.status})"
                        print(f"[Erreur API] {msg}")
                        if response_channel:
                            await response_channel.send(msg)
                        continue

                    commits = await resp.json()
                    latest_sha = commits[0]["sha"]

                    if latest_sha != last_sha:
                        commit_msg = commits[0]["commit"]["message"]
                        author = commits[0]["commit"]["author"]["name"]
                        link = commits[0]["html_url"]

                        repo_data[name]["last_sha"] = latest_sha
                        save_repos(repo_data)

                        notif = (
                            f"🔄 Nouveau commit sur `{name}` !\n"
                            f"**Auteur :** {author}\n"
                            f"**Message :** {commit_msg}\n{link}"
                        )
                        channel = bot.get_channel(channel_id)
                        if not channel:
                            print(f"[Erreur Channel] Le channel {channel_id} n'existe pas pour `{name}`.", flush=True)
                            continue
                        if channel:
                            await channel.send(notif)
                        if response_channel and channel.id != response_channel.id:
                            await response_channel.send(notif)
                    else:
                        if response_channel:
                            await response_channel.send(f"✅ Aucun nouveau commit pour `{name}`.")

            except Exception as e:
                error_msg = f"⚠️ Erreur pour `{name}` : {e}"
                print(error_msg)
                if response_channel:
                    await response_channel.send(error_msg)

# Utilisée par git check
async def force_check(bot, repo_data, response_channel):
    print("[Git-ETA] Vérification forcée déclenchée.", flush=True)
    await check_all(bot, repo_data, response_channel)

def extract_github_repo(url):
    """Convertit une URL GitHub en owner/repo"""
    if "github.com" not in url:
        return None
    url = url.replace(".git", "").strip()
    parts = url.split("github.com/")[-1].split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None
