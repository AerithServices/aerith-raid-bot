import discord
import base64
from discord import app_commands
from discord.ext import commands
from src.utils.helpers import log_command

class OtherCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="general info about a user")
    @app_commands.describe(user="The user to get info about")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer(ephemeral=True)
        target = user or interaction.user

        try:
            full_user = await self.bot.fetch_user(target.id)
        except:
            full_user = target

        display_name = full_user.display_name
        join_ts = f"<t:{int(full_user.created_at.timestamp())}:R>"

        serv_ts = "not in server"
        if interaction.guild:
            member = interaction.guild.get_member(full_user.id)
            if member and member.joined_at:
                serv_ts = f"<t:{int(member.joined_at.timestamp())}:R>"

        userid_into_base64 = base64.b64encode(str(full_user.id).encode()).decode().rstrip("=")
        bot_status = "YES" if full_user.bot else "NO"
        usericon = full_user.display_avatar.url

        class UserInfo(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(content=f"# {display_name}\ndiscord join: {join_ts}\nserver join: {serv_ts}\nusername: `{full_user.name}`\nid: `{full_user.id}`\nfirst token segment: `{userid_into_base64}`\nbot?: {bot_status}"),
                    accessory=discord.ui.Thumbnail(
                        media=usericon,
                    ),
                ),
                accent_colour=discord.Colour(16777215),
            )

        await interaction.followup.send(view=UserInfo())
        await log_command(interaction, "userinfo", f"viewed info for {full_user.id}")

    @app_commands.command(name="info", description="show bot information")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        import psutil
        import os
        import ast

        ver = discord.__version__
        process = psutil.Process()
        ram_mib = process.memory_info().rss / (1024 * 1024)
        try:
            cpu_percent = process.cpu_percent(interval=0.1)
        except Exception:
            cpu_percent = 0.0
        try:
            for child in process.children(recursive=True):
                try:
                    ram_mib += child.memory_info().rss / (1024 * 1024)
                    cpu_percent += child.cpu_percent(interval=0.0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass

        cogs_dir = os.path.dirname(__file__)
        cog_files = [f for f in os.listdir(cogs_dir) if f.endswith(".py") and f != "__init__.py" and os.path.isfile(os.path.join(cogs_dir, f))]

        def count_commands(filepath):
            with open(filepath, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        call = decorator
                        if isinstance(call, ast.Call):
                            call = call.func
                        name = None
                        if isinstance(call, ast.Attribute):
                            name = call.attr
                        elif isinstance(call, ast.Name):
                            name = call.id
                        if name == "command":
                            count += 1
                            break
            return count

        cog_data = []
        for filename in sorted(cog_files):
            filepath = os.path.join(cogs_dir, filename)
            name = os.path.splitext(filename)[0].capitalize()
            count = count_commands(filepath)
            cog_data.append((name, count))

        cog_lines = "\n".join([f"> {name} = `{count}` command{'s' if count != 1 else ''}" for name, count in cog_data])

        def page1():
            class Page1(discord.ui.LayoutView):
                container1 = discord.ui.Container(
                    discord.ui.Section(
                        discord.ui.TextDisplay(content="# `↯` Aerith Bot information\n### Links\n[website](https://zne.breed.rip/) • [leaderboard](https://zne.breed.rip/leaderboard) • [commands](https://zne.breed.rip/commands)\n[github](https://github.com/Aerith-Opensource-Project/zne-raid-bot) • [youtube](https://www.youtube.com/@78x2)"),
                        accessory=discord.ui.Thumbnail(
                            media="https://avatars.githubusercontent.com/u/295873404",
                        ),
                    ),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=f"### Technical information\n`➜` Running on discord.py {ver}\n`➜` Using {ram_mib:.1f} MiBs of RAM\n`➜` Using {cpu_percent:.1f}% of CPU\n`➜` `stable.120.010`"),
                    discord.ui.ActionRow(
                        discord.ui.Button(
                            style=discord.ButtonStyle.primary,
                            label="◀ Back",
                            custom_id="back_btn",
                            disabled=True,
                        ),
                        discord.ui.Button(
                            style=discord.ButtonStyle.primary,
                            label="Next ▶",
                            custom_id="next_btn",
                        ),
                    ),
                    accent_colour=discord.Colour(16777215),
                )

                async def interaction_check(self2, it: discord.Interaction) -> bool:
                    cid = it.data.get("custom_id")
                    if cid == "next_btn":
                        await it.response.edit_message(view=page2())
                    return False
            return Page1()

        def page2():
            class Page2(discord.ui.LayoutView):
                container1 = discord.ui.Container(
                    discord.ui.TextDisplay(content="# Cogs loaded"),
                    discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                    discord.ui.TextDisplay(content=cog_lines),
                    discord.ui.ActionRow(
                        discord.ui.Button(
                            style=discord.ButtonStyle.primary,
                            label="◀ Back",
                            custom_id="back_btn",
                        ),
                        discord.ui.Button(
                            style=discord.ButtonStyle.primary,
                            label="Next ▶",
                            custom_id="next_btn",
                            disabled=True,
                        ),
                    ),
                    accent_colour=discord.Colour(16777215),
                )

                async def interaction_check(self2, it: discord.Interaction) -> bool:
                    cid = it.data.get("custom_id")
                    if cid == "back_btn":
                        await it.response.edit_message(view=page1())
                    return False
            return Page2()

        await interaction.followup.send(view=page1())

    @app_commands.command(name="permcheck", description="check if the server is raidable or not")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def permcheck(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class Components(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.TextDisplay(content="**check if server is raidable or not**\nthis checks if the bot can send public messages which shows if a server is raidable"),
                discord.ui.ActionRow(
                        discord.ui.Button(
                            style=discord.ButtonStyle.secondary,
                            label="say",
                            custom_id="5b1ec20e48b54f008bd08c2644ba1d66",
                        ),
                ),
            )

            async def interaction_check(self, it: discord.Interaction) -> bool:
                cid = it.data.get("custom_id")
                if cid == "5b1ec20e48b54f008bd08c2644ba1d66":
                    await it.response.defer(ephemeral=True)
                    status_text = "not raidable"


                    try:
                        msg = await it.channel.send("\u200c")
                        status_text = "yes its raidable"
                        try: await msg.delete()
                        except: pass
                    except discord.Forbidden:
                        try:
                            msg = await it.followup.send("\u200c", ephemeral=False)
                            if msg.flags.ephemeral:
                                status_text = "not raidable"
                            else:
                                status_text = "yes its raidable"

                            try: await msg.delete()
                            except: pass
                        except:
                            pass
                    except Exception:
                        pass

                    class ResultView(discord.ui.LayoutView):
                        container1 = discord.ui.Container(
                            discord.ui.TextDisplay(content=f"**check if server is raidable or not**\n\nresult: **{status_text}**"),
                            accent_colour=discord.Colour(16777215)
                        )
                    await interaction.edit_original_response(view=ResultView())

                    raid_status = "is raidable" if status_text == "yes its raidable" else "isnt raidable"
                    await log_command(it, "permcheck", f"checked server raidability, the server {raid_status}")
                    return False


        await interaction.followup.send(view=Components, ephemeral=True)

    @app_commands.command(name="webhook-spam", description="spam a webhook.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def webhook_spam(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class Components(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        url="https://zne.breed.rip/webhook",
                        style=discord.ButtonStyle.link,
                        label="spam webhooks today!",
                    ),
                ),
            )

        await interaction.followup.send(view=Components())
        await log_command(interaction, "webhook-spam", "viewed webhook spam link")

    @app_commands.command(name="leaderboard", description="view the zne leaderboard")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class Components(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        url="https://zne.breed.rip/leaderboard",
                        style=discord.ButtonStyle.link,
                        label="view leaderboard",
                    ),
                ),
            )

        await interaction.followup.send(view=Components())
        await log_command(interaction, "leaderboard", "viewed leaderboard link")

async def setup(bot: commands.Bot):
    await bot.add_cog(OtherCog(bot))
