from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import requests
import tls_client
from bs4 import BeautifulSoup


BASE_URL = "https://oguser.com"
ALERTS_URL = f"{BASE_URL}/alerts.php"
MESSAGES_URL = f"{BASE_URL}/messages"
STATE_FILE = Path("oguser_seen.json")

# ================= CONFIG FIXA =================
OGUSER_TOKEN: str = "YOUR_OGUMYBBUSER_COOKIE"
TELEGRAM_BOT_TOKEN: str = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID: str = "YOUR_TELEGRAM_CHAT_ID"
POLL_SECONDS: int = 3
# ==============================================


class OguserMonitor:
    def __init__(self) -> None:
        self.session = self.create_session()
        self.seen = self.load_seen()

    def create_session(self) -> tls_client.Session:
        session = tls_client.Session(
            client_identifier="chrome_112",
            random_tls_extension_order=True,
        )
        session.cookies.set("ogumybbuser", OGUSER_TOKEN)
        return session

    def run(self) -> None:
        while True:
            try:
                events = [
                    *self.fetch_alerts(),
                    *self.fetch_private_messages(),
                ]

                for event in events:
                    event_id = self.fingerprint(event)

                    if event_id in self.seen:
                        continue

                    self.seen.add(event_id)
                    self.notify(event)

                self.save_seen()

            except Exception as exc:
                self.notify(
                    {
                        "type": "Erro no monitor",
                        "text": repr(exc),
                        "url": BASE_URL,
                    }
                )

            time.sleep(POLL_SECONDS)

    def fetch_alerts(self) -> list[dict[str, str]]:
        response = self.get(ALERTS_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        nodes = soup.select(".alert, .alerts, .myalerts_alert, li, tr")

        alerts: list[dict[str, str]] = []

        for node in nodes:
            raw_text = " ".join(node.get_text(" ", strip=True).split())
            text = self.clean_alert_text(raw_text)

            if not text:
                continue

            alert_type = self.classify_alert(text)
            if alert_type is None:
                continue

            link = node.find("a", href=True)
            url = self.normalize_url(link.get("href") if link else None)

            alerts.append(
                {
                    "type": alert_type,
                    "text": text,
                    "url": url,
                }
            )

        return self.deduplicate(alerts)

    def fetch_private_messages(self) -> list[dict[str, str]]:
        response = self.get(MESSAGES_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tr, li, .conversation, .conversation-row, .message-row")
        messages: list[dict[str, str]] = []

        for row in rows:
            text = " ".join(row.get_text(" ", strip=True).split())

            if not text or self.should_ignore_message_row(text):
                continue

            parsed = self.parse_message_row(text)

            if parsed is None:
                continue

            username, preview = parsed

            messages.append(
                {
                    "type": "Private Message",
                    "text": f'{username} chat message: "{preview}"',
                    "url": f"{BASE_URL}/{username}",
                }
            )

        return self.deduplicate(messages)

    def get(self, url: str) -> Any:
        response = self.session.get(url)

        if response.status_code == 403:
            raise RuntimeError("403 Forbidden: Cloudflare ou cookie inválido")

        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code}: {response.text[:300]}"
            )

        if "Just a moment" in response.text:
            raise RuntimeError("Cloudflare challenge retornado")

        if "login" in response.url.lower():
            raise RuntimeError("Sessão inválida: redirecionado para login")

        return response

    def classify_alert(self, text: str) -> str | None:
        value = text.lower()

        rules: dict[str, list[str]] = {
            "Thread reply": [
                "replied",
                "reply",
                "posted",
                "responded",
            ],
            "Thread mention": [
                "mentioned",
                "tagged",
                "quoted",
            ],
            "Rep / vouch update": [
                "reputation",
                "rep",
                "vouch",
                "vouched",
                "rating",
            ],
        }

        for alert_type, keywords in rules.items():
            if any(keyword in value for keyword in keywords):
                return alert_type

        return None

    def notify(self, event: dict[str, str]) -> None:
        text = (
            f"*{self.escape_md(event['type'])}*\n"
            f"{self.escape_md(event['text'])}\n\n"
            f"{event['url']}"
        )

        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        response.raise_for_status()

    @staticmethod
    def parse_message_row(text: str) -> tuple[str, str] | None:
        text = " ".join(text.split())

        text = re.sub(
            r"\s+\d+\s+(?:seconds?|minutes?|hours?|days?)\s+ago$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\s+Today\s*,\s*\d{1,2}:\d{2}\s*(?:AM|PM)$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\s+Yesterday\s*,\s*\d{1,2}:\d{2}\s*(?:AM|PM)$",
            "",
            text,
            flags=re.IGNORECASE,
        )

        parts = text.split()

        while parts and parts[0].isdigit():
            parts.pop(0)

        if len(parts) < 2:
            return None

        username = parts[0].strip()
        preview = " ".join(parts[1:]).strip()

        if not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
            return None

        if not username or not preview:
            return None

        return username, preview

    @staticmethod
    def clean_alert_text(text: str) -> str:
        remove_phrases = [
            "There may be more posts after this.",
            "Delete",
            "Today",
            "Yesterday",
        ]

        cleaned = text

        for phrase in remove_phrases:
            cleaned = cleaned.replace(phrase, "")

        return " ".join(cleaned.split()).strip()

    @staticmethod
    def should_ignore_message_row(text: str) -> bool:
        value = text.lower().strip()

        ignored_exact = {
            "messages",
            "messages messages",
            "new conversation",
            "delete conversation",
            "delete conversation(s)",
            "export",
            "browse",
            "usernames",
            "stats",
            "gaming",
            "services",
            "upgrade",
            "credits",
            "awards",
            "extras",
            "support",
            "members",
            "top members",
            "purchase sticky",
            "purchase extras",
            "team",
            "advanced search",
            "sell",
            "explore",
            "profile",
            "control panel",
            "threads",
            "logout",
            "home",
            "search",
            "more",
            "ogu",
        }

        ignored_contains = [
            "conversations are automatically deleted",
            "select all",
            "inbox",
            "sent",
            "drafts",
            "trash",
            "compose",
        ]

        if value in ignored_exact:
            return True

        return any(item in value for item in ignored_contains)

    @staticmethod
    def deduplicate(events: list[dict[str, str]]) -> list[dict[str, str]]:
        unique: dict[str, dict[str, str]] = {}

        for event in events:
            key = f"{event['type']}|{event['text']}|{event['url']}"
            unique[key] = event

        return list(unique.values())

    @staticmethod
    def normalize_url(path_or_url: str | None) -> str:
        if not path_or_url:
            return BASE_URL

        if path_or_url.startswith(("http://", "https://")):
            return path_or_url

        if not path_or_url.startswith("/"):
            path_or_url = f"/{path_or_url}"

        return f"{BASE_URL}{path_or_url}"

    @staticmethod
    def escape_md(value: str) -> str:
        return (
            value.replace("_", "\\_")
            .replace("*", "\\*")
            .replace("`", "\\`")
        )

    @staticmethod
    def fingerprint(event: dict[str, str]) -> str:
        payload = json.dumps(event, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def load_seen() -> set[str]:
        if not STATE_FILE.exists():
            return set()

        try:
            content = STATE_FILE.read_text(encoding="utf-8").strip()

            if not content:
                return set()

            data: Any = json.loads(content)
            return set(data)

        except json.JSONDecodeError:
            STATE_FILE.write_text("[]", encoding="utf-8")
            return set()

    def save_seen(self) -> None:
        STATE_FILE.write_text(
            json.dumps(sorted(self.seen), indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    OguserMonitor().run()