import base64
import gzip
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BODY = os.environ.get("ISSUE_BODY", "")
TARGET = Path("data/admin-posts.json")
ALLOWED_KINDS = {"notice", "update", "event", "alert", "maintenance", "campaign"}
ALLOWED_AUDIENCES = {"all", "world", "aft", "admin"}
ALLOWED_STATUSES = {"published", "draft", "scheduled", "hidden"}


def field(name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.*?)\s*$", BODY, re.MULTILINE)
    return match.group(1).strip() if match else ""


def decode_urlsafe(value: str) -> bytes:
    value = value.strip()
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value.encode("ascii"))


def clean_text(value, limit: int) -> str:
    value = re.sub(r"[\x00-\x1f\x7f]", " ", str(value or "")).strip()
    return value[:limit]


def clean_url(value) -> str:
    value = clean_text(value, 900)
    if not value:
        return ""
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def clean_time(value) -> str:
    return clean_text(value, 60)


def clean_id(value, prefix: str) -> str:
    value = clean_text(value, 120)
    if re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", value):
        return value
    stamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return f"{prefix}-{stamp}"


packed = field("ADMIN_POSTS_GZIP_B64")
plain = field("ADMIN_POSTS_JSON_B64")
if packed:
    raw = gzip.decompress(decode_urlsafe(packed)).decode("utf-8")
elif plain:
    raw = decode_urlsafe(plain).decode("utf-8")
else:
    raise SystemExit("ADMIN_POSTS_GZIP_B64 または ADMIN_POSTS_JSON_B64 が必要です。")

if len(raw.encode("utf-8")) > 2_000_000:
    raise SystemExit("管理データが大きすぎます。")

incoming = json.loads(raw)
if not isinstance(incoming, dict):
    raise SystemExit("管理データはJSONオブジェクトで指定してください。")

posts = []
for item in incoming.get("posts", [])[:200]:
    if not isinstance(item, dict):
        continue
    title = clean_text(item.get("title"), 100)
    body = clean_text(item.get("body"), 4000)
    if not title or not body:
        continue
    kind = clean_text(item.get("kind"), 30)
    audience = clean_text(item.get("audience"), 30)
    status = clean_text(item.get("status"), 30)
    posts.append({
        "id": clean_id(item.get("id"), "post"),
        "kind": kind if kind in ALLOWED_KINDS else "notice",
        "title": title,
        "body": body,
        "image_url": clean_url(item.get("image_url")),
        "action_label": clean_text(item.get("action_label"), 40),
        "action_url": clean_url(item.get("action_url")),
        "audience": audience if audience in ALLOWED_AUDIENCES else "all",
        "pinned": bool(item.get("pinned")),
        "status": status if status in ALLOWED_STATUSES else "draft",
        "starts_at": clean_time(item.get("starts_at")),
        "expires_at": clean_time(item.get("expires_at")),
        "author": "chinoyuuki3-del",
        "created_at": clean_time(item.get("created_at")),
        "updated_at": clean_time(item.get("updated_at")),
        "published_at": clean_time(item.get("published_at")),
    })

audit = []
for item in incoming.get("audit", [])[:200]:
    if not isinstance(item, dict):
        continue
    audit.append({
        "id": clean_id(item.get("id"), "audit"),
        "action": clean_text(item.get("action"), 80),
        "detail": clean_text(item.get("detail"), 500),
        "actor": "chinoyuuki3-del",
        "at": clean_time(item.get("at")),
    })

settings_in = incoming.get("settings") if isinstance(incoming.get("settings"), dict) else {}
result = {
    "version": "4.26",
    "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "settings": {
        "feed_enabled": bool(settings_in.get("feed_enabled", True)),
        "title": clean_text(settings_in.get("title", "Troll Engine 運営フィード"), 100),
    },
    "posts": posts,
    "audit": audit,
}

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"admin posts updated: {len(posts)} posts, {len(audit)} audit rows")
