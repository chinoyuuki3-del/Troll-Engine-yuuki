#!/usr/bin/env python3
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PAYLOAD_DIR = ROOT / ".publish-v423"


def decode_payload() -> dict[str, str]:
    parts = sorted(PAYLOAD_DIR.glob("public-world.gz.b64.part-*"))
    if not parts:
        raise SystemExit("public world payload parts were not found")
    encoded = "".join("".join(path.read_text(encoding="utf-8").split()) for path in parts)
    raw = gzip.decompress(base64.b64decode(encoded))
    data = json.loads(raw.decode("utf-8"))
    for key in ("style", "section", "script"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise SystemExit(f"missing payload block: {key}")
    return data


def remove_old_blocks(html: str) -> str:
    patterns = [
        r"\s*<!-- ===== Troll Public World .*? STYLE START ===== -->.*?<!-- ===== Troll Public World .*? STYLE END ===== -->\s*",
        r"\s*<!-- ===== Troll Public World .*? SECTION START ===== -->.*?<!-- ===== Troll Public World .*? SECTION END ===== -->\s*",
        r"\s*<!-- ===== Troll Public World .*? SCRIPT START ===== -->.*?<!-- ===== Troll Public World .*? SCRIPT END ===== -->\s*",
        r"\s*<script id=[\"']teOpenWorldV422Finalizer[\"']>.*?</script>\s*",
        r"\s*<button\b[^>]*id=[\"']teOpenWorldV421Tab[\"'][^>]*>.*?</button>\s*",
    ]
    for pattern in patterns:
        html = re.sub(pattern, "\n", html, flags=re.S | re.I)
    return html


def insert_before(html: str, needle: str, value: str, label: str) -> str:
    position = html.find(needle)
    if position < 0:
        raise SystemExit(f"cannot find insertion point: {label}")
    return html[:position] + value.rstrip() + "\n" + html[position:]


def main() -> None:
    if not INDEX.exists():
        raise SystemExit("index.html does not exist")

    payload = decode_payload()
    html = remove_old_blocks(INDEX.read_text(encoding="utf-8"))
    html = insert_before(html, "</head>", payload["style"] + "\n", "head")

    nav_button = (
        "  <button id=\"teOpenWorldV421Tab\" "
        "onclick=\"showTab('teOpenWorldV421', this);window.teOpenWorldV422?.open?.()\">"
        "🌍 公開ワールド</button>\n"
    )
    nav_anchor = '<button onclick="showTab(\'plus\', this)">追加+</button>'
    if nav_anchor in html:
        html = insert_before(html, nav_anchor, nav_button, "navigation")
    else:
        html = insert_before(html, "</nav>", nav_button, "navigation fallback")

    if '<section id="peerRoom">' in html:
        html = insert_before(html, '<section id="peerRoom">', payload["section"] + "\n", "peer room")
    else:
        html = insert_before(html, "</main>", payload["section"] + "\n", "main")

    html = insert_before(html, "</body>", payload["script"] + "\n", "body")
    html = re.sub(
        r"<title>.*?</title>",
        "<title>Troll Engine - Classic Standard Edition v4.23 - Public World All Peer Sync</title>",
        html,
        count=1,
        flags=re.S | re.I,
    )
    html = re.sub(
        r'(<meta\s+name=["\']troll-engine-classic-version["\']\s+content=["\'])[^"\']*(["\'])',
        r"\g<1>4.23\g<2>",
        html,
        count=1,
        flags=re.I,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Published Troll Public World v4.23 into {INDEX}")


if __name__ == "__main__":
    main()
