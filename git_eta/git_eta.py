import discord
import json
import os

REPO_FILE = "git_eta/repos.json"
repos = {}

def load_repos():
    if not os.path.exists(REPO_FILE):
        return {}
    with open(REPO_FILE, "r") as f:
        return json.load(f)

def save_repos(data):
    with open(REPO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_repos():
    return repos

async def handle_git_eta(client, message: discord.Message):
    global repos
    if not repos:
        repos = load_repos()

    if not message.content.startswith("git "):
        return

    args = message.content.split()
    if len(args) < 2:
        return

    cmd = args[1]

    if cmd == "add":
        if len(args) != 4:
            await message.channel.send("❌ Utilisation : `git add <url> <nom>`")
            return
        url, name = args[2], args[3]
        if name in repos:
            await message.channel.send(f"❌ Le dépôt `{name}` existe déjà.")
            return
        repos[name] = {
            "url": url,
            "channel_id": str(message.channel.id),
            "last_sha": None
        }
        save_repos(repos)
        await message.channel.send(f"✅ Dépôt `{name}` ajouté et surveillé.")

    elif cmd == "list":
        if not repos:
            await message.channel.send("📭 Aucun dépôt suivi.")
            return
        msg = "**📋 Dépôts suivis :**\n"
        for name, info in repos.items():
            msg += f"• `{name}` → {info['url']} (Salon <#{info['channel_id']}>)\n"
        await message.channel.send(msg)

    elif cmd == "rm" and len(args) == 3:
        name = args[2]
        if name not in repos:
            await message.channel.send(f"❌ Le dépôt `{name}` n’est pas suivi.")
            return
        del repos[name]
        save_repos(repos)
        await message.channel.send(f"🗑️ Dépôt `{name}` supprimé.")
    elif cmd == "check":
        from .repo_watch import force_check
        await force_check(client, repos, message.channel)

