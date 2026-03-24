Language: [日本語](README.md) | English

# ODPT Japanese Airport Flight Monitor

This project fetches flight arrival and departure information for a specific airport using the Public Transport Open Data Center (ODPT) API and sends notifications via a Discord Bot when changes are detected.
![Hero](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/hero-image.png)

## Key Features

- **Real-time Monitoring**: Fetches the latest flight information using the ODPT API.
- **Differential Notifications**: Compares current data with previous state to detect and notify about new flights, status changes, or removals (optional).
- **Discord Bot Integration**: Sends rich Embed notifications directly via a Discord Bot.
- **Slash Commands**: Filter notifications to specific flights using `/watch` and related commands.
- **Flexible Configuration**: Choose to monitor arrivals, departures, or both.
- **Multiple Environments**: Easily runs via Python natively, Docker, or Docker Compose.

## Screenshots
![1](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/sample1.jpg)

## Setup

### Prerequisites
- Docker and Docker Compose
- [Public Transport Open Data Center](https://developer.odpt.org/) API Key (Consumer Key)
- A Discord Bot token and a target channel ID

### Preparing the Discord Bot

1. Create an application and add a Bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Copy the Bot token (`DISCORD_BOT_TOKEN`).
3. Invite the Bot to your server (required permissions: `Send Messages`, `Embed Links`, and `applications.commands` for slash commands).
4. Right-click the target channel and select **Copy Channel ID** (`DISCORD_CHANNEL_ID`).
   - For a forum thread, you can use the thread's own channel ID directly.

### Configuration

Copy the example environment file and configure the variables:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `ODPT_CONSUMER_KEY` | **(Required)** Your ODPT API key. | - |
| `DISCORD_BOT_TOKEN` | **(Required)** Your Discord Bot token. | - |
| `DISCORD_CHANNEL_ID` | **(Required)** ID of the channel (or thread) to post notifications to. | - |
| `AIRPORT` | 3-letter IATA airport code you want to monitor. | `HKD` |
| `MODE` | Notification mode (`arrivals`, `departures`, or `both`). | `both` |
| `POLL_INTERVAL_SEC` | How frequently to check the API (in seconds). | `180` |
| `NOTIFY_REMOVED` | Set to `1` to send an alert when a flight is removed. | `0` |
| `DISCORD_ALERT_COLUMN_NUM` | Number of columns in Discord notification embeds. | `3` |
| `STATE_FILE` | Location to store the current flight state. | `data/state_[airport].json` |
| `RUN_FOREVER` | Set to `0` to run the check exactly once and exit. | `1` |
| `STARTUP_NOTICE` | `1` to post a startup notice to Discord on launch, `0` to disable. | `1` |
| `STARTUP_LOGO_URL` | Optional image URL for the startup notice (shown as a thumbnail). | - |

## Slash Commands (Flight Watch Filter)

Once the Bot is running and invited to your server, you can manage which flights trigger notifications:

| Command | Description |
|---|---|
| `/watch <flight>` | Add a flight to the watch list (e.g. `/watch JL584`) |
| `/unwatch <flight>` | Remove a flight from the watch list |
| `/watchlist` | Display the current watch list |
| `/help` | Show available commands |

When the watch list is **empty**, all flights are notified (default behavior).
When flights are registered, **only those flights** will trigger notifications (codeshare numbers are also matched).
The list is persisted in `data/watch_list.json` and survives restarts.

## Usage

*Note: For a one-time execution (like in a cron job), set `RUN_FOREVER=0` in your `.env` file.*

### Run with Docker Compose
**Docker Compose with pre-built image: ⭐ Recommended**
```yaml
services:
  airport-monitor:
    image: ghcr.io/halka/odpt-japanese-airport-flight-monitor:latest
    # or image: halka/odpt-japanese-airport-flight-monitor:latest

    container_name: airport-monitor
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

### Run with Pre-built Docker Image

Instead of building locally, you can use the pre-built image from Docker Hub or GitHub Container Registry:

**From Docker Hub:**
```bash
mkdir -p data
docker run -d \
  --name airport-monitor \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  halka/odpt-japanese-airport-flight-monitor:latest
```

**From GitHub Container Registry:**
```bash
mkdir -p data
docker run -d \
  --name airport-monitor \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ghcr.io/halka/odpt-japanese-airport-flight-monitor:latest
```

### Running via Docker Compose
Ensure the `data` directory exists locally so state can persist.

```bash
mkdir -p data
docker compose up -d --build
```

You can view logs via:
```bash
docker compose logs -f
```

### Run with Docker

To build and run the Docker image yourself:

```bash
docker build -t airport-monitor .
mkdir -p data
docker run -d \
  --name airport-monitor \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  airport-monitor
```

### Run Natively
```bash
# 1) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies (upgrade build tooling is recommended)
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3) Configure environment and run
cp .env.example .env   # edit as needed
python monitor_airport.py
```

## Docker Image Tags

Images are automatically built and pushed to both Docker Hub and GitHub Container Registry when changes are pushed to the `main` branch.

### Available Tags:
- `latest` - Latest build from main branch
- `main` - Latest build from main branch
- Branch-specific tags (e.g., `main-abc123def`)
- Semantic version tags (e.g., `v1.0.0`, `1.0`)

### Docker Hub:
```bash
docker pull halka/odpt-japanese-airport-flight-monitor:latest
```

### GitHub Container Registry:
```bash
docker pull ghcr.io/halka/odpt-japanese-airport-flight-monitor:latest
```

## Author

- [halka](https://halka.jp)
  - [GitHub](https://github.com/halka)
  - [X](https://x.com/a_halka)

## License
©2026 halka

This software is released under the **MIT License**.

The data used in this project is provided by the Public Transport Open Data Center.

For details, please refer to the [Public Transport Open Data Center Terms of Use](https://rules.odpt.org/).
