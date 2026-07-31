# Troll Engine Yuuki

Troll Engineの中央管理・保存リポジトリです。v4.9から、全端末共通の公開データ、更新配信、招待設定、メンテナンス、機能スイッチ、ライブコンテンツをこのリポジトリへ集約します。

## 現在のバージョン

- バージョン: 4.9
- コード名: GitHub All-in-One Storage Update
- チャンネル: Stable
- 中央保存先: `chinoyuuki3-del/Troll-Engine-yuuki`

## 中央保存データ

- `data/storage.json` — 保存先と安全ルールの一覧
- `data/update.json` — 最新版情報
- `data/releases.json` — リリース一覧
- `data/invite.json` — 友達招待設定
- `data/maintenance.json` — 全端末メンテナンス
- `data/feature-control.json` — 緊急機能停止
- `data/test-channel.json` — テストチャンネル
- `data/plans.json` — プラン・容量
- `data/badges.json` — 実績・称号
- `projects.json` / `events.json` / `themes.json` — ライブコンテンツ
- `news.json` / `status.json` / `safety-rules.json` — お知らせ・稼働状況・安全ルール
- `users.json` — 公開ユーザー名とユーザーIDだけの検索一覧
- `releases/` — 配布用HTML

Troll Engineは5秒ごとに必要な管理データを確認します。GitHubへ接続できない場合は、端末に保存済みのデータを使います。

## セキュリティ

ブラウザ版Troll Engineはこのリポジトリを読み取り専用で利用します。GitHubトークンをHTMLへ埋め込みません。

次の情報は公開GitHubへ保存しません。

- パスワード
- 秘密のオーナーキー
- メールアドレス
- 個人チャット
- 友達一覧
- 位置履歴
- 非公開ファイル
