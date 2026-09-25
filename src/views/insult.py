import os
import asyncio
import aiohttp
import discord
import random

from src.utils.helpers import send_message_http
from src.utils.helpers import deny_embed


def load_insults() -> list[str]:
    try:
        with open(os.path.join("data", "insults.txt"), "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def insult_panel(user: discord.User, delay: int = 0):
    class InsultView(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.user_id = user.id
            self.delay = delay

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"# INSULT {user.mention}!\nclick the button below to start roasting them."),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="roast!",
                    custom_id="roastbtn",
                ),
            ),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "roastbtn":
                await interaction.response.defer()

                insults = load_insults()
                if len(insults) < 5:
                    await interaction.followup.send(embed=deny_embed("insults.txt must contain at least 5 insults!"), ephemeral=True)
                    return False

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    for insult in random.sample(insults, 5):
                        await send_message_http(session, app_id, token, f"{user.mention} {insult}")
                        if self.delay:
                            await asyncio.sleep(self.delay)

                return False
            return True

    return InsultView()
