#!/usr/bin/env python3
"""
Diagnostic script to check API configuration and quota status.
Run directly: python check_quota.py
"""

import os
from dotenv import load_dotenv
import litellm
from config import GEMINI_MODELS


def main():
    load_dotenv()

    print("=" * 70)
    print("AGRO NEWS SCRAPER - DIAGNOSTIC CHECK")
    print("=" * 70)

    # 1. Check environment variables
    print("\n1. Checking Environment Variables...")
    print("-" * 70)

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
        print(f"GOOGLE_API_KEY found: {masked_key}")
    else:
        print("GOOGLE_API_KEY not found!")
        print("   Please create a .env file with your API key")
        raise SystemExit(1)

    # 2. Test LLM initialization
    print("\n2. Testing LLM Initialization...")
    print("-" * 70)

    working_models = []

    for model, description in GEMINI_MODELS:
        try:
            print(f"\nTesting: {description}")
            print(f"   Model: {model}")

            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                api_key=api_key,
            )

            print("   SUCCESS - Model is working!")
            working_models.append((model, description))

        except Exception as e:
            error_msg = str(e)

            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print("   QUOTA EXCEEDED")
                print("   This model is out of quota but might work tomorrow")
            elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                print("   AUTHENTICATION FAILED")
                print("   Check your API key")
            else:
                print(f"   FAILED: {error_msg[:100]}")

    # 3. Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    if working_models:
        print(f"\n{len(working_models)} model(s) available:")
        for model, desc in working_models:
            print(f"   - {desc}")
        print("\nRecommendation: Use the first available model")
        print("   Your workflow should work fine!")
    else:
        print("\nNo models available")
        print("\nPossible reasons:")
        print("   1. Daily quota exceeded (wait until midnight PT)")
        print("   2. Invalid API key")
        print("   3. API key not enabled for Gemini")
        print("\nUseful links:")
        print("   - Check quota: https://ai.dev/rate-limit")
        print("   - Get API key: https://aistudio.google.com/app/apikey")
        print("   - Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits")

    # 4. Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)

    if working_models:
        print("\nYou're ready to run the scraper!")
        print("\n   Run: python run.py")
    else:
        print("\nIf quota is exceeded:")
        print("   - Wait until tomorrow (quota resets midnight PT)")
        print("   - Or get a new API key from different Google account")
        print("\nIf API key issue:")
        print("   - Verify key at: https://aistudio.google.com/app/apikey")
        print("   - Make sure Gemini API is enabled")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
