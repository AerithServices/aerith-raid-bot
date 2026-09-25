import asyncio
import io
import os
import random
import aiohttp
import discord
import tomllib

from src.utils.helpers import Aerith_INVITE
from src.utils.db import get_global_default_message
from src.utils.helpers import send_message_http

_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.toml")
with open(_config_path, "rb") as f:
    _config = tomllib.load(f)
DEFAULT_BUTTON_MESSAGE = _config["messages"]["og_msg"]


class SpamButton(discord.ui.LayoutView):
    def __init__(self, user_id: int, preset_content: str = None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.preset_content = preset_content

    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# zne is open source so it would be really appreciated if you could star the [github repo](https://github.com/Aerith-Opensource-Project/zne-raid-bot)"),
        discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 5X",
                    custom_id="send_spam_button",
                ),
        ),
        accent_colour=discord.Colour(16777215),
    )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get("custom_id") == "send_spam_button":
            await interaction.response.defer()

            if self.preset_content:
                msg = self.preset_content
            else:
                global_msg = await get_global_default_message()
                msg = global_msg if global_msg else DEFAULT_BUTTON_MESSAGE

            app_id = interaction.client.application_id
            token = interaction.token

            async with aiohttp.ClientSession() as session:
                tasks = [
                    send_message_http(session, app_id, token, msg)
                    for _ in range(5)
                ]
                await asyncio.gather(*tasks)

            return False

def custom_spam_panel(user_id: int, message: str):
    class CustomSpamPanel(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.custom_message = message

        preview = message if len(message) <= 60 else message[:60] + "..."
        container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# you are spamming the following message:\n```{preview}```"),
            discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="SPAM 5X",
                        custom_id="custom_spam_send_button",
                    ),
                    discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="SPAM 6X",
                        custom_id="custom_spam_send_button_6x",
                    ),
            ),
        accent_colour=discord.Colour(16777215),
    )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "custom_spam_send_button":
                await interaction.response.defer()

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, self.custom_message)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False

            if interaction.data.get("custom_id") == "custom_spam_send_button_6x":
                await interaction.response.defer()

                await interaction.followup.send(self.custom_message, ephemeral=False, allowed_mentions=discord.AllowedMentions(everyone=True))

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, self.custom_message)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False
            return True

    return CustomSpamPanel()


def multiplespam_panel(messages: list[str]):
    display = "\n".join(f"```{m if len(m) <= 60 else m[:60] + '...'}```" for m in messages)

    class MultipleSpamPanel(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.messages = messages

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# you are spamming the following messages randomly:\n{display}"),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 5X",
                    custom_id="multi_spam_5x",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 10X",
                    custom_id="multi_spam_10x",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            cid = interaction.data.get("custom_id")

            if cid == "multi_spam_5x":
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, random.choice(self.messages))
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)
                return False

            if cid == "multi_spam_10x":
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, random.choice(self.messages))
                        for _ in range(10)
                    ]
                    await asyncio.gather(*tasks)
                return False

            return True

    return MultipleSpamPanel()
