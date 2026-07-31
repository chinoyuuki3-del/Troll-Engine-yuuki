import json
import os
import re
import sys
from datetime import date
from pathlib import Path


BODY = os.environ.get("ISSUE_BODY", "")
USERS_PATH = Path("users.json")


def field(name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.+?)\s*$", BODY, re.MULTILINE)
    return match.group(1).strip() if match else ""


user_id = field("TROLL_ENGINE_ID")
username = field("USERNAME")

if not re.fullmatch(r"[A-Za-z0-9._:-]{8,180}", user_id):
    sys.exit("Troll Engine IDの形式が正しくありません。")
if not 2 <= len(username) <= 30:
    sys.exit("ユーザー名は2〜30文字で入力してください。")
if "@" in username or any(ord(char) < 32 or ord(char) == 127 for char in username):
    sys.exit("ユーザー名に使用できない文字が含まれています。")

document = json.loads(USERS_PATH.read_text(encoding="utf-8"))
users = document.setdefault("users", [])

if any(str(user.get("id", "")) == user_id for user in users):
    sys.exit("このTroll Engine IDはすでに登録されています。")

users.append(
    {
        "id": user_id,
        "username": username,
        "status": "active",
        "searchable": True,
        "ban_until": 0,
    }
)
users.sort(key=lambda user: (str(user.get("username", "")).casefold(), str(user.get("id", ""))))
document["updated_at"] = date.today().isoformat()
USERS_PATH.write_text(
    json.dumps(document, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
