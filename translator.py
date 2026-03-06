import os
import logging
import litellm
from config import GEMINI_MODELS

logger = logging.getLogger(__name__)


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

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("API kalit topilmadi. .env faylida GEMINI_API_KEY yoki GOOGLE_API_KEY ni belgilang.")

    for model, description in GEMINI_MODELS:
        try:
            response = litellm.completion(
                model=model,
                api_key=api_key,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("Model %s ishlamadi: %s", description, e)
            continue

    raise RuntimeError("Tarjima amalga oshmadi. Barcha modellar ishlamadi.")
