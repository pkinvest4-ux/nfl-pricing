"""Shared helper: polite HTTP with retries."""
import json, time, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"


def fetch(url, tries=4, as_json=True):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            return json.loads(body) if as_json else body
        except Exception:
            time.sleep(2 * (i + 1))
    return None
