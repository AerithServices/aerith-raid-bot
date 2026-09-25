import re
import aiohttp
import discord
from discord.ext import commands

from src.utils.helpers import log_command, OWNER_IDS, deny_embed, success_embed

FALLBACK_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"

INVITE_REGEX = re.compile(r"(?:https?:\/\/)?(?:www\.|ptb\.|canary\.)?discord(?:app)?\.(?:(?:com|gg)[/\\]+(?:invite|servers)[/\\]+[a-z0-9-_]+)|(?:https?://)?(?:www\.)?(?:dsc\.gg|invite\.gg+|discord\.link|(?:discord\.(?:gg|io|me|li|id))|disboard\.org)[/\\]+[a-z0-9-_/]+")


def _extract_invite_code(raw: str) -> str | None:
    if not raw:
        return None
    raw = raw.strip()

    match = INVITE_REGEX.search(raw)
    if match:
        return match.group(1)

    code = raw.rstrip("/").split("/")[-1].split("?")[0].strip()
    return code or None


async def _fetch_invite(code: str) -> dict | None:
    url = f"https://discord.com/api/v10/invites/{code}?with_counts=true"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except Exception:
        return None


def _build_result_view(server_name: str, server_icon: str, server_invite: str,
                       member_count: int, requested_by: str) -> discord.ui.LayoutView:

    class Components(discord.ui.LayoutView):
        container1 = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=(
                        f"# `⚔` Ra1d Request!\n"
                        f"Server: {server_name}\n"
                        f"Requested by: {requested_by}\n"
                        f"-# the server has {member_count} members"
                    )
                ),
                accessory=discord.ui.Thumbnail(
                    media=server_icon,
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    url=server_invite,
                    style=discord.ButtonStyle.link,
                    label="Join",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

    return Components()


class SuggestModal(discord.ui.Modal, title="Suggest a Ra1d"):
    server_invite = discord.ui.TextInput(
        label="Server Invite",
        placeholder="https://discord.gg/xxxxxx",
        required=True,
        max_length=200,
    )
    anonymous = discord.ui.TextInput(
        label="Anonymous",
        placeholder="True or False",
        required=True,
        max_length=5,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        code = _extract_invite_code(self.server_invite.value)
        if not code:
            await interaction.followup.send("that doesn't look like a valid invite.", ephemeral=True)
            return

        data = await _fetch_invite(code)
        if not data or "guild" not in data:
            await interaction.followup.send("couldn't fetch that server, is the invite valid?", ephemeral=True)
            return

        guild = data.get("guild", {})
        server_name = guild.get("name", "Unknown Server")
        member_count = data.get("approximate_member_count", 0)

        icon_hash = guild.get("icon")
        guild_id = guild.get("id")
        if icon_hash and guild_id:
            ext = "gif" if icon_hash.startswith("a_") else "png"
            server_icon = f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.{ext}?size=256"
        else:
            server_icon = FALLBACK_ICON

        server_invite = f"https://discord.gg/{code}"

        is_anonymous = self.anonymous.value.strip().lower() in ("true", "t", "yes", "y", "1")
        requested_by = "REDACTED" if is_anonymous else interaction.user.mention

        view = _build_result_view(server_name, server_icon, server_invite, member_count, requested_by)

        try:
            await interaction.channel.send(view=view)
        except Exception:
            await interaction.followup.send("i couldn't send the suggestion in this channel.", ephemeral=True)
            return

        await interaction.followup.send("your suggestion has been sent!", ephemeral=True)

        who = "anonymously" if is_anonymous else "publicly"
        await log_command(interaction, "suggest", f"suggested a ra1d on {server_name} ({who})")


class SuggestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="Suggest",
            custom_id="suggest_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SuggestModal())


class SuggestPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.TextDisplay(
            content="# `💡` Suggest an attack on any server\nClick the button below to suggest a server get ra1ded."
        ),
        discord.ui.ActionRow(
            SuggestButton(),
        ),
        accent_colour=discord.Colour(16777215),
    )


class SuggestionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(SuggestPanel())

    @commands.command(name="suggestsend")
    async def suggestsend(self, ctx: commands.Context):
        if ctx.author.id not in OWNER_IDS:
            print(f"User {ctx.author} ({ctx.author.id}) tried to use suggestsend but is not an owner.")
            return

        await ctx.send(view=SuggestPanel())


async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionCog(bot))
