# ODPT Airport Flight Monitor

This Python script monitors flight arrival and departure information for a specific airport using the Public Transport Open Data Center (ODPT) API and sends notifications to Discord when changes are detected.

## Key Features

- **Real-time Monitoring**: Fetches the latest flight information using the ODPT API.
- **Differential Notifications**: Compares current data with previous state to detect and notify about new flights, status changes, or removals (optional).
- **Discord Integration**: Sends notifications via Discord Webhooks using rich Embed formats.
- **Flexible Configuration**: Choose to monitor arrivals, departures, or both.
- **Multiple Environments**: Easily runs via Python natively, Docker, or Docker Compose.

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

## Usage

*Note: For a one-time execution (like in a cron job), set `RUN_FOREVER=0` in your `.env` file.*

### Run with Docker Compose ⭐️Recommended

Running via Docker Compose is recommended for continuous, background execution. Ensure the `data` directory exists locally so state can persist.

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

### Run Natively 😇As You Like
```bash
cd ODPT-Japanese-Airport-Flight-Monitor/
cp .env.example .env
# edit .env then
python -m venv .
source bin/activate
pip -r install requirements.txt
python monitor_airport.py
```

## Author

- [halka](https://halka.jp)
  - [GitHub](https://github.com/halka)
  - [X](https://x.com/a_halka)

## License

This software is released under the **MIT License**.

The data used in this project is provided by the Public Transport Open Data Center.

For details, please refer to the [Public Transport Open Data Center Terms of Use](https://rules.odpt.org/).
