import asyncio
import io
import random
from pathlib import Path
import requests
import string
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont
from datetime import datetime

from src.utils.helpers import log_command

from src.views import FakeNitroView, fake_giveaway
from src.client import deny, approve

FONT_DIR = Path("fonts")
BG = (54, 57, 63)
PILL_BG = (35, 35, 46)
WHITE = (255, 255, 255)
TIME_COLOR = (219, 222, 225)
GGSANS_SEMIBOLD = "src/utils/fonts/ggsanssemibold.ttf"
GGSANS_MEDIUM = "src/utils/fonts/ggsansmedium.ttf"

def load_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONT_DIR / filename), size)
    except OSError:
        return ImageFont.load_default(size)


def random_time() -> str:
    hour = random.randint(1, 12)
    minute = random.randint(0, 59)
    return f"{hour}:{minute:02d} {random.choice(['AM', 'PM'])}"


def circle_avatar(data: bytes, size: int) -> Image.Image:
    scale = 4
    avatar = Image.open(io.BytesIO(data)).convert("RGBA").resize((size * scale,) * 2, Image.LANCZOS)
    mask = Image.new("L", (size * scale,) * 2, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=255)
    avatar.putalpha(mask)
    return avatar.resize((size, size), Image.LANCZOS)


def render_fake_message(
    display_name: str,
    avatar_bytes: bytes,
    tag: str | None,
    badge_bytes: bytes | None,
    message: str,
) -> io.BytesIO:
    name_font = load_font(GGSANS_MEDIUM, 52)
    tag_font = load_font(GGSANS_SEMIBOLD, 36)
    time_font = load_font(GGSANS_MEDIUM, 36)
    msg_font = load_font(GGSANS_SEMIBOLD, 40)

    time_str = random_time()

    name_w = name_font.getlength(display_name)
    x_name = 240
    x = x_name + name_w

    pill = None
    if tag:
        badge_size = 40
        pad = 14
        gap = 8
        tag_w = tag_font.getlength(tag)
        content_w = (badge_size + gap if badge_bytes else 0) + tag_w
        pill_w = int(content_w + pad * 2)
        pill_x0 = int(x + 8)
        pill = (pill_x0, 35, pill_x0 + pill_w, 93)
        x = pill[2]

    time_x = x + 26
    line1_right = time_x + time_font.getlength(time_str)
    line2_right = x_name + msg_font.getlength(message)
    width = max(1172, int(max(line1_right, line2_right) + 60))
    height = 233

    img = Image.new("RGBA", (width, height), BG + (255,))
    draw = ImageDraw.Draw(img)

    img.paste(circle_avatar(avatar_bytes, 150), (35, 30), circle_avatar(avatar_bytes, 150))

    draw.text((x_name, 84), display_name, font=name_font, fill=WHITE, anchor="ls")

    if pill:
        draw.rounded_rectangle(pill, radius=12, fill=PILL_BG)
        cx = pill[0] + 14
        if badge_bytes:
            badge = Image.open(io.BytesIO(badge_bytes)).convert("RGBA").resize((40, 40), Image.LANCZOS)
            img.paste(badge, (cx, pill[1] + (pill[3] - pill[1] - 40) // 2), badge)
            cx += 40 + 8
        draw.text((cx, 80), tag, font=tag_font, fill=WHITE, anchor="ls")

    draw.text((time_x, 82), time_str, font=time_font, fill=TIME_COLOR, anchor="ls")
    draw.text((x_name, 158), message, font=msg_font, fill=WHITE, anchor="ls")

    out = io.BytesIO()
    img.convert("RGB").save(out, "PNG")
    out.seek(0)
    return out


class FakeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="fakenitro", description="send a ULTRA realistic nitro embed.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fake_nitro(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await approve(interaction, "⌛ Loading nitro panel...", ephemeral=True)
        await interaction.followup.send(view=FakeNitroView(), ephemeral=False)
        await log_command(interaction, "fake nitro", "user baited someone with a fake nitro.")

    @app_commands.command(name="fakeip", description="show a fake ip to a user and scare them.")
    @app_commands.describe(user="The user to scare")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fake_ip(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await approve(interaction, "hacking noww", ephemeral=True)

        random_company = random.choice([
            "Cloudflare",
            "GitHub",
            "Discord",
            "AWS",
            "Microsoft",
            "Google",
            "Meta",
            "Netflix",
            "Steam",
            "OpenAI",
            "Roblox",
            "Minecraft",
            "Dropbox",
        ])
        trace_letters = "".join(random.choices(string.ascii_uppercase, k=3))
        trace_numbers = random.randint(100, 999)
        fake_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

        class Components(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.TextDisplay(content=f"{user.mention}\n## data breach notification\nyour network signature has been matched with compromised assets from the **{random_company}** data breach. your connection details have been logged for analysis.\n**source of compromise:** `{random_company}`\n**trace id:** `#{trace_letters}-{trace_numbers}`\n**exposed ip address:**\n```ini\n{fake_ip}\n```\n*system alert proactive measures are advised*"),
            )

        await interaction.followup.send(view=Components(), ephemeral=False)
        await log_command(interaction, "fakeip", f"scared user: {user.id}")

    @app_commands.command(name="fakegiveaway", description="send a fake giveaway embed.")
    @app_commands.describe(prize="The prize for the giveaway")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fake_giveaway(self, interaction: discord.Interaction, prize: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await approve(interaction, "⌛ Loading giveaway panel...", ephemeral=True)
        await interaction.followup.send(view=fake_giveaway(prize), ephemeral=False)
        await log_command(interaction, "fake giveaway", f"user baited someone with a fake giveaway for: {prize}")

    @app_commands.command(name="fakemessage", description="Generate a fake Discord message image")
    @app_commands.describe(userid="The ID of the user", message="The fake message to show", keep_tag="Show the user's server tag")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fake_message(self, interaction: discord.Interaction, userid: str, message: str, keep_tag: bool = True):
        await interaction.response.defer()

        try:
            user = await interaction.client.fetch_user(int(userid))
        except (ValueError, discord.NotFound):
            return await deny(interaction, "Couldn't find a user with that ID.")
        except discord.HTTPException:
            return await deny(interaction, "Discord API error, try again.")

        avatar_bytes = await user.display_avatar.replace(size=256, format="png").read()

        tag = None
        badge_bytes = None
        if keep_tag:
            pg = user.primary_guild
            if pg and pg.identity_enabled and pg.tag:
                tag = pg.tag
                if pg.badge:
                    badge_bytes = await pg.badge.replace(size=64, format="png").read()

        buf = await asyncio.to_thread(
            render_fake_message, user.display_name, avatar_bytes, tag, badge_bytes, message
        )
        await interaction.followup.send(file=discord.File(buf, "fakemessage.png"))
        await log_command(interaction, "fake message", f"user spoofed message as {user.display_name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(FakeCog(bot))
