# OGUser Monitor

Real-time monitoring tool for **OGUser.com** that tracks alerts and
private messages using an authenticated session. Designed for
low-latency event detection with reliable deduplication and instant
Telegram delivery.

------------------------------------------------------------------------

## Overview

OGUser Monitor continuously polls your account for:

-   Thread replies
-   Mentions / quotes
-   Reputation (rep/vouch) updates
-   Private messages

It leverages a browser-like TLS session to bypass Cloudflare protections
and operates without requiring API access.

------------------------------------------------------------------------

## Features

-   Real-time monitoring (default: 3s polling)
-   Telegram notifications (Markdown formatted)
-   Event deduplication via hashing
-   Session validation & error reporting
-   Cloudflare-aware requests using `tls_client`
-   Persistent state across restarts

------------------------------------------------------------------------

## Tech Stack

-   Python 3.10+
-   tls_client
-   requests
-   BeautifulSoup4

------------------------------------------------------------------------

## Installation

``` bash
git clone https://github.com/your-username/OGUser-monitor.git
cd OGUser-monitor
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Configuration

Edit the constants inside `OGUser-Monitor.py`:

``` python
OGUSER_TOKEN = "YOUR_OGUMYBBUSER_COOKIE"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
POLL_SECONDS = 3
```

------------------------------------------------------------------------

## Usage

``` bash
python OGUser-Monitor.py
```

------------------------------------------------------------------------

## How It Works

1.  Creates a TLS session mimicking Chrome
2.  Authenticates using your OGUser cookie
3.  Scrapes alerts and messages
4.  Parses and classifies events
5.  Generates a SHA-256 fingerprint per event
6.  Filters duplicates
7.  Sends notifications via Telegram API

------------------------------------------------------------------------

## State Management

-   Stored in `oguser_seen.json`
-   Prevents duplicate alerts between runs

------------------------------------------------------------------------

## Error Handling

Detects: - Invalid session - Cloudflare challenges - HTTP errors

Errors are sent via Telegram.

------------------------------------------------------------------------

## Security Considerations

-   Never commit sensitive data
-   Use environment variables in production
-   Treat cookies as credentials

------------------------------------------------------------------------

## License

MIT

------------------------------------------------------------------------

## Disclaimer

Not affiliated with OGUser. Use at your own risk.
