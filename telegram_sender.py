import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

_PLACEHOLDER_TOKEN = "your_telegram_bot_token_here"
_PLACEHOLDER_CHAT = "your_chat_id_here"


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
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error("Telegram xabari yuborishda xato: %s", e)
        return False


def format_news_message(news_item: dict, index: int) -> str:
    """Format a single news item as a Telegram HTML message."""
    sarlavha = news_item.get("Sarlavha", "Sarlavha yo'q")
    matn = news_item.get("Yangilik matni", "")
    manba = news_item.get("Manba", "")

    message = f"<b>{index}. {sarlavha}</b>\n\n{matn}\n\n"
    if manba and manba.startswith("http"):
        message += f'<a href="{manba}">Manbaga o\'tish</a>'
    elif manba:
        message += f"Manba: {manba}"
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

    send_daily_header()
    results = {"success": 0, "failed": 0}

    for i, news_item in enumerate(news_list[:2], start=1):
        if send_message(format_news_message(news_item, i)):
            results["success"] += 1
            logger.info("Yangilik %d muvaffaqiyatli jo'natildi.", i)
        else:
            results["failed"] += 1
            logger.error("Yangilik %d jo'natilmadi!", i)

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
