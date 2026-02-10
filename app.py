import os
from main import run
import time
max_retries = 3

for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1}: Running the crew...")
        result = run()
        print("✅ Task completed successfully!")
        break  # Exit the loop if successful
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print(f"⚠️ Quota exceeded. Waiting 45 seconds to refill the bucket...")
                
            # This is where you put time.sleep()
            time.sleep(45) 
                
            print("🔄 Retrying now...")
        else:
            print(f"❌ An unexpected error occurred: {e}")
            break