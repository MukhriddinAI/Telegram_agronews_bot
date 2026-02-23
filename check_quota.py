#!/usr/bin/env python3
"""
Diagnostic script to check API configuration and quota status
"""

import os
from dotenv import load_dotenv
import litellm

load_dotenv()

print("=" * 70)
print("🔍 AGRO NEWS SCRAPER - DIAGNOSTIC CHECK")
print("=" * 70)

# 1. Check environment variables
print("\n1️⃣ Checking Environment Variables...")
print("-" * 70)

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
    print(f"✅ GOOGLE_API_KEY found: {masked_key}")
else:
    print("❌ GOOGLE_API_KEY not found!")
    print("   Please create a .env file with your API key")
    exit(1)

# 2. Test LLM initialization
print("\n2️⃣ Testing LLM Initialization...")
print("-" * 70)

models_to_test = [
    ("gemini/gemini-1.5-flash", "Gemini 1.5 Flash (Recommended - 1500 RPD)"),
    ("gemini/gemini-2.0-flash-exp", "Gemini 2.0 Flash Experimental"),
    ("gemini/gemini-2.5-flash", "Gemini 2.5 Flash (20 RPD)")
]

working_models = []

for model, description in models_to_test:
    try:
        print(f"\n🧪 Testing: {description}")
        print(f"   Model: {model}")
        
        # Try to make a simple call
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
            api_key=api_key
        )
        
        print(f"   ✅ SUCCESS - Model is working!")
        working_models.append((model, description))
        
    except Exception as e:
        error_msg = str(e)
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print(f"   ⚠️ QUOTA EXCEEDED")
            if "20" in error_msg:
                print(f"   📊 Daily limit reached (20/20 requests)")
            print(f"   💡 This model is out of quota but might work tomorrow")
        elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
            print(f"   ❌ AUTHENTICATION FAILED")
            print(f"   💡 Check your API key")
        else:
            print(f"   ❌ FAILED: {error_msg[:100]}")

# 3. Summary
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)

if working_models:
    print(f"\n✅ {len(working_models)} model(s) available:")
    for model, desc in working_models:
        print(f"   • {desc}")
    print("\n💡 Recommendation: Use the first available model")
    print("   Your workflow should work fine!")
else:
    print("\n❌ No models available")
    print("\n💡 Possible reasons:")
    print("   1. Daily quota exceeded (wait until midnight PT)")
    print("   2. Invalid API key")
    print("   3. API key not enabled for Gemini")
    print("\n🔗 Useful links:")
    print("   • Check quota: https://ai.dev/rate-limit")
    print("   • Get API key: https://aistudio.google.com/app/apikey")
    print("   • Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits")

# 4. Next steps
print("\n" + "=" * 70)
print("🚀 NEXT STEPS")
print("=" * 70)

if working_models:
    print("\n✅ You're ready to run the scraper!")
    print("\n   Run: python run.py")
else:
    print("\n⏰ If quota is exceeded:")
    print("   • Wait until tomorrow (quota resets midnight PT)")
    print("   • Or get a new API key from different Google account")
    print("\n🔧 If API key issue:")
    print("   • Verify key at: https://aistudio.google.com/app/apikey")
    print("   • Make sure Gemini API is enabled")

print("\n" + "=" * 70)
