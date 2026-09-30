# the bot has an aging codebase :pray:
import asyncio
import os
import tomllib
import traceback
import discord
import sys
from discord import app_commands
from discord.ext import commands
from discord import AllowedMentions

from src.utils.checks import global_interaction_check
from src.utils.db import init_db
# from src.utils.helpers import post_commands_to_api, post_leaderboard_to_api
from src.utils.leaderboard import load_leaderboard, track_command
from src.utils.logger import setup_logging


with open("config.toml", "rb") as f:
    config = tomllib.load(f)

TOKEN = config["TOKEN"]
OWNERS = config["owner_ids"]
MESSAGE_LIMIT = 2000
# mentions still render as chips without this, they just don't notify the owners
PING_OWNERS = bool(config.get("logging", {}).get("ping_owners_on_error", False))
logger, DEBUG_MODE = setup_logging(config)
if DEBUG_MODE:
    logger.info("debug logging is enabled (discord.http stays at INFO to avoid leaking interaction tokens)")

class AerithRaid(commands.Bot):
    def __init__(self) -> None:
            super().__init__(
                command_prefix="..",
                case_insensitive=True,
                intents=discord.Intents.all(),
                help_command=None,
                allowed_mentions=AllowedMentions(
                    everyone=True, roles=True, replied_user=False
                ),
                owner_ids=OWNERS,
            )

bot = AerithRaid()
bot.tree.interaction_check = global_interaction_check


def total_commands() -> int:
    _, total_commands = load_leaderboard()
    return total_commands

async def update_bot_status():
    activity = discord.Activity(
        name=f"zne.breed.rip | {total_commands()} raids...",
        type=discord.ActivityType.streaming,
        url="https://twitch.tv/voby7"
    )
    await bot.change_presence(activity=activity)


# async def leaderboard_sync_loop():
#     await asyncio.sleep(5 * 60)
#     while True:
#         await post_leaderboard_to_api(bot)
#         await update_bot_status()
#         await asyncio.sleep(5 * 60)

# the loop above is still commented out, keep a name so on_ready can check for it
leaderboard_sync_loop = None


# @bot.event
# async def on_interaction(interaction: discord.Interaction):
#     if interaction.type != discord.InteractionType.application_command:
#         return
#     if not interaction.command:
#         return
#     await track_command(
#         str(interaction.user.id),
#         interaction.command.qualified_name,
#         display_name=interaction.user.display_name,
#         avatar_url=interaction.user.display_avatar.url,
#     )


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    logger.error("prefix command %r failed in %s", ctx.command, ctx.channel, exc_info=error)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type is not discord.InteractionType.application_command:
        return
    command = interaction.command.qualified_name if interaction.command else "unresolved"
    logger.info(
        "app command /%s from %s (%s) guild=%s channel=%s",
        command,
        interaction.user,
        interaction.user.id,
        interaction.guild_id,
        interaction.channel_id,
    )


CODE_FENCE_OVERHEAD = len("```\n\n```")


def _format_traceback(error: BaseException, budget: int) -> str:
    trace = "".join(traceback.format_exception(type(error), error, error.__traceback__)).rstrip()
    if len(trace) > budget:
        # the tail holds the exception type, its message and the frames that caused it
        trace = "...\n" + trace[-(budget - 4):]
    return f"```\n{trace}\n```"


def _build_error_message(command: str, error: BaseException) -> str:
    header = f"something broke while running `/{command}`:\n"
    footer = f"\n\nyou may ping the owners ({', '.join(f'<@{owner_id}>' for owner_id in OWNERS)}) about this."
    if not OWNERS:
        footer = "\n\ncheck the bot logs for the full traceback."

    budget = MESSAGE_LIMIT - len(header) - len(footer) - CODE_FENCE_OVERHEAD
    return f"{header}{_format_traceback(error, budget)}{footer}"


async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    command = interaction.command.qualified_name if interaction.command else "unresolved"
    logger.error(
        "app command /%s failed for %s (%s) guild=%s channel=%s",
        command,
        interaction.user,
        interaction.user.id,
        interaction.guild_id,
        interaction.channel_id,
        exc_info=error,
    )

    message = _build_error_message(command, error)
    mentions = discord.AllowedMentions(users=OWNERS) if PING_OWNERS else discord.AllowedMentions.none()
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True, allowed_mentions=mentions)
        else:
            await interaction.response.send_message(message, ephemeral=True, allowed_mentions=mentions)
    except discord.HTTPException:
        logger.warning("could not deliver the error message for /%s", command, exc_info=True)


bot.tree.on_error = on_app_command_error


def discover_cogs(commands_dir: str = "src/commands") -> list[str]:
    cogs = []
    for filename in os.listdir(commands_dir):
        full_path = os.path.join(commands_dir, filename)
        if filename.endswith(".py") and not filename.startswith("__"):
            cogs.append(f"src.commands.{filename[:-3]}")
        elif os.path.isdir(full_path) and filename != "__pycache__":
            if os.path.exists(os.path.join(full_path, "__init__.py")):
                cogs.append(f"src.commands.{filename}")
    cogs.sort()
    return cogs


async def load_cog(cog: str):
    try:
        module = __import__(cog, fromlist=[""])
    except Exception as e:
        logger.error(f"Failed to import cog {cog}: {e}", exc_info=True)
        return
    if hasattr(module, "cog_setup"):
        try:
            module.cog_setup(bot)
            logger.info(f"new cog loaded: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)
        return
    try:
        await bot.load_extension(cog)
        logger.info(f"new cog loaded: {cog}")
    except Exception as e:
        logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)


@bot.event
async def on_ready():
    try:
        await init_db()
    except Exception:
        logger.error("failed to open the database, every db-backed command will fail", exc_info=True)
    logger.info(f"i am {bot.user}")
    for cog in discover_cogs():
        await load_cog(cog)
    try:
        await bot.tree.sync()
    except Exception as e:
        logger.error(f"Error syncing tree: {e}", exc_info=True)
    # await post_commands_to_api(bot)
    # await post_leaderboard_to_api(bot)
    try:
        await update_bot_status()
    except Exception:
        logger.error("failed to update presence", exc_info=True)
    if leaderboard_sync_loop is not None and (
        not getattr(bot, "_leaderboard_sync_task", None) or bot._leaderboard_sync_task.done()
    ):
        bot._leaderboard_sync_task = asyncio.create_task(leaderboard_sync_loop())
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    logger.info(f"Bot invite: {invite_url}")


async def main():
    logger.info("Starting bot...")
    await bot.start(TOKEN)
    logger.info("Bot disconnected.")


if __name__ == "__main__":
    try:
        # debug=True logs "executing <Handle ...> took N seconds", which is how a
        # command that never answers the interaction shows up
        asyncio.run(main(), debug=DEBUG_MODE)
    except KeyboardInterrupt:
        sys.exit()
    except Exception:
        logger.critical("bot crashed on startup", exc_info=True)
        sys.exit(1)
