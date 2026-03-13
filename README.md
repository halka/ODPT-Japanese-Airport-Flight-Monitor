言語: 日本語 | [English](README.en.md)

# ODPT Japanese Airport Flight Monitor

このプロジェクトは、公共交通オープンデータセンター（ODPT）の API を利用して特定空港の到着・出発情報を取得し、変更を検知すると Discord に通知します。
![Hero](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/hero-image.png)

## 主な機能

- **リアルタイム監視**: ODPT API を用いて最新のフライト情報を取得します。
- **差分通知**: 直前の状態と比較し、新規便・ステータス変更・削除（任意）を検出して通知します。
- **Discord 連携**: Discord Webhook を使い、リッチな Embed 形式で通知します。
- **柔軟な設定**: 到着・出発・両方のいずれかを選んで監視できます。
- **複数の実行方法**: Python（ネイティブ）、Docker、Docker Compose に対応。

## スクリーンショット
![1](https://raw.githubusercontent.com/halka/ODPT-Japanese-Airport-Flight-Monitor/refs/heads/main/assets/images/sample1.jpg)

## セットアップ

### 前提条件
- Docker と Docker Compose
- [公共交通オープンデータセンター（ODPT）](https://developer.odpt.org/) の API キー（Consumer Key）
- Discord Webhook URL

### 設定

サンプル環境ファイルをコピーし、各変数を設定します:

```bash
cp .env.example .env
```

| 変数 | 説明 | 既定値 |
|------|------|--------|
| `ODPT_CONSUMER_KEY` | 【必須】ODPT の API キー。 | - |
| `DISCORD_WEBHOOK_URL` | 【必須】Discord の Webhook URL。 | - |
| `AIRPORT` | 監視対象の IATA 空港コード（3 文字）。 | `HKD` |
| `MODE` | 通知モード（`arrivals` / `departures` / `both`）。 | `both` |
| `POLL_INTERVAL_SEC` | API をポーリングする間隔（秒）。 | `180` |
| `NOTIFY_REMOVED` | 便が削除された際にも通知するなら `1`。 | `0` |
| `DISCORD_ALERT_COLUMN_NUM` | Discord 通知のカラム数。 | `3` |
| `DISCORD_THREAD_ID` | フォーラム/スレッドに投稿する場合の任意の ID。 | - |
| `STATE_FILE` | 現在のフライト状態を保存するファイルの場所。 | `data/state_[airport].json` |
| `RUN_FOREVER` | `0` にすると 1 回だけ実行して終了。 | `1` |
| `STARTUP_NOTICE` | 起動時に Discord へ通知するなら `1`、無効は `0`。 | `1` |
| `STARTUP_LOGO_URL` | 起動通知のサムネイルに使う任意の画像 URL。 | - |

## 使い方

※ 単発実行（cron など）を行う場合は `.env` の `RUN_FOREVER=0` を設定してください。

### Docker Compose で実行（推奨・事前ビルド済みイメージ）
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

### 事前ビルド済み Docker イメージで実行

ローカルでビルドせず、Docker Hub または GitHub Container Registry の事前ビルド済みイメージを利用できます。

**Docker Hub から:**
```bash
mkdir -p data
docker run -d \
  --name airport-monitor \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  halka/odpt-japanese-airport-flight-monitor:latest
```

**GitHub Container Registry から:**
```bash
mkdir -p data
docker run -d \
  --name airport-monitor \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ghcr.io/halka/odpt-japanese-airport-flight-monitor:latest
```

### Docker Compose での実行（ビルド/起動）
ローカルに `data` ディレクトリを作成しておくと状態が永続化されます。

```bash
mkdir -p data
docker compose up -d --build
```

ログの確認:
```bash
docker compose logs -f
```

### Docker で実行（ローカルビルド）

自分で Docker イメージをビルドして実行する場合:

```bash
docker build -t airport-monitor .
mkdir -p data
docker run -d \
  --name airport-monitor \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  airport-monitor
```

### ローカル環境で実行（ネイティブ）
```bash
# 1) 仮想環境を作成・有効化
python3 -m venv .venv
source .venv/bin/activate

# 2) 依存パッケージをインストール（ビルド系ツールの更新を推奨）
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3) 環境を設定して起動
cp .env.example .env   # 必要に応じて編集
python monitor_airport.py
```

## Docker イメージのタグ

`main` ブランチへ変更が push されると、Docker Hub と GitHub Container Registry の両方に自動でビルド・公開されます。

### 利用可能なタグ
- `latest` - main ブランチからの最新ビルド
- `main` - main ブランチからの最新ビルド
- ブランチ固有タグ（例: `main-abc123def`）
- セマンティックバージョン（例: `v1.0.0`, `1.0`）

### Docker Hub:
```bash
docker pull halka/odpt-japanese-airport-flight-monitor:latest
```

### GitHub Container Registry:
```bash
docker pull ghcr.io/halka/odpt-japanese-airport-flight-monitor:latest
```

## 作者

- [halka](https://halka.jp)
  - [GitHub](https://github.com/halka)
  - [X](https://x.com/a_halka)

## ライセンス
©2026 halka

このソフトウェアは **MIT License** の下で提供されます。

本プロジェクトで利用するデータは公共交通オープンデータセンターにより提供されています。

詳細は [公共交通オープンデータセンター 利用規約](https://rules.odpt.org/) をご確認ください。
