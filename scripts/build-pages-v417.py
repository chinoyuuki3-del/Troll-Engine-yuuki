import base64
import gzip
import re
from pathlib import Path

SOURCE = Path("index (24).html")
OUTPUT = Path("index.html")
PART_DIR = Path(".publish-v417")
PARTS = [PART_DIR / f"aft-section.gz.b64.part-{i:02d}" for i in range(4)]

if not SOURCE.exists():
    raise SystemExit(f"公開元が見つかりません: {SOURCE}")

html = SOURCE.read_text(encoding="utf-8")
payload = "".join(path.read_text(encoding="utf-8").strip() for path in PARTS)
aft_section = gzip.decompress(base64.b64decode(payload)).decode("utf-8")

pattern = re.compile(
    r"<!-- ===== Troll Engine v[0-9.]+ AFT Video[^\n]* START ===== -->.*?"
    r"<!-- ===== Troll Engine v[0-9.]+ AFT Video[^\n]* END ===== -->",
    re.DOTALL,
)

html, count = pattern.subn(lambda _match: aft_section, html, count=1)
if count != 1:
    raise SystemExit(f"AFT動画セクションを置換できませんでした: count={count}")

html = re.sub(
    r"<title>.*?</title>",
    "<title>Troll Engine - Classic Standard Edition v4.17 - Web Edition</title>",
    html,
    count=1,
    flags=re.DOTALL,
)
html = re.sub(
    r'(<meta\s+name="troll-engine-classic-version"\s+content=")[^"]*("\s*/?>)',
    r"\g<1>4.17\2",
    html,
    count=1,
)
html = re.sub(
    r'(<meta\s+name="troll-engine-aft-video"\s+content=")[^"]*("\s*/?>)',
    r"\g<1>public-publication-fix-v4.17\2",
    html,
    count=1,
)

if "window.__teAftVideoCampaignV417" not in html:
    raise SystemExit("v4.17 AFT動画ランタイムの検証に失敗しました。")

OUTPUT.write_text(html, encoding="utf-8")
Path(".nojekyll").write_text("", encoding="utf-8")
print(f"Generated {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
