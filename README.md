# Troll Engine Yuuki

Troll Engineの中央管理・保存リポジトリです。v4.10では、約1,000本のMega Store、ライブ文章、映像・音声P2Pライブ、一般ユーザー向けAFT動画・過去ライブを追加しました。

## 現在のバージョン

- バージョン: 4.10
- コード名: Mega Store & Live Broadcast Update
- チャンネル: Stable
- 中央保存先: `chinoyuuki3-del/Troll-Engine-yuuki`

## v4.10

- 既存123本＋新規877本、合計約1,000本のオンラインストア
- 最高管理者のカメラ＋音声、画面＋音声、音声のみのP2Pライブ
- このHTMLを持つ一般ユーザーがライブを視聴可能
- 配信終了時、最高管理者の端末へ過去配信を自動録画
- GitHubで公開した録画をAFT動画として一般ユーザーも再生可能
- 最高管理者がライブ文章を入力し、GitHub経由で全端末へ配信

## 中央保存データ

- `data/store-catalog.json` — Mega Storeカタログ
- `data/live-messages.json` — ライブ文章
- `data/aft-videos.json` — 公開済みAFT動画・過去ライブ
- `data/storage.json` — 保存先と安全ルール
- `data/update.json` / `data/releases.json` — 更新配信
- `data/invite.json` — 友達招待設定
- `data/maintenance.json` / `data/feature-control.json` — メンテナンス・機能制御
- `data/test-channel.json` / `data/plans.json` / `data/badges.json`
- `projects.json` / `events.json` / `themes.json` — ライブコンテンツ
- `releases/` — 配布用HTML

## ライブ保存

ライブ中の映像・音声はP2Pで視聴者へ送られます。録画は最高管理者の端末内へ保存され、未公開の録画はGitHubへ自動送信しません。GitHub Releasesへ公開した動画URLだけを `data/aft-videos.json` へ登録し、一般ユーザーの過去ライブ一覧へ表示します。

## セキュリティ

ブラウザ版Troll EngineはGitHubを読み取り専用で利用し、秘密トークンをHTMLへ埋め込みません。パスワード、オーナーキー、メール、個人チャット、友達一覧、位置履歴、非公開ファイル、未公開録画は公開GitHubへ保存しません。
