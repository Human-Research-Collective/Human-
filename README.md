# Human Research Collective

ZINE「Human?」の制作を通して〈人間とは何か？〉を探求するコレクティブの静的サイト。

- **トップページ:** リポジトリルート（`index.template.html` → `index.html` を生成、`home.css`）
- **ブログ:** `blog/`（`build.py`, `style.css`, `posts/*.md`, `images/`）
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
category: "お知らせ"   # お知らせ/エッセイ/寄稿募集
excerpt: "一覧に表示される概要文。"
thumbnail: images/thumb-news.svg   # 任意
---
```

`python blog/build.py` が全記事ページ・ブログ一覧・トップページの「最新記事」を一括生成します。

## 特徴

- ダークモード切り替え（ヘッダー右上トグル、`localStorage` で記憶）
- カテゴリによる一覧の絞り込み（クリックで表示/非表示）
- Markdown を書くだけで記事が増やせるビルドスクリプト
