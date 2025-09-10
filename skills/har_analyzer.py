import re
import json
from pathlib import Path
from utils.logging_utils import getLogger

logger = getLogger()

async def scrub_sensitive_data(har: dict) -> dict:
    """
    Scrub sensitive information from HAR file including:
    - Authorization headers (Bearer tokens, API keys)
    - Session cookies
    - Personal identification information
    - Sensitive query parameters
    - Request/response body data that may contain tokens
    """

    logger.info("Starting to scrub sensitive data from HAR")
    
    # Common patterns for sensitive data
    sensitive_patterns = [
        # Authorization patterns
        r'bearer\s+[a-zA-Z0-9\-._~+/]+=*',
        r'token["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        r'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        r'access[_-]?token["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        r'refresh[_-]?token["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        # Session IDs
        r'session[_-]?id["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        r'jsessionid["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        # Common secret patterns
        r'secret["\s]*[:=]["\s]*[a-zA-Z0-9\-._~+/]+=*',
        r'password["\s]*[:=]["\s]*[^"\s]+',
        # Email patterns (basic PII)
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # Credit card patterns (basic)
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    ]
    
    # Sensitive header names to scrub
    sensitive_headers = {
        'authorization', 'x-api-key', 'x-auth-token', 'x-access-token',
        'cookie', 'set-cookie', 'x-csrf-token', 'x-session-token'
    }
    
    # Sensitive query parameter names
    sensitive_params = {
        'token', 'access_token', 'api_key', 'apikey', 'session_id',
        'sessionid', 'auth', 'authorization', 'key', 'secret'
    }
    
    async def scrub_string(text: str) -> str:
        """Replace sensitive patterns in a string with [REDACTED]"""
        if not isinstance(text, str):
            return text
            
        for pattern in sensitive_patterns:
            text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
        return text
    
    async def scrub_url(url: str) -> str:
        """Remove sensitive query parameters from URLs"""
        if '?' not in url:
            return url
            
        base_url, query_string = url.split('?', 1)
        params = []
        
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                if key.lower() in sensitive_params:
                    params.append(f"{key}=[REDACTED]")
                else:
                    params.append(param)
            else:
                params.append(param)
                
        return f"{base_url}?{'&'.join(params)}"
    
    async def scrub_headers(headers: list) -> list:
        """Remove sensitive information from headers"""
        logger.info("Scrubbing headers")
        scrubbed_headers = []
        for header in headers:
            if isinstance(header, dict) and 'name' in header:
                header_name = header['name'].lower()
                if header_name in sensitive_headers:
                    scrubbed_headers.append({
                        'name': header['name'],
                        'value': '[REDACTED]'
                    })
                else:
                    scrubbed_headers.append({
                        'name': header['name'],
                        'value': scrub_string(header.get('value', ''))
                    })
            else:
                scrubbed_headers.append(header)
        return scrubbed_headers
    
    # Create a deep copy to avoid modifying the original
    import copy
    logger.info("Creating deep copy of HAR for scrubbing")
    scrubbed_har = copy.deepcopy(har)
    
    # Process all entries in the HAR file
    entries = scrubbed_har.get("log", {}).get("entries", [])
    for entry in entries:
        # Scrub request data
        if "request" in entry:
            request = entry["request"]
            
            # Scrub URL
            if "url" in request:
                request["url"] = scrub_url(request["url"])
            
            # Scrub headers
            if "headers" in request:
                request["headers"] = scrub_headers(request["headers"])
            
            # Scrub cookies
            if "cookies" in request:
                for cookie in request["cookies"]:
                    if isinstance(cookie, dict) and "value" in cookie:
                        cookie["value"] = "[REDACTED]"
            
            # Scrub POST data
            if "postData" in request and "text" in request["postData"]:
                request["postData"]["text"] = scrub_string(request["postData"]["text"])
        
        # Scrub response data
        if "response" in entry:
            response = entry["response"]
            
            # Scrub response headers
            if "headers" in response:
                response["headers"] = scrub_headers(response["headers"])
            
            # Scrub response cookies
            if "cookies" in response:
                for cookie in response["cookies"]:
                    if isinstance(cookie, dict) and "value" in cookie:
                        cookie["value"] = "[REDACTED]"
            
            # Scrub response content
            if "content" in response and "text" in response["content"]:
                response["content"]["text"] = scrub_string(response["content"]["text"])
    
    # Write scrubbed HAR to file
    scrubbed_dir = Path("run_output/scrubbed")
    scrubbed_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename based on original HAR structure or timestamp
    import time
    timestamp = time.strftime("%Y%m%d")
    scrubbed_file = scrubbed_dir / f"scrubbed_har_{timestamp}.har"
    
    with open(scrubbed_file, 'w', encoding='utf-8') as f:
        json.dump(scrubbed_har, f, indent=2, ensure_ascii=False)
    
    logger.info("Scrubbed sensitive data from HAR file and saved to: %s", scrubbed_file)
    return scrubbed_har

async def analyze_har(har: dict) -> dict:
    """
    Analyze HAR file data after scrubbing sensitive information.
    
    Examples:
      - Summarize slow endpoints
      - Flag PII
      - Extract domains/methods/status codes
      - Score sessions for anomalies

    You can wire this to any model:
      - Cloud LLM via API (OpenAI, Anthropic, etc.)
      - Local model server (e.g., Ollama) via HTTP
    Return a structured dict; store or send it wherever you like.
    """
    # First scrub the HAR file of sensitive data
    logger.debug("scrubbing data")
    scrubbed_har = scrub_sensitive_data(har)
    
    # Example: simple summary of request counts per host
    by_host = {}
    for entry in scrubbed_har.get("log", {}).get("entries", []):
        try:
            url = entry["request"]["url"]
            host = url.split("/")[2] if "://" in url else url
            by_host[host] = by_host.get(host, 0) + 1
        except Exception:
            continue

    result = {
        "total_entries": len(scrubbed_har.get("log", {}).get("entries", [])),
        "by_host": by_host,
        "scrubbed": True  # Indicate that sensitive data has been removed
    }
    logger.info("Analysis summary: %s", result)
    return result