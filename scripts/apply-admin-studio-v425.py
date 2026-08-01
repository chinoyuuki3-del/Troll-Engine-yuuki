#!/usr/bin/env python3
from __future__ import annotations
import re
import json
import gzip
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PAYLOAD = ROOT / ".publish-v425" / "admin-studio.gz.b64"

FEED_SECTION = r'''<!-- ===== Troll Engine v4.25 Admin Feed SECTION START ===== -->
<section id="teAdminFeedV425">
  <div class="te425Hero">
    <span class="te425Badge">OFFICIAL FEED · Troll Engine運営からの公式情報</span>
    <h2 id="te425FeedTitle">📡 Troll Engine 運営フィード</h2>
    <p>アップデート、イベント、重要なお知らせ、メンテナンス情報をここで確認できます。</p>
  </div>
  <div class="te425FeedToolbar">
    <span id="te425FeedStatus">運営投稿を読み込み中…</span>
    <button id="te425RefreshFeed" type="button">🔄 再読み込み</button>
  </div>
  <div id="te425PublicPosts" class="te425PostGrid"></div>
</section>
<!-- ===== Troll Engine v4.25 Admin Feed SECTION END ===== -->'''

ADMIN_SECTION = r'''<!-- ===== Troll Engine v4.25 Admin Studio SECTION START ===== -->
<section id="teAdminStudioV425">
  <div class="te425Hero">
    <span class="te425Badge">OWNER STUDIO · 最高管理者専用</span>
    <h2>👑 Troll Engine 管理スタジオ</h2>
    <p>GitHubのファイル画面を開かず、投稿、予約公開、固定、編集、削除、緊急告知、メンテナンス操作をTroll Engine内で実行します。</p>
  </div>
  <div id="te425AdminGate" class="te425Gate">最高管理者アカウントを確認しています…</div>
  <div id="te425AdminShell" class="te425AdminShell te425Hidden">
    <aside class="te425AdminNav">
      <button type="button" data-te425-pane="compose">✍️ 投稿を作る</button>
      <button type="button" data-te425-pane="manage">🗂️ 投稿を管理</button>
      <button type="button" data-te425-pane="quick">⚡ 即時コントロール</button>
      <button type="button" data-te425-pane="audit">🧾 操作履歴</button>
      <button type="button" onclick="document.getElementById('teAdminDataV424Tab')?.click()">🧭 管理データを見る</button>
      <button id="te425AdminReload" type="button">🔄 全データ再読込</button>
    </aside>
    <div class="te425AdminMain">
      <div id="te425AdminStatus" class="te425Status">管理データを準備しています…</div>

      <div class="te425Panel" data-te425-panel="compose">
        <h3>✍️ 公式投稿エディター</h3>
        <div class="te425ComposeGrid">
          <div class="te425Form">
            <label>投稿タイプ
              <select id="te425Kind">
                <option value="announcement">📢 お知らせ</option>
                <option value="update">🚀 アップデート</option>
                <option value="event">🎪 イベント</option>
                <option value="alert">🚨 重要警告</option>
                <option value="maintenance">🛠️ メンテナンス</option>
                <option value="campaign">🎁 キャンペーン</option>
                <option value="world">🌍 公開ワールド</option>
                <option value="video">🎬 AFT動画</option>
              </select>
            </label>
            <label>公開対象
              <select id="te425Audience">
                <option value="all">全ユーザー</option>
                <option value="world">公開ワールド利用者</option>
                <option value="video">AFT動画利用者</option>
                <option value="admin">管理者だけ</option>
              </select>
            </label>
            <label class="wide">タイトル
              <input id="te425Title" maxlength="120" placeholder="例：Troll Engine v4.25アップデート">
            </label>
            <label class="wide">本文
              <textarea id="te425Body" maxlength="5000" placeholder="投稿内容を入力"></textarea>
            </label>
            <label class="wide">画像URL（任意）
              <input id="te425Image" type="url" placeholder="https://...">
            </label>
            <label>ボタン名（任意）
              <input id="te425ActionLabel" maxlength="50" placeholder="詳しく見る">
            </label>
            <label>ボタンURL（任意）
              <input id="te425ActionUrl" type="url" placeholder="https://...">
            </label>
            <label>公開開始（空欄なら即時）
              <input id="te425Starts" type="datetime-local">
            </label>
            <label>公開終了（任意）
              <input id="te425Expires" type="datetime-local">
            </label>
            <label class="te425Check"><input id="te425Pinned" type="checkbox"> 投稿を一番上に固定</label>
            <div class="te425FormActions">
              <button id="te425SaveDraft" type="button">下書き保存</button>
              <button id="te425Publish" type="button" class="publish">🚀 今すぐ公開</button>
              <button id="te425Reset" type="button" class="reset">新規作成に戻す</button>
            </div>
          </div>
          <div class="te425PreviewBox">
            <h4>ライブプレビュー</h4>
            <div id="te425Preview"></div>
          </div>
        </div>
      </div>

      <div class="te425Panel te425Hidden" data-te425-panel="manage">
        <h3>🗂️ 投稿管理</h3>
        <div id="te425PostManager"></div>
      </div>

      <div class="te425Panel te425Hidden" data-te425-panel="quick">
        <h3>⚡ 即時コントロール</h3>
        <div class="te425QuickGrid">
          <div class="te425QuickCard">
            <h4>🛠️ メンテナンス</h4>
            <p>Troll Engine全体へメンテナンス状態を送ります。</p>
            <input id="te425MaintenanceMinutes" type="number" min="1" max="1440" value="15" placeholder="分数">
            <textarea id="te425MaintenanceMessage" placeholder="メンテナンス中に表示する文章">システム点検を行っています。</textarea>
            <div class="te425QuickActions">
              <button id="te425MaintenanceStart" type="button">開始</button>
              <button id="te425MaintenanceStop" type="button">終了</button>
            </div>
          </div>
          <div class="te425QuickCard">
            <h4>🚨 緊急告知</h4>
            <p>ライブメッセージとしてすぐに全体へ送信します。</p>
            <input id="te425LiveTitle" maxlength="100" placeholder="告知タイトル">
            <textarea id="te425LiveMessage" maxlength="1200" placeholder="緊急告知の本文"></textarea>
            <div class="te425QuickActions"><button id="te425LivePublish" type="button">固定告知を送信</button></div>
          </div>
          <div class="te425QuickCard">
            <h4>🎛️ 機能スイッチ</h4>
            <p>登録済みの機能キーを有効・無効にします。</p>
            <input id="te425FeatureKey" placeholder="機能キー">
            <select id="te425FeatureEnabled"><option value="true">有効</option><option value="false">無効</option></select>
            <input id="te425FeatureReason" maxlength="180" placeholder="変更理由">
            <div class="te425QuickActions"><button id="te425FeatureApply" type="button">設定を反映</button></div>
          </div>
        </div>
      </div>

      <div class="te425Panel te425Hidden" data-te425-panel="audit">
        <h3>🧾 管理操作履歴</h3>
        <div id="te425Audit"></div>
      </div>
    </div>
  </div>
</section>
<!-- ===== Troll Engine v4.25 Admin Studio SECTION END ===== -->'''


def insert_before(html: str, needle: str, value: str, label: str) -> str:
    pos = html.find(needle)
    if pos < 0:
        raise SystemExit(f"missing insertion point: {label}")
    return html[:pos] + value.rstrip() + "\n" + html[pos:]


def insert_last_before(html: str, needle: str, value: str, label: str) -> str:
    pos = html.rfind(needle)
    if pos < 0:
        raise SystemExit(f"missing insertion point: {label}")
    return html[:pos] + value.rstrip() + "\n" + html[pos:]


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    encoded = "".join(PAYLOAD.read_text(encoding="utf-8").split())
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)).decode("utf-8"))
    css = payload["css"]
    js = payload["js"]
    patterns = [
        r'\s*<style\b[^>]*id=["\']teAdminStudioV425Css["\'][^>]*>.*?</style>\s*',
        r'\s*<script\b[^>]*id=["\']teAdminStudioV425External["\'][^>]*>.*?</script>\s*',
        r'\s*<!-- ===== Troll Engine v4\.25 Admin Feed SECTION START ===== -->.*?<!-- ===== Troll Engine v4\.25 Admin Feed SECTION END ===== -->\s*',
        r'\s*<!-- ===== Troll Engine v4\.25 Admin Studio SECTION START ===== -->.*?<!-- ===== Troll Engine v4\.25 Admin Studio SECTION END ===== -->\s*',
        r'\s*<button\b[^>]*id=["\']teAdminFeedV425Tab["\'][^>]*>.*?</button>\s*',
        r'\s*<button\b[^>]*id=["\']teAdminStudioV425Tab["\'][^>]*>.*?</button>\s*',
    ]
    for pattern in patterns:
        html = re.sub(pattern, "\n", html, flags=re.S | re.I)

    html = insert_before(html, "</head>", f'<style id="teAdminStudioV425Css">\n{css}\n</style>', "head")
    feed_button = '<button id="teAdminFeedV425Tab" onclick="showTab(\'teAdminFeedV425\',this);window.teAdminStudioV425?.loadFeed?.()">📡 運営フィード</button>'
    admin_button = '<button id="teAdminStudioV425Tab" onclick="showTab(\'teAdminStudioV425\',this);window.teAdminStudioV425?.open?.()">👑 管理スタジオ</button>'
    anchor = '<button onclick="showTab(\'plus\', this)">追加+</button>'
    nav_anchor = anchor if anchor in html else "</nav>"
    html = insert_before(html, nav_anchor, feed_button + "\n" + admin_button, "navigation")

    section_anchor = '<section id="peerRoom">' if '<section id="peerRoom">' in html else "</main>"
    html = insert_before(html, section_anchor, FEED_SECTION + "\n" + ADMIN_SECTION, "main")
    html = insert_last_before(html, "</body>", f'<script id="teAdminStudioV425External">\n{js}\n</script>', "body")

    html = re.sub(r"<title>.*?</title>", "<title>Troll Engine - Classic Standard Edition v4.25 - Owner Studio</title>", html, count=1, flags=re.S | re.I)
    html = re.sub(r'(<meta\s+name=["\']troll-engine-classic-version["\']\s+content=["\'])[^"\']*(["\'])', r'\g<1>4.25\g<2>', html, count=1, flags=re.I)
    INDEX.write_text(html, encoding="utf-8")
    print("Published Troll Engine v4.25 Owner Studio")


if __name__ == "__main__":
    main()
