import os
import re
import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

_PLACEHOLDER_TOKEN = "TELEGRAM_BOT_TOKEN"
_PLACEHOLDER_CHAT = "TELEGRAM_CHAT_ID"


def _get_config():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    api_base = f"https://api.telegram.org/bot{token}"
    return token, chat_id, api_base


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a single message to Telegram chat."""
    _, chat_id, api_base = _get_config()
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }
    try:
        response = requests.post(f"{api_base}/sendMessage", json=payload, timeout=15)
        if response.status_code != 200:
            logger.error(f"Telegram Error: {response.text}") # Bu yerda Bad Request sababi yoziladi
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return False


def _escape_html(text: str) -> str:
    """Escape HTML special characters in plain text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _clean_url(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""
    
    # AI ba'zan [text](link) ko'rinishida beradi, shuni ajratib olish
    match = re.search(r'(https?://[^\s)\]]+)', url)
    if match:
        found_url = match.group(1)
        # Oxiridagi keraksiz tinish belgilarini olib tashlash
        return found_url.rstrip('.,;:-"\') ]')
    return ""


def format_news_message(news_item: dict, index: int) -> str:
    sarlavha = news_item.get("Sarlavha", "Sarlavha yo'q")
    matn = news_item.get("Yangilik matni", "")
    manba = news_item.get("Manba", "")

    # Sarlavha va matnni tozalash
    safe_title = _escape_html(str(sarlavha))
    safe_text = _escape_html(str(matn))
    
    message = f"<b>{index}. {safe_title}</b>\n\n{safe_text}\n\n"

    clean_url = _clean_url(manba)
    if clean_url:
        # URL ichidagi maxsus belgilarni Telegram HTML uchun tozalash
        # Ayniqsa &, <, > belgilari href ichida ham muammo tug'diradi
        html_url = clean_url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        message += f'<a href="{html_url}">👉 Manbaga o\'tish</a>'
    elif manba:
        message += f"<i>Manba:</i> {_escape_html(str(manba))}"
    
    return message


def send_daily_header() -> bool:
    """Send a header message before the news."""
    today = datetime.now().strftime("%d.%m.%Y")
    header = (
        f"<b>Kunlik Agro Yangiliklar</b>\n"
        f"{today}\n\n"
        f"Bugungi eng so'nggi 2 ta agro yangilik:"
    )
    return send_message(header)


def send_news_to_telegram(news_list: list) -> dict:
    """Send list of news items to Telegram. Returns success/failure counts."""
    token, chat_id, _ = _get_config()

    if not token or token == _PLACEHOLDER_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN .env faylida sozlanmagan!")
        return {"success": 0, "failed": 0, "error": "token_missing"}

    if not chat_id or chat_id == _PLACEHOLDER_CHAT:
        logger.warning("TELEGRAM_CHAT_ID .env faylida sozlanmagan!")
        return {"success": 0, "failed": 0, "error": "chat_id_missing"}

    if not news_list:
        logger.warning("Jo'natish uchun yangilik yo'q.")
        return {"success": 0, "failed": 0}

    if not send_daily_header():
        logger.warning("Telegram header xabari jo'natilmadi.")
    results = {"success": 0, "failed": 0}

    for i, news_item in enumerate(news_list[:2], start=1):
        if send_message(format_news_message(news_item, i)):
            results["success"] += 1
            logger.info("Yangilik %d muvaffaqiyatli jo'natildi.", i)
        else:
            results["failed"] += 1
            logger.error("Yangilik %d jo'natilmadi!", i)
        time.sleep(1)  # Telegram rate limit: 1 message/second per chat

    return results


def validate_bot_connection() -> bool:
    """Check if bot token is valid by calling getMe."""
    token, _, api_base = _get_config()
    if not token or token == _PLACEHOLDER_TOKEN:
        return False
    try:
        data = requests.get(f"{api_base}/getMe", timeout=10).json()
        if data.get("ok"):
            logger.info("Bot ulangan: @%s", data["result"].get("username", ""))
            return True
        return False
    except requests.RequestException:
        return False
