import json
import os
import urllib.error
import urllib.request


def get_feedback_config(secrets):
    url = secrets.get("SUPABASE_URL") if secrets else None
    key = None
    table = "feedback"
    if secrets:
        key = secrets.get("SUPABASE_KEY") or secrets.get("SUPABASE_ANON_KEY")
        table = secrets.get("FEEDBACK_TABLE", "feedback")
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    table = os.getenv("FEEDBACK_TABLE", table)
    return {"url": url, "key": key, "table": table}


def submit_feedback(payload, config, timeout=10):
    if not config.get("url") or not config.get("key"):
        raise RuntimeError("Feedback backend is not configured.")

    endpoint = f"{config['url'].rstrip('/')}/rest/v1/{config.get('table', 'feedback')}"
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "apikey": config["key"],
            "Authorization": f"Bearer {config['key']}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"Feedback submission failed with HTTP {response.status}.")
            return True
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Feedback submission failed with HTTP {exc.code}: {detail[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Feedback backend could not be reached: {exc.reason}") from exc
