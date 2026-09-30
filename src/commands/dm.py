import asyncio
import discord
import tomllib
from discord import app_commands
from discord.ext import commands
from src.utils.helpers import log_command
from src.client import deny, approve


class DmCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dmanon", description="dm someone.")
    @app_commands.describe(user_id="User ID to DM", message="Message to send")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def dmanon(self, interaction: discord.Interaction, user_id: str, message: str):
        await interaction.response.defer(ephemeral=True)
        try:
            user = await self.bot.fetch_user(int(user_id))
            await approve(interaction, f"DM sent to {user.display_name}!")
            await log_command(interaction, "anon-dm", f"sent DM to {user_id}")
        except discord.Forbidden:
            await deny(interaction, "Cannot send DM - user has DMs disabled or bot is blocked.")
        except Exception as e:
            await deny(interaction, f"Error sending DM: {e}")

    @app_commands.command(name="dmflood", description="Send 20 DMs to a user.")
    @app_commands.describe(user_id="User ID to flood", message="Message to send")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def dmflood(self, interaction: discord.Interaction, user_id: str, message: str):
        await interaction.response.defer(ephemeral=True)
        await approve(interaction, "⏳ Flooding started in background...")

        async def flood_task():
            try:
                user = await self.bot.fetch_user(int(user_id))
                for i in range(20):
                    await user.send(f"{message}")
                await approve(interaction, f"Flooded {user.display_name} with 20 DMs!")
            except discord.Forbidden:
                await deny(interaction, "Cannot send DM - user has DMs disabled or bot is blocked.")
            except Exception as e:
                await deny(interaction, f"Error sending DM: {e}")

        asyncio.create_task(flood_task())


async def setup(bot: commands.Bot):
    await bot.add_cog(DmCog(bot))
