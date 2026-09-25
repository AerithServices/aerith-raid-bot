import discord
from discord.ext import commands
from discord import app_commands, AllowedMentions
from src.utils.helpers import Aerith_INVITE

class Panel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ad", description="send the zne advertisement")
    @app_commands.describe(noping="If true, removes @everyone ping from the ad")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ad(self, interaction: discord.Interaction, noping: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)

        class Components(discord.ui.LayoutView):
            discord.ui.TextDisplay(content=f"{Aerith_INVITE} {'@everyone ' if not noping else ''}"),

            container1 = discord.ui.Container(
                discord.ui.TextDisplay(content="# __WELCOME TO Aerith__\n**STOP PAYING FOR GARBAGE BOTS THAT BARELY HAVE ANY FEATURES**\nAerith is a 100% free discord raid bot, no premium shenanigans, no hidden paywalls\nAerith has been free for a *YEAR* now (made in april 2025)"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="## `❓` What does Aerith offer?\n> Blazing fast discord raider bots\n> Nuke bots that will **100%** crash your phone\n> Easy-to use Webhook spammers\n> Weekly Giveaways!"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(
                        media="https://zne.breed.rip/assets/banner.gif",
                    ),
                ),
                discord.ui.ActionRow(
                    discord.ui.Button(
                        url=Aerith_INVITE,
                        style=discord.ButtonStyle.link,
                        label="join",
                    ),
                ),
            )

        view = Components()

        await interaction.followup.send(
            "ok loading it nooow!!",
            ephemeral=True
        )
        await interaction.followup.send(
            view=view,
            allowed_mentions=AllowedMentions(everyone=True)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Panel(bot))
