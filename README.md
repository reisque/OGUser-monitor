# OGUser Monitor

Real-time monitor for OGUser that tracks alerts and private messages using an authenticated session (cookie-based). Designed to bypass Cloudflare protections and deliver instant Telegram notifications with minimal latency.

## Features

- Tracks:
  - Thread replies
  - Mentions / tags
  - Reputation / vouch updates
  - Private messages
- High-frequency polling (default: 3 seconds)
- Deduplication to prevent repeated alerts
- Telegram integration (Markdown formatted messages)
- Automatic session validation and error reporting

## Requirements

- Python 3.10+
- Valid OGUser session cookie (`ogumybbuser`)
- Telegram bot token and chat ID

## Installation

```bash
pip install -r requirements.txt
