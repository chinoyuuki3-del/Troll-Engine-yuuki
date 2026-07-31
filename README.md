# Troll Engine Yuuki

Troll Engineの更新、お知らせ、安全ルール、機能スイッチ、ライブコンテンツをGitHubで管理するリポジトリです。

## 現在のバージョン

- バージョン: 4.3
- コード名: GitHub Live Content Update
- チャンネル: Stable

## GitHub自動更新データ

- `projects.json` — 公式プロジェクト
- `events.json` — イベント
- `themes.json` — テーマ
- `メンテナンス.json` — 専用メンテナンス設定
- `features.json` — 機能の公開・停止
- `safety-rules.json` — 追加安全ルール
- `news.json` — お知らせ
- `status.json` — 稼働状況
- `update.json` — 最新版情報
- `releases.json` — バージョン履歴

v4.3はGitHubデータを5分ごとに取得します。プロジェクト、イベント、テーマ、メンテナンスの内容変更ではHTMLの再アップロードは不要です。GitHubへ接続できない場合は保存済みデータを使用します。

## セキュリティ

秘密のオーナーキー、パスワード、ユーザー名、個人情報はGitHubへ保存しません。
