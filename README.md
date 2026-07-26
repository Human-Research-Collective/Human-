# Human Research Collective

ZINE「Human?」の制作を通して〈人間とは何か？〉を探求するコレクティブの静的サイト。

- **構成:** リポジトリ直下にサイト一式（`build.py`, `style.css`, `posts/*.md`、生成物の `*.html`）
- **URL:** 一覧は `…/Human-/`、各記事は `…/Human-/<スラッグ>`（`.html` なし。GitHub Pages が自動解決）
- **公開:** GitHub Pages（GitHub Actions でビルド & デプロイ）

## 記事の追加

`posts/` に frontmatter 付きの `.md` を1枚置いて、ビルドを実行するだけ。

```bash
pip install -r requirements.txt
python build.py
```

frontmatter の例:

```yaml
---
title: "記事タイトル"
date: 2026-06-20
category: "エッセイ"   # エッセイ/フォトエッセイ/お知らせ/その他（未指定は「その他」）
excerpt: "任意。全文検索の対象に含まれます。"
---
```

`python build.py` が全記事ページとブログ一覧を一括生成します。

## 特徴

- ヘッダー（タイトル＋サブタイトル）＋全文検索＋カテゴリ絞り込みのシンプル構成
- 全文検索（タイトル・本文をブラウザ内で横断検索）
- カテゴリ絞り込み（`build.py` の `CATEGORIES`）
- サムネイル・タグなしのミニマルなリスト表示
- ダーク/ライトは OS 設定（`prefers-color-scheme`）に追従
- Markdown を書くだけで記事が増やせるビルドスクリプト

タイトル・サブタイトル・ヘッダーリンク・カテゴリは `build.py` 冒頭の
`BLOG_TITLE` / `BLOG_SUBTITLE` / `BACK_LINK` / `CATEGORIES` で変更できます。
