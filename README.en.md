Language: [日本語](README.md) | English

# ODPT Japanese Airport Flight Monitor

This is a flight arrival and departure information for a specific airport using the Public Transport Open Data Center (ODPT) API and sends notifications to Discord when changes are detected.
![Hero](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/hero-image.png)
## Key Features

- **Real-time Monitoring**: Fetches the latest flight information using the ODPT API.
- **Differential Notifications**: Compares current data with previous state to detect and notify about new flights, status changes, or removals (optional).
- **Discord Integration**: Sends notifications via Discord Webhooks using rich Embed formats.
- **Flexible Configuration**: Choose to monitor arrivals, departures, or both.
- **Multiple Environments**: Easily runs via Python natively, Docker, or Docker Compose.

## Screenshots
![1](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/sample1.jpg)

## Setup

### Prerequisites
- Docker and Docker Compose
- [Public Transport Open Data Center](https://developer.odpt.org/) API Key (Consumer Key)
- Discord Webhook URL

### Configuration

Copy the example environment file and configure the variables:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `ODPT_CONSUMER_KEY` | **(Required)** Your ODPT API key. | - |
| `DISCORD_WEBHOOK_URL` | **(Required)** Your Discord webhook URL. | - |
| `AIRPORT` | 3-letter IATA airport code you want to monitor. | `HKD` |
| `MODE` | Notification mode (`arrivals`, `departures`, or `both`). | `both` |
| `POLL_INTERVAL_SEC` | How frequently to check the API (in seconds). | `180` |
| `NOTIFY_REMOVED` | Set to `1` to send an alert when a flight is removed. | `0` |
| `DISCORD_ALERT_COLUMN_NUM` | Set Column's of Discord Notification | `3` |
| `DISCORD_THREAD_ID` | Optional ID for Forum/Thread posting. | - |
| `STATE_FILE` | Location to store the current flight state. | `data/state_[airport].json` |
| `RUN_FOREVER` | Set to `0` to run the check exactly once and exit. | `1` |
| `STARTUP_NOTICE` | `1` to post a startup notice to Discord on launch, `0` to disable. | `1` |
| `STARTUP_LOGO_URL` | Optional image URL for the startup notice (shown as a thumbnail). | - |

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
