import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BODY = os.environ.get("ISSUE_BODY", "")
NOW = datetime.now(timezone.utc)


def field(name, default=""):
    match = re.search(rf"^{re.escape(name)}:\s*(.*?)\s*$", BODY, re.MULTILINE)
    return match.group(1).strip() if match else default


def safe_text(value, limit=300):
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(value)).strip()[:limit]


def iso():
    return NOW.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def valid_video_url(value):
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    host = parsed.netloc.lower().split(":", 1)[0]
    allowed_hosts = {
        "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
        "youtube-nocookie.com", "www.youtube-nocookie.com",
        "vimeo.com", "www.vimeo.com", "player.vimeo.com",
        "github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
        "github-releases.githubusercontent.com", "user-images.githubusercontent.com"
    }
    if host in allowed_hosts:
        return True
    return bool(re.search(r"\.(mp4|webm|m4v|mov|ogv|ogg)(?:$|[?#])", parsed.path, re.IGNORECASE))


action = field("ACTION")
if action != "aft_video_publish":
    raise SystemExit("ACTIONがaft_video_publishではありません。")

video_url = field("VIDEO_URL")
if not valid_video_url(video_url):
    raise SystemExit("VIDEO_URLはhttpsのYouTube、Vimeo、GitHub Release、または直接再生できる動画URLを指定してください。")

path = Path("data/aft-videos.json")
data = json.loads(path.read_text(encoding="utf-8"))
issue_number = os.environ.get("ISSUE_NUMBER", "0")
update_id = f"github-{issue_number}-{int(NOW.timestamp())}"
video = {
    "id": update_id,
    "title": safe_text(field("TITLE", "AFT動画"), 100),
    "description": safe_text(field("DESCRIPTION", ""), 500),
    "video_url": video_url,
    "thumbnail_url": safe_text(field("THUMBNAIL_URL", ""), 1000),
    "author": safe_text(field("AUTHOR", "Troll Engine Owner"), 50),
    "channel_id": safe_text(field("CHANNEL", "aft-community"), 80),
    "official": field("OFFICIAL", "false").lower() in {"true", "yes", "1", "on"},
    "published_at": iso(),
}

videos = [item for item in data.get("videos", []) if item.get("video_url") != video_url]
videos.insert(0, video)
data.update({"enabled": True, "videos": videos[:200], "updated_at": iso()})
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
