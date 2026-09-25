import re
import time
import psutil
import os
import discord
from discord import app_commands
from discord.ext import commands

from src.utils.helpers import (
    log_command,
    Aerith_INVITE,
)

from src.views import (
    SpamButton,
    PingPanel,
    ThugView,
    custom_spam_panel,
    FakeNitroView,
    PresetManagementView,
    insult_panel,
    InteractionRaidView,
    InteractionThugView,
    multiplespam_panel,
    )

from src.utils.db import get_user_presets, get_preset_by_title


class RaidCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def preset_autocomplete(self, interaction: discord.Interaction, current: str):
        presets = await get_user_presets(str(interaction.user.id))
        return [
            app_commands.Choice(name=p['title'], value=p['title'])
            for p in presets if current.lower() in p['title'].lower()
        ][:25]

    @app_commands.command(name="ra1d", description="the command of eternal doom and gloom")
    @app_commands.describe(preset="Optional preset to use for the raid")
    @app_commands.autocomplete(preset=preset_autocomplete)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ra1d(self, interaction: discord.Interaction, preset: str = None):
        await interaction.response.defer(ephemeral=True, thinking=True)

        preset_content = None
        if preset:
            preset_content = await get_preset_by_title(str(interaction.user.id), preset)

        await interaction.followup.send(view=SpamButton(interaction.user.id, preset_content, ephemeral=True))
        await log_command(interaction, "ra1d", "user raided a server")

    @app_commands.command(name="interaction-ra1d", description="raid using stored interaction webhook tokens")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def interaction_ra1d(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        view = InteractionRaidView()
        msg = await interaction.followup.send(view=view, ephemeral=True)
        updated_view = InteractionRaidView(original_message=msg)
        await msg.edit(view=updated_view)
        await log_command(interaction, "interaction-ra1d", "user started interaction raid")

    @app_commands.command(name="setpresetmsg", description="open the custom ra1d message panel")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def custom_ra1d(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=PresetManagementView(interaction.user.id, ephemeral=True))
        await log_command(interaction, "custom_ra1d", "user opened custom message panel")

    @app_commands.command(name="thug", description="thug the server!!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def thug(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=ThugView(interaction.user.id, ephemeral=True))
        await log_command(interaction, "thug", "user thugged a server 😂")

    @app_commands.command(name="interactionthug", description="thug raid using stored interaction webhook tokens")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def interactionthug(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        view = InteractionThugView()
        msg = await interaction.followup.send(view=view, ephemeral=True)
        updated_view = InteractionThugView(original_message=msg)
        await msg.edit(view=updated_view)
        await log_command(interaction, "interactionthug", "user started interaction thug")

    @app_commands.command(name="blame", description="blame a user for raiding.")
    @app_commands.describe(user="The user to blame")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def blame(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        loading_msg = await interaction.followup.send("❗ blaming....", ephemeral=True)
        expires_ts = int(time.time()) + 7 * 24 * 60 * 60
        avatar_url = user.display_avatar.url

        class Blame(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(content=f"## `✅`  Raid Completed\n{user.mention} Your raid was completed!\n**Remember!** your trial is ending in <t:{expires_ts}:R>"),
                    accessory=discord.ui.Thumbnail(
                        media=avatar_url,
                    ),
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"-# Join our [discord]({Aerith_INVITE}) to remove this message"),
                accent_colour=discord.Colour(16777215),
            )

        await interaction.followup.send(view=Blame())
        await loading_msg.delete()
        await log_command(interaction, "blame", f"blamed user: {user.id}")

    @app_commands.command(name="say", description="say something through the bot.")
    @app_commands.describe(text="The text for the bot to say")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def say(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("sending..", ephemeral=True)
        await interaction.followup.send(text, ephemeral=False)

    @app_commands.command(name="spam", description="spam something.")
    @app_commands.describe(text="The message to spam")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def spam(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if "discord.gg/" in text.lower():
            text = re.sub(r'(?:https?://)?discord\.gg/\S+', Aerith_INVITE, text)

        await interaction.followup.send(view=custom_spam_panel(interaction.user.id, text, ephemeral=True))
        await log_command(interaction, "spam", f"user spammed: {text}")

    @app_commands.command(name="multiplespam", description="spam multiple messages randomly")
    @app_commands.describe(
        message1="First message to spam",
        message2="Second message to spam",
        message3="Third message to spam",
        message4="Fourth message to spam",
        message5="Fifth message to spam",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def multiplespam(
        self,
        interaction: discord.Interaction,
        message1: str,
        message2: str = None,
        message3: str = None,
        message4: str = None,
        message5: str = None,
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        import re

        raw_messages = [message1, message2, message3, message4, message5]
        messages = []
        for m in raw_messages:
            if m and "discord.gg/" in m.lower():
                m = re.sub(r'(?:https?://)?discord\.gg/\S+', Aerith_INVITE, m)
            if m:
                messages.append(m)

        if not messages:
            await interaction.followup.send("You need to provide at least one message!", ephemeral=True)
            return

        await interaction.followup.send(view=multiplespam_panel(messages, ephemeral=True))
        await log_command(interaction, "multiplespam", f"user spammed {len(messages)} messages randomly")

    @app_commands.command(name="insult", description="insult a user with a roast button.")
    @app_commands.describe(user="The user to insult", delay="Optional delay in seconds between each insult")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def insult(self, interaction: discord.Interaction, user: discord.User, delay: app_commands.Range[int, 0, 60] = 0):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(view=insult_panel(user, delay), ephemeral=False)
        await log_command(interaction, "insult", f"insulted user: {user.id} with {delay}s delay")


async def setup(bot: commands.Bot):
    await bot.add_cog(RaidCog(bot))
