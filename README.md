# Human Research Collective

ZINE「Human?」の制作を通して〈人間とは何か？〉を探求するコレクティブの静的サイト。

- **ブログ:** `blog/`（`build.py`, `style.css`, `posts/*.md`, `images/`）
- **ルート:** `index.html` は `blog/` へのリダイレクト（サイトはブログのみ）
- **公開:** GitHub Pages（GitHub Actions でビルド & デプロイ）

## 記事の追加

`blog/posts/` に frontmatter 付きの `.md` を1枚置いて、ビルドを実行するだけ。

```bash
pip install -r requirements.txt
python blog/build.py
```

frontmatter の例:

```yaml
---
title: "記事タイトル"
date: 2026-06-20
excerpt: "任意。全文検索の対象に含まれます。"
---
```

`python blog/build.py` が全記事ページとブログ一覧を一括生成します。

## 特徴

- ヘッダー（タイトル＋サブタイトル）＋全文検索＋記事リストのシンプル構成
- 全文検索（タイトル・本文をブラウザ内で横断検索。クリックで絞り込み）
- サムネイル・タグなしのミニマルなリスト表示
- ダーク/ライトは OS 設定（`prefers-color-scheme`）に追従
- Markdown を書くだけで記事が増やせるビルドスクリプト

ブログのタイトル・サブタイトル・ヘッダーリンクは `blog/build.py` 冒頭の
`BLOG_TITLE` / `BLOG_SUBTITLE` / `BACK_LINK` で変更できます。
