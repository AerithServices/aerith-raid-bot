import discord
from src.utils.config import EMOJIS


async def deny(interaction: discord.Interaction, error_msg: str, ephemeral: bool = True, **kwargs):
    embed = discord.Embed(
        color=16606309,
        description=f"{EMOJIS.deny} {interaction.user.mention}: {error_msg}",
    )
    kwargs["embed"] = embed
    kwargs.setdefault("ephemeral", ephemeral)
    if interaction.response.is_done():
        return await interaction.followup.send(**kwargs)
    return await interaction.response.send_message(**kwargs)


async def approve(interaction: discord.Interaction, success_msg: str, ephemeral: bool = True, **kwargs):
    embed = discord.Embed(
        color=10938999,
        description=f"{EMOJIS.approve} {interaction.user.mention}: {success_msg}",
    )
    kwargs["embed"] = embed
    kwargs.setdefault("ephemeral", ephemeral)
    if interaction.response.is_done():
        return await interaction.followup.send(**kwargs)
    return await interaction.response.send_message(**kwargs)
