import discord
import tomllib
from discord import app_commands
from src.utils.db import is_server_blacklisted, is_user_blacklisted
from src.utils.helpers import deny_embed

with open("config.toml", "rb") as f:
    _config = tomllib.load(f)

OWNER_IDS = [int(uid) for uid in _config.get("owner_ids", [])]
OWNER_BLACKLIST_BYPASS = bool(_config.get("owner_blacklist_bypass", True))
MAIN_SERVER_ID = int(_config.get("main_server", _config.get("server", {}).get("main_server", 0)))
REQUIRED_SERVER_ID = MAIN_SERVER_ID
VERIFIED_ROLE_ID = int(_config.get("server", {}).get("verified_role_id", 0))


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id in OWNER_IDS


async def global_interaction_check(interaction: discord.Interaction) -> bool:
    user_id = interaction.user.id
    is_bot_owner = user_id in OWNER_IDS

    if is_bot_owner and OWNER_BLACKLIST_BYPASS:
        return True

    if await is_user_blacklisted(str(user_id)):
        await interaction.response.send_message("You are blacklisted from using the bot.", ephemeral=True)
        return False

    guild_id = interaction.guild_id

    if guild_id and await is_server_blacklisted(str(guild_id)):
        await interaction.response.send_message("This server is blacklisted.", ephemeral=True)
        return False

    if interaction.type != discord.InteractionType.application_command:
        return True

    if not interaction.command:
        return True

    if interaction.command.name == "userinfo":
        return True

    if MAIN_SERVER_ID and guild_id is not None and int(guild_id) == MAIN_SERVER_ID:
        await interaction.response.send_message("u can't raid this server lil bro 😂✌🏿", ephemeral=True)
        return False

    guild = interaction.client.get_guild(REQUIRED_SERVER_ID)
    if guild is None:
        from src.views.join import get_access_denied_view
        await interaction.response.send_message(ephemeral=True, view=get_access_denied_view(interaction.client.user))
        return False

    member = guild.get_member(user_id)
    if member is None:
        from src.views.join import get_access_denied_view
        await interaction.response.send_message(ephemeral=True, view=get_access_denied_view(interaction.client.user))
        return False

    role = guild.get_role(VERIFIED_ROLE_ID)
    if role is None or role not in member.roles:
        from src.views.join import get_access_denied_view
        await interaction.response.send_message(ephemeral=True, view=get_access_denied_view(interaction.client.user))
        return False

    return True
