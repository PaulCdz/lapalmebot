import discord

async def handle_help(message):
    if message.content.strip().lower() == "br help":
        help_msg = (
            "**📘 Commandes disponibles :**\n\n"
            "__🎮 LoLTime__\n"
            "`loltime` : Affiche le temps de jeu de Sheep Vibes\n"
            "`loltime <RÉGION> <Nom#Tag>` : Affiche le temps de jeu du joueur indiqué\n"
            "`loltime -help` : Affiche l’aide LoL\n\n"
            "__🐙 Git ETA__\n"
            "`git add <url> <nom>` : Ajoute un dépôt à surveiller\n"
            "`git list` : Liste les dépôts suivis\n"
            "`git rm <nom>` : Supprime un dépôt suivi\n"
        )
        await message.channel.send(help_msg)

