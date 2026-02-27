import os
import litellm
from config import GEMINI_MODELS


def translator(text: str, target_lang: str) -> str:
    """
    Matnni berilgan til kodiga tarjima qiladi.
    Misol: translator("Salom dunyo", "ru") -> "Привет мир"

    target_lang: "ru", "en", "uz", "tr", "de" va hokazo ISO til kodlari.
    """
    prompt = (
        f"Translate the following text to the language with ISO code '{target_lang}'. "
        f"Return only the translated text, nothing else.\n\n{text}"
    )

    api_key = os.getenv("GOOGLE_API_KEY")
    for model, _ in GEMINI_MODELS:
        try:
            response = litellm.completion(
                model=model,
                api_key=api_key,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            continue

    raise RuntimeError(f"Tarjima amalga oshmadi. Barcha modellar ishlamadi.")
