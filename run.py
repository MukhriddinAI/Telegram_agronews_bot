import os
import json
import logging
import time
import re
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(override=True)

from config import SEPARATOR, OUTPUTS_DIR, QUOTA_KEYWORDS
from main import crew_run
from telegram_sender import send_news_to_telegram, validate_bot_connection

MAX_RETRIES = 3
INITIAL_WAIT = 60
BACKOFF_MULTIPLIER = 2

logger = logging.getLogger(__name__)


def parse_dirty_json(input_data):
    """Extract and parse JSON from a string that may contain markdown or extra text.
    Always returns a list."""
    text = str(input_data)

    start = text.find("[")
    end = text.rfind("]") + 1

    if start == -1 or end == 0:
        start = text.find("{")
        end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No JSON structure found in the output.")

    clean_json = text[start:end].replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(clean_json)
        return result if isinstance(result, list) else [result]
    except json.JSONDecodeError as e:
        logger.warning("JSON parsing error: %s | snippet: %s", e, clean_json[:200])
        raise


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

_HALLUCINATED_URL_PATTERN = re.compile(r'-\d{5,}(?:\.aspx|\.html|/)?$')


def _is_likely_hallucinated(url: str) -> bool:
    """Detect if a URL looks like an LLM hallucination (long numeric ID at the end)."""
    if not url:
        return False
    path = urlparse(url).path
    return bool(_HALLUCINATED_URL_PATTERN.search(path))


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


def sanitize_urls(results: list) -> list:
    """If a URL looks hallucinated, fall back to just the base domain."""
    for item in results:
        url = item.get("Manba", "")
        if url and _is_likely_hallucinated(url):
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            logger.warning("Hallucinated URL detected, falling back to domain: %s -> %s", url, base)
            item["Manba"] = base
    return results


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
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"{OUTPUTS_DIR}/app.log", encoding="utf-8"),
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
            result = crew_run()

            results = parse_dirty_json(result)
            results = sanitize_urls(results)

            if is_fake_results(results):
                logger.warning("Soxta 'yangilik topilmadi' mazmun aniqlandi. Qayta urinilmoqda...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(10)
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
                logger.info("Retrying workflow in 10 seconds...")
                time.sleep(10)
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
                    wait_time = INITIAL_WAIT * (BACKOFF_MULTIPLIER ** attempt)
                    logger.warning("Rate limit hit. Waiting %d seconds...", wait_time)
                    for remaining in range(wait_time, 0, -10):
                        print(f"\r⏳ {remaining}s remaining...", end="", flush=True)
                        time.sleep(10)
                    print()
                    logger.info("Retrying now...")
            else:
                if attempt < MAX_RETRIES - 1:
                    logger.info("Unexpected error. Retrying in 30 seconds...")
                    time.sleep(30)
                else:
                    logger.error("All retry attempts exhausted.")
                    break

    logger.error("EXECUTION FAILED AFTER ALL RETRY ATTEMPTS")
    return None


if __name__ == "__main__":
    result = main()
    raise SystemExit(0 if result is not None else 1)
