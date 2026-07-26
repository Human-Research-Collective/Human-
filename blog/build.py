#!/usr/bin/env python3
"""
Human Research Collective Blog ビルドスクリプト

使い方:
    python3 build.py

posts/ 内の *.md を読み込み、記事ページと index.html を生成する。
記事の追加は「posts/ に .md を1枚置いて、このスクリプトを実行する」だけ。
"""

import re
import html
from pathlib import Path
import markdown

ROOT = Path(__file__).parent          # blog/ ディレクトリ
POSTS_DIR = ROOT / "posts"

# ブログのタイトル・説明
BLOG_TITLE = "Human Research Collective Blog"
BLOG_SUBTITLE = "ZINE「Human?」制作の記録。お知らせ・エッセイ・寄稿募集など。"
# ヘッダー左上の外部リンク（無くしたい場合は None）
BACK_LINK = None

# カテゴリ（絞り込みの表示順）。記事の frontmatter で category を指定する。
CATEGORIES = ["エッセイ", "フォトエッセイ", "お知らせ", "その他"]
DEFAULT_CATEGORY = "その他"

# ---- 共通パーツ -------------------------------------------------------------

def footer_html():
    return """  <footer class="site-footer">
    <div class="site-footer__inner">
      <span>© 2026 Human Research Collective</span>
      <div class="social">
        <a href="https://humanresearchcollective.substack.com/" target="_blank" rel="noopener">Substack</a>
        <a href="https://hrc.theshop.jp/" target="_blank" rel="noopener">STORE</a>
      </div>
    </div>
  </footer>"""

def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="style.css?v=3" />
</head>
<body>
  <div class="wrap">
{body}
  </div>
{footer_html()}
</body>
</html>
"""

# ---- frontmatter パーサ -----------------------------------------------------

def parse_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"frontmatter がありません: {path.name}")
    meta_block, body_md = m.group(1), m.group(2)

    meta = {}
    for line in meta_block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        # 前後の対になるクオートを除去
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        meta[key.strip()] = val

    for req in ("title", "date"):
        if req not in meta:
            raise ValueError(f"{path.name}: '{req}' が frontmatter にありません")

    meta["slug"] = path.stem                 # 出力ファイル名に使用
    meta["category"] = meta.get("category", "").strip() or DEFAULT_CATEGORY
    body_html = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
    meta["body_html"] = body_html
    meta.setdefault("excerpt", "")

    # 全文検索用のプレーンテキスト（タイトル＋本文）
    plain = re.sub(r"<[^>]+>", " ", body_html)
    plain = html.unescape(plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    meta["plain"] = (meta["title"] + " " + plain).lower()
    return meta

def date_ja(iso):
    y, mth, d = iso.split("-")
    return f"{int(y)}年{int(mth):02d}月{int(d):02d}日"

# ---- 記事ページ生成 ---------------------------------------------------------

def render_article(p):
    body = f"""    <article class="article">
      <a href="index.html" class="article__back">← ブログ一覧へ戻る</a>
      <h1 class="article__title">{html.escape(p["title"])}</h1>
      <div class="article__meta">
        <span class="article__cat">{html.escape(p["category"])}</span>
        <span class="article__date">{date_ja(p["date"])}</span>
      </div>
      <div class="article__body">
{p["body_html"]}
      </div>
    </article>"""
    out = ROOT / f'{p["slug"]}.html'
    out.write_text(page(f'{p["title"]} | {BLOG_TITLE}', body), encoding="utf-8")
    return out.name

# ---- 一覧ページ生成 ---------------------------------------------------------

def blog_head_html():
    back = ""
    if BACK_LINK:
        label, href = BACK_LINK
        back = (f'      <a href="{html.escape(href)}" class="blog-head__back" '
                f'target="_blank" rel="noopener">{html.escape(label)}</a>\n')
    return f"""    <header class="blog-head">
{back}      <h1 class="blog-head__title">{html.escape(BLOG_TITLE)}</h1>
      <p class="blog-head__sub">{html.escape(BLOG_SUBTITLE)}</p>
    </header>"""

def search_html():
    return """    <div class="search">
      <input type="search" class="search__input" placeholder="全文検索（記事横断）…" aria-label="全文検索" />
      <button class="search__btn" type="button">検索</button>
    </div>"""

def catfilter_html():
    pills = ['      <button class="pill is-active" type="button" data-cat="all">all</button>']
    for c in CATEGORIES:
        ce = html.escape(c)
        pills.append(f'      <button class="pill" type="button" data-cat="{ce}">{ce}</button>')
    return ('    <div class="catfilter">\n'
            '      <div class="catfilter__label">カテゴリで絞り込む</div>\n'
            '      <div class="catfilter__pills">\n'
            + "\n".join(pills) +
            '\n      </div>\n    </div>')

def render_index(posts):
    cards = []
    for p in posts:
        link = f'{p["slug"]}.html'
        data_search = html.escape(p["plain"], quote=True)
        data_cat = html.escape(p["category"], quote=True)
        cards.append(f"""      <article class="post" data-category="{data_cat}" data-search="{data_search}">
        <a href="{link}" class="post__title">{html.escape(p["title"])}</a>
        <div class="post__meta">
          <span class="post__cat">{html.escape(p["category"])}</span>
          <span class="post__date">{date_ja(p["date"])}</span>
        </div>
      </article>""")

    empty = '      <p class="posts__empty" hidden>該当する記事はありません。</p>'
    body = "\n\n".join([
        blog_head_html(),
        search_html(),
        catfilter_html(),
        '    <main class="posts">\n' + "\n\n".join(cards) + "\n" + empty + "\n    </main>",
        FILTER_JS,
    ])
    (ROOT / "index.html").write_text(page(BLOG_TITLE, body), encoding="utf-8")

# 一覧の絞り込み（カテゴリ＋全文検索）
FILTER_JS = """    <script>
    (function () {
      var posts = Array.prototype.slice.call(document.querySelectorAll(".post"));
      var empty = document.querySelector(".posts__empty");
      var input = document.querySelector(".search__input");
      var btn = document.querySelector(".search__btn");
      var pills = Array.prototype.slice.call(document.querySelectorAll(".catfilter .pill"));
      var activeCat = "all";

      function apply() {
        var q = (input && input.value || "").trim().toLowerCase();
        var shown = 0;
        posts.forEach(function (el) {
          var okCat = activeCat === "all" || el.getAttribute("data-category") === activeCat;
          var okQ = q === "" || (el.getAttribute("data-search") || "").indexOf(q) !== -1;
          var show = okCat && okQ;
          el.hidden = !show;
          if (show) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
      }

      function setCat(cat) {
        activeCat = cat;
        pills.forEach(function (p) {
          p.classList.toggle("is-active", p.getAttribute("data-cat") === cat);
        });
        apply();
      }

      pills.forEach(function (p) {
        p.addEventListener("click", function () { setCat(p.getAttribute("data-cat")); });
      });

      // 記事カード内のカテゴリをクリックしても絞り込む
      document.querySelectorAll(".post .post__cat").forEach(function (c) {
        c.style.cursor = "pointer";
        c.addEventListener("click", function () {
          setCat(c.textContent.trim());
          window.scrollTo({ top: 0, behavior: "smooth" });
        });
      });

      if (input) input.addEventListener("input", apply);
      if (btn) btn.addEventListener("click", apply);
      apply();
    })();
    </script>"""

# ---- main -------------------------------------------------------------------

def main():
    md_files = sorted(POSTS_DIR.glob("*.md"))
    if not md_files:
        print("posts/ に .md がありません。")
        return
    posts = [parse_post(f) for f in md_files]
    posts.sort(key=lambda p: p["date"], reverse=True)   # 新しい順

    for p in posts:
        name = render_article(p)
        print(f"  記事生成: {name}")
    render_index(posts)
    print(f"\n✅ 完了: {len(posts)}件の記事 + 一覧を生成しました。")

if __name__ == "__main__":
    main()
