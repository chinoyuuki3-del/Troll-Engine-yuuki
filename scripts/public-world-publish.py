#!/usr/bin/env python3
import base64
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

CATALOG = Path("data/public-worlds.json")
ALLOWED_THEMES = {"plaza", "game", "theater", "creative"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,79}$")


def fail(message: str) -> None:
    raise SystemExit(message)


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in body.splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip().upper()
        if key and key not in fields:
            fields[key] = value.strip()
    return fields


def decode_world(value: str) -> dict:
    if not value:
        fail("WORLD_JSON_B64 is required")
    try:
        padded = value + "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        world = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        fail(f"invalid WORLD_JSON_B64: {exc}")
    if not isinstance(world, dict):
        fail("world data must be an object")
    return world


def text(value, limit: int) -> str:
    value = " ".join(str(value or "").split()).strip()
    return value[:limit]


def validate_world(raw: dict) -> dict:
    world_id = text(raw.get("id"), 80).lower()
    name = text(raw.get("name"), 40)
    if not ID_PATTERN.fullmatch(world_id):
        fail("world id must use lowercase letters, numbers, dot, underscore or hyphen")
    if not name:
        fail("world name is required")

    icon = text(raw.get("icon") or "🌍", 8) or "🌍"
    theme = text(raw.get("theme") or "plaza", 20)
    if theme not in ALLOWED_THEMES:
        theme = "plaza"
    description = text(raw.get("description") or "公開交流ワールド", 180)

    tags = []
    for item in raw.get("tags") if isinstance(raw.get("tags"), list) else []:
        item = text(item, 18)
        if item and item not in tags:
            tags.append(item)
        if len(tags) >= 5:
            break

    zones = []
    source_zones = raw.get("zones") if isinstance(raw.get("zones"), list) else []
    for item in source_zones[:8]:
        if not isinstance(item, dict):
            continue
        label = text(item.get("label"), 30)
        if not label:
            continue
        try:
            x = max(5.0, min(95.0, float(item.get("x", 50))))
            y = max(8.0, min(92.0, float(item.get("y", 50))))
        except (TypeError, ValueError):
            x, y = 50.0, 50.0
        zones.append({"label": label, "x": round(x, 2), "y": round(y, 2)})

    if not zones:
        zones = [{"label": "🌐 メインエリア", "x": 50, "y": 50}]

    return {
        "id": world_id,
        "name": name,
        "icon": icon,
        "theme": theme,
        "description": description,
        "tags": tags,
        "zones": zones,
    }


def load_catalog() -> dict:
    if not CATALOG.exists():
        return {"version": "4.22", "updatedAt": "", "worlds": []}
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"catalog cannot be read: {exc}")
    if not isinstance(data, dict):
        data = {"worlds": []}
    if not isinstance(data.get("worlds"), list):
        data["worlds"] = []
    return data


def save_catalog(data: dict) -> None:
    data["version"] = "4.22"
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    fields = parse_fields(os.environ.get("ISSUE_BODY", ""))
    action = fields.get("ACTION", "")
    data = load_catalog()

    if action == "public_world_publish":
        world = validate_world(decode_world(fields.get("WORLD_JSON_B64", "")))
        worlds = [item for item in data["worlds"] if not isinstance(item, dict) or item.get("id") != world["id"]]
        worlds.append(world)
        data["worlds"] = worlds[:100]
        save_catalog(data)
        print(f"published public world: {world['id']}")
        return

    if action == "public_world_delete":
        world_id = text(fields.get("WORLD_ID"), 80).lower()
        if not ID_PATTERN.fullmatch(world_id):
            fail("invalid WORLD_ID")
        before = len(data["worlds"])
        data["worlds"] = [item for item in data["worlds"] if not isinstance(item, dict) or item.get("id") != world_id]
        if len(data["worlds"]) == before:
            fail("world was not found")
        save_catalog(data)
        print(f"deleted public world: {world_id}")
        return

    fail("unsupported public world action")


if __name__ == "__main__":
    main()
