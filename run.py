import os
import json
import logging
import time
import tracemalloc
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from config import SEPARATOR, OUTPUTS_DIR, QUOTA_KEYWORDS
from main import crew_run
from telegram_sender import send_news_to_telegram, validate_bot_connection

MAX_RETRIES = 3
INITIAL_WAIT = 1       # base wait in seconds (doubles each attempt: 1, 2, 4, …)
BACKOFF_MULTIPLIER = 2

logger = logging.getLogger(__name__)


def _backoff_wait(attempt: int) -> None:
    """Sleep 1s, 2s, 4s … based on attempt index (0-based)."""
    wait = INITIAL_WAIT * (BACKOFF_MULTIPLIER ** attempt)
    logger.info("Waiting %d second(s) before retry (attempt %d/%d)...", wait, attempt + 1, MAX_RETRIES)
    time.sleep(wait)


_FAKE_CONTENT_PHRASES = [
    "yangilik topilmadi",
    "xabarlar topilmadi",
    "yangi xabarlar topilmadi",
    "bugun yangi xabar",
    "qidiruv jarayonida",
    "ma'lumotlar bazasida yangi",
    "vaqtincha mavjud emas",
    "no news found",
    "no results found",
]

def is_fake_results(results: list) -> bool:
    """Return True if ALL items look like hallucinated 'no news found' placeholders."""
    if not results:
        return True
    fake_count = 0
    for item in results:
        combined = (item.get("Sarlavha", "") + " " + item.get("Yangilik matni", "")).lower()
        if any(phrase in combined for phrase in _FAKE_CONTENT_PHRASES):
            fake_count += 1
    return fake_count == len(results)



def save_results(results, filename=None):
    """Save parsed results to a JSON file."""
    if filename is None:
        filename = f"{OUTPUTS_DIR}/final_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info("Results saved to: %s", filename)
    return filename


def check_quota_error(error_msg):
    error_upper = str(error_msg).upper()
    return any(kw in error_upper for kw in QUOTA_KEYWORDS)


def is_daily_quota_exceeded(error_msg):
    error_str = str(error_msg).lower()
    return (
        "perdayperproject" in error_str
        or "quota exceeded for metric" in error_str
    )


def main():
    tracemalloc.start()
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )

    logger.info(SEPARATOR)
    logger.info("AGRO NEWS SCRAPER - EXECUTION STARTED")
    logger.info("Start Time: %s | Max Retries: %d", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), MAX_RETRIES)
    logger.info(SEPARATOR)

    logger.info("Telegram bot tekshirilmoqda...")
    if validate_bot_connection():
        logger.info("Telegram bot muvaffaqiyatli ulandi.")
    else:
        logger.warning("Telegram bot ulanmadi. .env faylida TELEGRAM_BOT_TOKEN va TELEGRAM_CHAT_ID ni to'ldiring.")

    for attempt in range(MAX_RETRIES):
        try:
            logger.info("Attempt %d/%d: Running the crew workflow...", attempt + 1, MAX_RETRIES)
            results = crew_run()

            if not isinstance(results, list) or not results:
                raise ValueError("crew_run() returned empty or invalid results")

            if is_fake_results(results):
                logger.warning("Soxta 'yangilik topilmadi' mazmun aniqlandi. Qayta urinilmoqda...")
                if attempt < MAX_RETRIES - 1:
                    _backoff_wait(attempt)
                    continue
                else:
                    logger.error("Barcha urinishlardan keyin ham haqiqiy yangilik topilmadi.")
                    return None

            saved_file = save_results(results)

            print("\n" + "=" * 70)
            print("SUMMARIZER AGENTI - FINAL NATIJA")
            print("=" * 70)
            for idx, news in enumerate(results, 1):
                print(f"\n[{idx}] {news.get('Sarlavha', '—')}")
                print(f"    {news.get('Yangilik matni', '—')}")
                print(f"    Manba: {news.get('Manba', '—')}")
            print("\n" + "=" * 70)
            print(f"Saqlandi: {saved_file}")
            print("=" * 70)

            logger.info("Sending to Telegram...")
            tg_result = send_news_to_telegram(results)
            if tg_result.get("error"):
                logger.warning("Telegram xatosi: %s", tg_result["error"])
            else:
                logger.info("Telegram: %d sent, %d failed.", tg_result["success"], tg_result["failed"])

            logger.info("TASK COMPLETED SUCCESSFULLY — output: %s | time: %s",
                        saved_file, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return results

        except (ValueError, json.JSONDecodeError) as parse_error:
            logger.warning("JSON parsing failed: %s", parse_error)
            if attempt < MAX_RETRIES - 1:
                _backoff_wait(attempt)
            else:
                logger.error("All retry attempts exhausted.")
                raise

        except Exception as e:
            error_msg = str(e)
            logger.error("Error occurred: %s", error_msg[:200])

            if check_quota_error(error_msg):
                if is_daily_quota_exceeded(error_msg):
                    logger.error(
                        "DAILY QUOTA EXCEEDED — quota resets at midnight Pacific Time. "
                        "Wait until tomorrow or upgrade to paid tier."
                    )
                    break
                else:
                    logger.warning("Rate limit hit.")
                    _backoff_wait(attempt)
            else:
                if attempt < MAX_RETRIES - 1:
                    _backoff_wait(attempt)
                else:
                    logger.error("All retry attempts exhausted.")
                    break

    logger.error("EXECUTION FAILED AFTER ALL RETRY ATTEMPTS")
    return None


if __name__ == "__main__":
    result = main()
    raise SystemExit(0 if result is not None else 1)
