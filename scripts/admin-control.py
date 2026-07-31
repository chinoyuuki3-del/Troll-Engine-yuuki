import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

BODY = os.environ.get("ISSUE_BODY", "")
NOW = datetime.now(timezone.utc)

def field(name, default=""):
    match = re.search(rf"^{re.escape(name)}:\s*(.*?)\s*$", BODY, re.MULTILINE)
    return match.group(1).strip() if match else default

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def iso(value=NOW):
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def safe_text(value, limit=300):
    return re.sub(r"[\x00-\x1f\x7f]", " ", value).strip()[:limit]

def parse_bool(value):
    if value.lower() in {"true", "on", "1", "yes"}:
        return True
    if value.lower() in {"false", "off", "0", "no"}:
        return False
    raise SystemExit("ENABLEDはtrueまたはfalseで指定してください。")

action = field("ACTION")
update_id = f"github-{os.environ.get('ISSUE_NUMBER', '0')}-{int(NOW.timestamp())}"

if action in {"maintenance_start", "maintenance_stop"}:
    path = "data/maintenance.json"
    data = load(path)
    if action == "maintenance_start":
        minutes = int(field("MINUTES", "5"))
        if not 1 <= minutes <= 1440:
            raise SystemExit("MINUTESは1〜1440で指定してください。")
        data.update({
            "enabled": True,
            "update_id": update_id,
            "starts_at": iso(),
            "ends_at": iso(NOW + timedelta(minutes=minutes)),
            "message": safe_text(field("MESSAGE", "データ保存とシステム点検を行っています。")),
            "work": ["ユーザー情報の保存", "クラウド状態の確認", "機能の最終確認"],
            "updated_by": "chinoyuuki3-del",
            "updated_at": iso(),
        })
    else:
        data.update({"enabled": False, "update_id": update_id, "ends_at": iso(), "updated_at": iso()})
    save(path, data)

elif action == "feature_set":
    path = "data/feature-control.json"
    data = load(path)
    feature = field("FEATURE")
    if feature not in data.get("features", {}):
        raise SystemExit("FEATUREが登録されていません。")
    data["features"][feature] = {
        "enabled": parse_bool(field("ENABLED")),
        "reason": safe_text(field("REASON"), 180),
    }
    data.update({"update_id": update_id, "updated_at": iso()})
    save(path, data)

elif action == "test_channel":
    path = "data/test-channel.json"
    data = load(path)
    channel = field("CHANNEL", "stable")
    data.update({
        "enabled": parse_bool(field("ENABLED", "true")),
        "channel": channel if channel in {"stable", "test"} else "stable",
        "message": safe_text(field("MESSAGE", "")),
        "updated_at": iso(),
    })
    save(path, data)

elif action == "badge_award":
    path = "data/badges.json"
    data = load(path)
    user_id = field("USER_ID")
    badge = field("BADGE")
    if not re.fullmatch(r"[A-Za-z0-9._:-]{8,180}", user_id):
        raise SystemExit("USER_IDの形式が正しくありません。")
    if badge not in data.get("badge_definitions", {}):
        raise SystemExit("BADGEが登録されていません。")
    if not any(item.get("user_id") == user_id and item.get("badge") == badge for item in data.get("awards", [])):
        data.setdefault("awards", []).append({"user_id": user_id, "badge": badge, "awarded_at": iso()})
    data["updated_at"] = iso()
    save(path, data)

else:
    raise SystemExit("ACTIONが対応していません。")
