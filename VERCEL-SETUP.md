# Troll Engine Vercel Server v1

この構成では、Troll Engineの実行/APIをVercelに置き、永続データの最終保存先をGitHubにします。

## 役割

- Vercel: 静的画面、認証付きAPI、GitHubへの読み書き
- GitHub: 本体HTML、JSON、画像、短い音声・短い動画、GitHub Releaseの大きな動画
- PeerJS / WebRTC: リアルタイム映像・音声

## 必須のVercel環境変数

- `GITHUB_TOKEN`: 対象リポジトリのContentsを読み書きできるFine-grained token
- `GITHUB_REPO`: `chinoyuuki3-del/Troll-Engine-yuuki`
- `GITHUB_BRANCH`: `main`
- `TROLL_ENGINE_API_KEY`: オーナー用ツールから書き込みAPIを呼ぶための長いランダム文字列
- `TROLL_ENGINE_CORS_ORIGIN`: 本番Vercel URL。初期確認だけなら `*`

秘密値をHTML、JSON、GitHubコミットへ書かないでください。現在の書き込みAPIはオーナー・管理ツール向けです。一般ユーザー投稿には、別途ユーザー認証と短時間セッションを追加します。

## API

### 稼働確認

`GET /api/health`

### JSON読み込み

`GET /api/data?path=data/update.json`

### JSON保存

`PUT /api/data`

```json
{
  "path": "data/example.json",
  "value": { "hello": "world" },
  "message": "Update example data"
}
```

ヘッダーに `Authorization: Bearer <TROLL_ENGINE_API_KEY>` を付けます。

### 小さいメディア保存

`POST /api/media`

```json
{
  "path": "voice/example.webm",
  "contentBase64": "...",
  "message": "Upload voice message"
}
```

このAPIでは最大2.5MBです。ボイスメッセージや短いクリップ向けです。

## 大きな動画

大きな動画はGitHub Releaseのassetへ置き、そのURLを `data/aft-videos.json` に登録します。Vercel APIへ大容量動画を丸ごと通す方式にはしません。

## 公開リポジトリの注意

現在のリポジトリはpublicです。保存されたJSON・動画・音声は原則として誰でも取得できます。パスワード、秘密トークン、個人チャット、正確な位置履歴などは保存しないでください。
