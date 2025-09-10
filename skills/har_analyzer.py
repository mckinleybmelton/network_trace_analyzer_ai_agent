from utils.logging_utils import getLogger

logger = getLogger()

def analyze_har(har: dict) -> dict:
    """
    Place your AI logic here. Examples:
      - Summarize slow endpoints
      - Flag PII
      - Extract domains/methods/status codes
      - Score sessions for anomalies

    You can wire this to any model:
      - Cloud LLM via API (OpenAI, Anthropic, etc.)
      - Local model server (e.g., Ollama) via HTTP
    Return a structured dict; store or send it wherever you like.
    """
    # Example: simple summary of request counts per host
    by_host = {}
    for entry in har.get("log", {}).get("entries", []):
        try:
            url = entry["request"]["url"]
            host = url.split("/")[2] if "://" in url else url
            by_host[host] = by_host.get(host, 0) + 1
        except Exception:
            continue

    result = {
        "total_entries": len(har.get("log", {}).get("entries", [])),
        "by_host": by_host
    }
    logger.info("Analysis summary: %s", result)
    return result