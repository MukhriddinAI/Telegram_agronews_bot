import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a single message to Telegram chat."""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Telegram xabari yuborishda xato: {e}")
        return False


def format_news_message(news_item: dict, index: int) -> str:
    """Format a single news item as a Telegram HTML message."""
    sarlavha = news_item.get("Sarlavha", "Sarlavha yo'q")
    matn = news_item.get("Yangilik matni", "")
    manba = news_item.get("Manba", "")

    message = f"<b>{index}. {sarlavha}</b>\n\n"
    message += f"{matn}\n\n"

    if manba and manba.startswith("http"):
        message += f'<a href="{manba}">Manbaga o\'tish</a>'
    elif manba:
        message += f"Manba: {manba}"

    return message


def send_daily_header() -> bool:
    """Send a header message before the news."""
    from datetime import datetime
    today = datetime.now().strftime("%d.%m.%Y")
    header = (
        f"<b>Kunlik Agro Yangiliklar</b>\n"
        f"{today}\n\n"
        f"Bugungi eng so'nggi 2 ta agro yangilik:"
    )
    return send_message(header)


def send_news_to_telegram(news_list: list) -> dict:
    """
    Send list of news items to Telegram.
    Returns a dict with success/failure counts.
    """
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        print("TELEGRAM_BOT_TOKEN .env faylida sozlanmagan!")
        return {"success": 0, "failed": 0, "error": "token_missing"}

    if not CHAT_ID or CHAT_ID == "your_chat_id_here":
        print("TELEGRAM_CHAT_ID .env faylida sozlanmagan!")
        return {"success": 0, "failed": 0, "error": "chat_id_missing"}

    if not news_list:
        print("Jo'natish uchun yangilik yo'q.")
        return {"success": 0, "failed": 0}

    # Send header
    send_daily_header()

    results = {"success": 0, "failed": 0}

    for i, news_item in enumerate(news_list[:2], start=1):  # faqat 2 ta
        message = format_news_message(news_item, i)
        ok = send_message(message)
        if ok:
            results["success"] += 1
            print(f"   Yangilik {i} muvaffaqiyatli jo'natildi.")
        else:
            results["failed"] += 1
            print(f"   Yangilik {i} jo'natilmadi!")

    return results


def validate_bot_connection() -> bool:
    """Check if bot token is valid by calling getMe."""
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        return False
    try:
        url = f"{TELEGRAM_API}/getMe"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("ok"):
            bot_name = data["result"].get("username", "")
            print(f"Bot ulangan: @{bot_name}")
            return True
        return False
    except requests.RequestException:
        return False
