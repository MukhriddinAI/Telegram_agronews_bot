import os
import json
import time
from datetime import datetime
from main import crew_run
from dotenv import load_dotenv
load_dotenv(override=True)
from telegram_sender import send_news_to_telegram, validate_bot_connection

# Configuration
MAX_RETRIES = 3
INITIAL_WAIT = 60  # seconds
BACKOFF_MULTIPLIER = 2


def parse_dirty_json(input_data):
    """
    Extracts and parses JSON from a string that might contain markdown or extra text.
    Handles both file paths and string inputs.
    """
    # If input_data is a file path, read it; otherwise, treat as string
    if isinstance(input_data, str) and os.path.exists(input_data):
        with open(input_data, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = str(input_data)

    # Try to find JSON array first
    start = text.find("[")
    end = text.rfind("]") + 1

    if start == -1 or end == 0:
        # Fallback for single objects if it's not a list
        start = text.find("{")
        end = text.rfind("}") + 1
        
    if start == -1 or end == 0:
        raise ValueError("No JSON structure found in the output.")

    clean_json = text[start:end]
    
    # Remove markdown code blocks if present
    clean_json = clean_json.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error: {e}")
        print(f"📄 Problematic JSON: {clean_json[:200]}...")
        raise


def save_results(results, filename=None):
    """
    Save parsed results to a JSON file.
    """
    if filename is None:
        filename = f"outputs/final_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    os.makedirs("outputs", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    return filename


def check_quota_error(error_msg):
    """
    Check if error is quota-related
    """
    quota_keywords = [
        "429",
        "RESOURCE_EXHAUSTED",
        "QUOTA",
        "RATE_LIMIT",
        "exceeded your current quota",
        "perdayperproject"
    ]
    error_upper = str(error_msg).upper()
    return any(keyword in error_upper for keyword in quota_keywords)


def is_daily_quota_exceeded(error_msg):
    """
    Check if this is a daily quota limit (not just RPM)
    """
    error_str = str(error_msg).lower()
    return ("perdayperproject" in error_str or 
            "quota exceeded for metric" in error_str or
            ("20" in error_str and "gemini-2.5-flash" in error_str))


# --- Main Execution Loop ---
def main():
    print("=" * 70)
    print("🌾 AGRO NEWS SCRAPER - EXECUTION STARTED")
    print("=" * 70)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Max Retries: {MAX_RETRIES}")
    print("=" * 70)

    # Check Telegram bot connection
    print("\n🤖 Telegram bot tekshirilmoqda...")
    if validate_bot_connection():
        print("✅ Telegram bot muvaffaqiyatli ulandi.\n")
    else:
        print("⚠️  Telegram bot ulanmadi. .env faylida TELEGRAM_BOT_TOKEN va TELEGRAM_CHAT_ID ni to'ldiring.\n")
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"\n🚀 Attempt {attempt + 1}/{MAX_RETRIES}: Running the crew workflow...")
            print("-" * 70)
            
            result = crew_run()
            
            print("\n" + "=" * 70)
            print("📊 PARSING RESULTS...")
            print("=" * 70)
            
            # Parse the result
            try:
                results = parse_dirty_json(result)
                print("✅ JSON parsed successfully!")
                
                # Display results
                print("\n📰 PARSED NEWS ARTICLES:")
                print("-" * 70)
                if isinstance(results, list):
                    for idx, news in enumerate(results, 1):
                        print(f"\n{idx}. {news.get('Sarlavha', 'No title')}")
                        print(f"   Manba: {news.get('Manba', 'No source')}")
                else:
                    print(json.dumps(results, ensure_ascii=False, indent=2))
                
                # Save results
                saved_file = save_results(results)

                # Send top 2 news to Telegram
                print("\n" + "=" * 70)
                print("📨 TELEGRAM BOTGA JO'NATILMOQDA...")
                print("=" * 70)
                top2 = results[:2] if isinstance(results, list) else []
                if top2:
                    tg_result = send_news_to_telegram(top2)
                    if tg_result.get("error"):
                        print(f"⚠️  Telegram xatosi: {tg_result['error']}")
                    else:
                        print(f"✅ Telegram: {tg_result['success']} ta jo'natildi, "
                              f"{tg_result['failed']} ta xato.")
                else:
                    print("⚠️  Jo'natish uchun yangilik topilmadi.")

                print("\n" + "=" * 70)
                print("✅ TASK COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print(f"📁 Output file: {saved_file}")
                print(f"⏰ Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70)

                return results  # Success - exit the loop
                
            except (ValueError, json.JSONDecodeError) as parse_error:
                print(f"⚠️ JSON parsing failed: {parse_error}")
                print("\n📄 Raw output:")
                print(str(result)[:500])
                
                if attempt < MAX_RETRIES - 1:
                    print("\n🔄 Retrying the entire workflow...")
                    time.sleep(10)
                    continue
                else:
                    print("\n❌ All retry attempts exhausted.")
                    raise

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Error occurred: {error_msg[:200]}")
            
            # Check if it's a quota error
            if check_quota_error(error_msg):
                # Check if it's daily quota (not recoverable by waiting)
                if is_daily_quota_exceeded(error_msg):
                    print("\n" + "=" * 70)
                    print("🚫 DAILY QUOTA EXCEEDED")
                    print("=" * 70)
                    print("📊 Status: You've used all available requests for today")
                    print("⏰ Quota Reset: Midnight Pacific Time")
                    print("💡 Solutions:")
                    print("   1. Wait until quota resets (tomorrow)")
                    print("   2. Upgrade to paid tier")
                    print("   3. Use a different Google Cloud project")
                    print("=" * 70)
                    break  # Don't retry on daily quota
                else:
                    # RPM limit - retry with backoff
                    wait_time = INITIAL_WAIT * (BACKOFF_MULTIPLIER ** attempt)
                    print(f"\n⚠️ Rate limit hit. Waiting {wait_time} seconds before retry...")
                    print(f"🔄 Retry {attempt + 1}/{MAX_RETRIES}")
                    
                    # Countdown
                    for remaining in range(wait_time, 0, -10):
                        print(f"⏳ {remaining} seconds remaining...", end='\r')
                        time.sleep(10)
                    
                    print("\n🔄 Retrying now...")
            else:
                # Non-quota error
                print(f"\n❌ Unexpected error: {error_msg}")
                if attempt < MAX_RETRIES - 1:
                    print(f"🔄 Retrying in 30 seconds...")
                    time.sleep(30)
                else:
                    print("\n💡 Suggestions:")
                    print("   1. Check your internet connection")
                    print("   2. Verify DuckDuckGo search is working")
                    print("   3. Review error logs above")
                    break
    
    print("\n" + "=" * 70)
    print("❌ EXECUTION FAILED AFTER ALL RETRY ATTEMPTS")
    print("=" * 70)
    return None


if __name__ == "__main__":
    result = main()
    if result is None:
        exit(1)  # Exit with error code
    else:
        exit(0)  # Exit successfully