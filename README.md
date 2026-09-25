<p align="center">
  <img src="https://avatars.githubusercontent.com/u/295873404?s=512" alt="Aerith Raid Bot" width="200" height="200">
</p>

<h1 align="center">Aerith Raid Bot</h1>

<p align="center">A powerful Discord bot built with discord.py for raiding, spamming, and managing servers.</p>

---

## Features

- **Raid** — Insanely Fast Raid Command
- **Interaction Raid** — Send bursts of messages via one button (up-to unlimited)
- **Spam** — Send custom messages or files on repeat
- **Thug** — Gay porn spamming for fun
- **Fake Nitro** — Deploy fake nitro giveaways and hoaxes
- **Fake Giveaway** — Host counterfeit giveaways
- **Ghost** — Ghost mention and ghost ping tools
- **DM Raid** — Direct message flooding tools
- **Ads** — Automatic advertisement posting
- **Leaderboard** — Track top raiders 
- **Admin Tools** — Reload cogs, set global messages, blacklist servers/users

---

## Installation

### Prerequisites

- [Python 3.10+](https://www.python.org/)

### Setup

```bash
# Clone the repo
git clone https://github.com/Aerith-Opensource-Project/zne-raid-bot.git
cd AerithRaid

# Create a virtual environment (standard venv)
python -m venv .venv

# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# On Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **Optional:** If you prefer [uv](https://docs.astral.sh/uv/) for faster installs, you can use `uv venv` and `uv pip install -r requirements.txt` instead.

### Configuration

Copy the example config and fill in your values:

```bash
cp config.example.toml config.toml
# Windows
copy config.example.toml config.toml
```

> **Note:** The `[api]` section in `config.toml` is used for leaderboard syncing and command tracking. These features rely on the companion website. You do not need to configure `[api]` unless you are running your own instance of the [Aerith Website](https://github.com/Aerith-Opensource-Project/zne-website/).

Edit `config.toml`:

```toml
TOKEN = "your-bot-token-here"
owner_ids = [123456789012345678]

[server]
main_server = 0
verified_role_id = 0

[channels]
log_channel_id = 0

[messages]
og_msg = """your default raid message here"""

[api]
url = "your-api-url"
secret = "your-api-secret"
```

### Running

```bash
python main.py
```

---

## Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [LMDB](https://lmdb.readthedocs.io/) — High-performance leaderboard storage
- [aiohttp](https://docs.aiohttp.org/) — Async HTTP for API posting

> **uv** (optional) — Fast package & venv management, if you prefer it over standard `venv`/`pip`