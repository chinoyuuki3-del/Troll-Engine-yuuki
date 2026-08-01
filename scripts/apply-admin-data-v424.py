#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SECTION = '''<!-- ===== Troll Engine v4.24 Admin Data Menu SECTION START ===== -->
<section id="teAdminDataV424">
  <div class="admHero">
    <span class="admBadge">ADMIN DATA CENTER · GitHubの生ファイルを開かない管理画面</span>
    <h2>🧭 管理データメニュー</h2>
    <p>GitHubへ移動せず、Troll Engine内で公開ワールド・動画・ユーザー・保存データ・運営設定を表形式で確認できます。</p>
  </div>
  <div id="teAdmGate" class="admGate">管理者アカウントを確認しています…</div>
  <div id="teAdmShell" class="admShell admHidden">
    <aside id="teAdmMenu" class="admMenu"></aside>
    <div class="admMain">
      <div class="admToolbar">
        <input id="teAdmSearch" placeholder="表示中のデータを検索">
        <button id="teAdmReload" type="button" class="mainBtn">再読み込み</button>
        <button id="teAdmJson" type="button" class="grayBtn">JSON表示</button>
        <button id="teAdmCopy" type="button" class="grayBtn">内容をコピー</button>
      </div>
      <div id="teAdmStatus" class="admStatus">データを選択してください。</div>
      <div id="teAdmStats" class="admStats"></div>
      <div id="teAdmView"></div>
      <div id="teAdmDetail" class="admDetail admHidden"></div>
    </div>
  </div>
</section>
<!-- ===== Troll Engine v4.24 Admin Data Menu SECTION END ===== -->'''


def first_insert(html: str, needle: str, value: str) -> str:
    pos = html.find(needle)
    if pos < 0: raise SystemExit(f"missing insertion point: {needle}")
    return html[:pos] + value.rstrip() + "\n" + html[pos:]

def last_insert(html: str, needle: str, value: str) -> str:
    pos = html.rfind(needle)
    if pos < 0: raise SystemExit(f"missing insertion point: {needle}")
    return html[:pos] + value.rstrip() + "\n" + html[pos:]

def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    patterns = [
      r'\s*<link\b[^>]*id=["\']teAdminDataV424Css["\'][^>]*>\s*',
      r'\s*<script\b[^>]*id=["\']teAdminDataV424External["\'][^>]*>\s*</script>\s*',
      r'\s*<!-- ===== Troll Engine v4\.24 Admin Data Menu SECTION START ===== -->.*?<!-- ===== Troll Engine v4\.24 Admin Data Menu SECTION END ===== -->\s*',
      r'\s*<button\b[^>]*id=["\']teAdminDataV424Tab["\'][^>]*>.*?</button>\s*',
    ]
    for pattern in patterns: html = re.sub(pattern, "\n", html, flags=re.S|re.I)
    html = first_insert(html, "</head>", '<link id="teAdminDataV424Css" rel="stylesheet" href="assets/admin-data-v424.css">')
    nav = '<button id="teAdminDataV424Tab" onclick="showTab(\'teAdminDataV424\',this);window.teAdminDataV424?.open?.()">🧭 管理データ</button>'
    anchor = '<button onclick="showTab(\'plus\', this)">追加+</button>'
    html = first_insert(html, anchor if anchor in html else "</nav>", nav)
    html = first_insert(html, '<section id="peerRoom">' if '<section id="peerRoom">' in html else "</main>", SECTION)
    html = last_insert(html, "</body>", '<script id="teAdminDataV424External" src="assets/admin-data-v424.js"></script>')
    html = re.sub(r"<title>.*?</title>", "<title>Troll Engine - Classic Standard Edition v4.24 - Admin Data Menu</title>", html, count=1, flags=re.S|re.I)
    html = re.sub(r'(<meta\s+name=["\']troll-engine-classic-version["\']\s+content=["\'])[^"\']*(["\'])', r'\g<1>4.24\g<2>', html, count=1, flags=re.I)
    INDEX.write_text(html, encoding="utf-8")
    print("Published Troll Engine v4.24 Admin Data Menu")

if __name__ == "__main__": main()
