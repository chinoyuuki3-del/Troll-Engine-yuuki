# Troll Engine Yuuki

Troll Engineの更新、お知らせ、安全ルール、機能スイッチをGitHubで管理するリポジトリです。

## 現在のバージョン

- バージョン: 4.2
- コード名: GitHub Operations Control Update
- チャンネル: Stable
- 配信状態: HTMLアップロード準備中

## GitHubサービス

- `update.json` — 最新版の確認
- `releases.json` — バージョン履歴とダウンロード情報
- `news.json` — Troll Engine内のお知らせ
- `status.json` — サービスの稼働状況
- `features.json` — 機能の公開・停止とメンテナンス
- `safety-rules.json` — 追加安全ルールとBAN時間

## v4.2運営コントロール

Troll Engineは5分ごとにGitHub設定を確認します。GitHubへ接続できない場合は、保存済み設定または安全な初期設定を使います。基本安全フィルターはGitHub設定に関係なく常に有効です。

## 更新の流れ

1. 新しいHTMLをリポジトリへ追加します。
2. `update.json`と`releases.json`へ新しいバージョンを登録します。
3. `news.json`でアップデートをお知らせします。
4. HTMLのアップロード確認後に`download_ready`を`true`へ変更します。

## セキュリティ

秘密のオーナーキー、パスワード、ユーザー名、個人情報はGitHubへ保存しません。
