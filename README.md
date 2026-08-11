# Human Research Collective

ZINE「Human?」の制作を通して〈人間とは何か？〉を探求するコレクティブのブログ。

- **構成:** GitHub Pages 標準の **Jekyll** サイト。リポジトリ直下に記事の `.md` を置くだけ
- **URL:** 一覧は `…/Human-/`、各記事は `…/Human-/<ファイル名>`（`.html` なし）
- **公開:** GitHub Pages が `main` への push を自動でビルド＆公開（ビルドスクリプト不要）

## 記事の追加

リポジトリ直下に frontmatter 付きの `.md` を1枚置いて push するだけ。
ファイル名がそのまま URL になります（例: `ebina1.md` → `/Human-/ebina1`）。

```yaml
---
title: "記事タイトル"
date: 2026-06-20
category: "エッセイ"   # エッセイ/フォトエッセイ/お知らせ/ログ（未指定は「ログ」）
---

本文を Markdown で。
```

> 見出しは `## 見出し` のように `#` の後に**半角スペース**を入れてください（Jekyll の kramdown 仕様）。

## 画像の追加

画像は `images/` フォルダに入れます（GitHub の Web 画面からドラッグ＆ドロップでアップロード可）。
記事の Markdown からは次のように呼び出します。

```markdown
![説明文](images/ファイル名.jpg)
```

- ファイル名は**半角英数字**を推奨（日本語やスペースは避ける）
- 画像は自動で本文幅に収まり、角丸＋枠線が付きます（`style.css`）
- 写真はアップロード前に長辺 1600px 程度まで縮小しておくと表示が軽くなります

## OGP（SNS シェア時のカード画像）

全ページ共通で `images/ogp.png`（1200×630）を使います。差し替えるときは同じパスに
同じサイズの画像を置くか、`_config.yml` の `ogp_image` を変更してください。

> 反映されないときは各SNSのキャッシュが原因です。X なら
> [Card Validator](https://cards-dev.twitter.com/validator)、Facebook なら
> [Sharing Debugger](https://developers.facebook.com/tools/debug/) で再取得できます。

## サイトの設定

`_config.yml` で変更できます。

| 項目 | キー |
|---|---|
| ブログ名 | `title` |
| サブタイトル | `subtitle` |
| カテゴリと表示順 | `categories_list` |
| 未指定時のカテゴリ | `default_category` |

見た目は `style.css`、ページ構造は `_layouts/`（`default.html` / `post.html`）と `index.html`。

## 特徴

- ヘッダー（タイトル＋サブタイトル）＋全文検索＋カテゴリ絞り込みのシンプル構成
- 全文検索（タイトル・本文をブラウザ内で横断検索。ビルド時に埋め込み）
- サムネイル・タグなしのミニマルなリスト表示
- ダーク/ライトは OS 設定（`prefers-color-scheme`）に追従

## 隠しページ `/secret`

パスワードで保護されたページ（フッターの「community」からアクセス）。
本文は AES-256-GCM で暗号化して `secret.html` に埋め込まれており、
正しいパスワード入力時のみブラウザ内で復号されます。

内容を更新するには、平文の `secret_content.md`（Git 管理外）を編集して再生成します。

```bash
pip install -r requirements.txt
SECRET_PW='パスワード' python3 make_secret.py
```

生成された `secret.html` をコミットすれば反映されます（別の `.md` を引数で指定も可）。
`secret.html` は Jekyll に処理されない静的ファイルとしてそのまま配信されます。
