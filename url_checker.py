import json
import re

_TOKEN_RE = re.compile(r"\[?(URL:\d+)\]?")


def _save_urls_callback(task_output):
    """No-op callback kept for backward compatibility."""
    pass


def _extract_numbers(text: str) -> set:
    """Extract all numeric tokens (years, percentages, quantities) from text."""
    return set(re.findall(r'\d+', text))


def _best_url_by_content(uzbek_text: str, url_store: dict, body_store: dict, min_score: int = 2) -> str | None:
    """
    Compare Uzbek news text against stored English DuckDuckGo bodies.
    Returns the URL whose body shares the most numeric tokens with the Uzbek text.
    Requires at least min_score shared numbers to avoid false positives.
    """
    uzb_numbers = _extract_numbers(uzbek_text.lower())
    if not body_store:
        return None

    best_score, best_url = 0, None
    for url_id, body_text in body_store.items():
        score = len(uzb_numbers & _extract_numbers(body_text)) if uzb_numbers else 0
        if score > best_score:
            best_score = score
            best_url = url_store.get(url_id)

    return best_url if best_score >= min_score else None


def inject_urls(final_json_str: str, url_store: dict, body_store: dict = None) -> list[dict]:
    # Resolve any [URL:N] tokens in the raw JSON string
    def _resolve_token(m):
        return url_store.get(m.group(1), m.group(0))

    resolved_str = _TOKEN_RE.sub(_resolve_token, final_json_str)

    match = re.search(r"\[.*\]", resolved_str, re.DOTALL)
    if not match:
        return []
    try:
        items = json.loads(match.group())
    except json.JSONDecodeError:
        return []

    for item in items:
        manba = item.get("Manba", "")

        # Resolve any remaining token still in Manba field
        token_match = _TOKEN_RE.search(manba)
        if token_match:
            resolved = url_store.get(token_match.group(1))
            if resolved:
                item["Manba"] = resolved
                manba = resolved

        # Content-based fallback: only when Manba is missing or still unresolved (not a real URL)
        manba_is_unresolved = not manba or _TOKEN_RE.search(manba) or not manba.startswith("http")
        if body_store and manba_is_unresolved:
            uzb_text = item.get("Yangilik matni", "") + " " + item.get("Sarlavha", "")
            # Try strict match first (>=2 shared numbers), then lenient (>=1), then any available
            better_url = (
                _best_url_by_content(uzb_text, url_store, body_store, min_score=2)
                or _best_url_by_content(uzb_text, url_store, body_store, min_score=1)
            )
            if better_url:
                item["Manba"] = better_url

    return items