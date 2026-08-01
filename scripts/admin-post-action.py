import base64
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


def decode_urlsafe(value: str) -> str:
    value = value.strip() + "=" * (-len(value.strip()) % 4)
    return base64.urlsafe_b64decode(value.encode("ascii")).decode("utf-8")


def clean_text(value, limit: int) -> str:
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(value or "")).strip()[:limit]


def clean_url(value) -> str:
    value = clean_text(value, 900)
    if not value:
        return ""
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def clean_time(value) -> str:
    return clean_text(value, 60)


def clean_id(value: str) -> str:
    value = clean_text(value, 120)
    if not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", value):
        raise SystemExit("投稿IDの形式が正しくありません。")
    return value


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_post(item: dict) -> dict:
    if not isinstance(item, dict):
        raise SystemExit("投稿データが正しくありません。")
    title = clean_text(item.get("title"), 100)
    body = clean_text(item.get("body"), 4000)
    if not title or not body:
        raise SystemExit("タイトルと本文が必要です。")
    kind = clean_text(item.get("kind"), 30)
    audience = clean_text(item.get("audience"), 30)
    status = clean_text(item.get("status"), 30)
    return {
        "id": clean_id(item.get("id")),
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
        "created_at": clean_time(item.get("created_at")) or now_iso(),
        "updated_at": now_iso(),
        "published_at": clean_time(item.get("published_at")),
    }


data = json.loads(TARGET.read_text(encoding="utf-8")) if TARGET.exists() else {
    "version": "4.28.1",
    "updated_at": "",
    "settings": {"feed_enabled": True, "title": "Troll Engine 運営フィード"},
    "posts": [],
    "audit": [],
}
posts = data.setdefault("posts", [])
audit = data.setdefault("audit", [])
action = field("ACTION")

if action == "admin_post_upsert":
    encoded = field("POST_JSON_B64")
    if not encoded:
        raise SystemExit("POST_JSON_B64が必要です。")
    post = normalize_post(json.loads(decode_urlsafe(encoded)))
    index = next((i for i, row in enumerate(posts) if str(row.get("id")) == post["id"]), -1)
    if index >= 0:
        posts[index] = post
        audit_action = "github_post_update"
    else:
        posts.insert(0, post)
        audit_action = "github_post_create"
    detail = post["title"]
elif action == "admin_post_delete":
    post_id = clean_id(field("POST_ID"))
    before = len(posts)
    posts[:] = [row for row in posts if str(row.get("id")) != post_id]
    if len(posts) == before:
        raise SystemExit("削除対象の投稿が見つかりません。")
    audit_action = "github_post_delete"
    detail = post_id
else:
    raise SystemExit("ACTIONが対応していません。")

audit.insert(0, {
    "id": f"audit-github-{int(datetime.now(timezone.utc).timestamp() * 1000)}",
    "action": audit_action,
    "detail": clean_text(detail, 500),
    "actor": "chinoyuuki3-del",
    "at": now_iso(),
})
data["audit"] = audit[:200]
data["posts"] = posts[:200]
data["version"] = "4.28.1"
data["updated_at"] = now_iso()
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{action}: {detail}")
