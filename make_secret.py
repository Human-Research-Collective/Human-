#!/usr/bin/env python3
"""
パスワード付き隠しページ secret.html を生成するスクリプト。

- 保護したい本文は Markdown で書く（デフォルト: secret_content.md、平文・Git管理外）。
  frontmatter は記事と同じ（title / date 必須、category 任意）。
- パスワードは環境変数 SECRET_PW で渡す（未指定なら対話入力）。
- 本文を AES-256-GCM で暗号化し、salt/iv/暗号文だけを secret.html に埋め込む。
  → ソースを見ても暗号文しか見えず、正しいパスワード入力時のみブラウザ内で復号。

使い方:
    pip install cryptography markdown
    SECRET_PW='あなたのパスワード' python3 make_secret.py            # secret_content.md を使う
    SECRET_PW='...' python3 make_secret.py path/to/other.md          # 別の .md を指定
"""

import os
import re
import sys
import html
import base64
import getpass
import hashlib
from pathlib import Path

import markdown
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "secret_content.md"
OUT = ROOT / "secret.html"
ITERATIONS = 200_000

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex, nofollow" />
  <title>secret | Human Research Collective</title>
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Human Research Collective Blog" />
  <meta property="og:locale" content="ja_JP" />
  <meta property="og:title" content="Human Research Collective" />
  <meta property="og:description" content="ZINE「Human?」の制作を通して〈人間とは何か？〉を探求するコレクティブ。" />
  <meta property="og:url" content="https://human-research-collective.github.io/Human-/secret" />
  <meta property="og:image" content="https://human-research-collective.github.io/Human-/images/ogp.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="https://human-research-collective.github.io/Human-/images/ogp.png" />
  <link rel="stylesheet" href="style.css?v=4" />
  <style>
    .secret {{ max-width: 640px; margin: 0 auto; padding: 40px 0 24px; text-align: center; }}
    .secret__eyebrow {{ font-size: 12px; letter-spacing: 0.32em; text-transform: uppercase; color: var(--muted); font-weight: 700; }}
    .secret__mark {{ font-size: 56px; margin: 22px 0 6px; }}
    .secret__title {{ font-size: 30px; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 20px; }}
    .secret__body p {{ font-size: 16.5px; color: var(--text); margin: 14px 0; line-height: 1.85; }}
    .lock__form {{ display: flex; gap: 12px; max-width: 420px; margin: 8px auto 0; }}
    .lock__input {{ flex: 1 1 auto; min-width: 0; font: inherit; font-size: 15px; padding: 13px 18px; color: var(--text); background: var(--bg); border: 1px solid var(--input-border); border-radius: 10px; outline: none; }}
    .lock__input:focus {{ border-color: var(--text); }}
    .lock__btn {{ flex: none; font: inherit; font-weight: 700; font-size: 15px; padding: 0 24px; color: var(--btn-text); background: var(--btn-bg); border: none; border-radius: 10px; cursor: pointer; }}
    .lock__err {{ margin-top: 16px; color: #e5484d; font-size: 14px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="secret lock">
      <div class="secret__eyebrow">SECRET</div>
      <div class="secret__mark">🔒</div>
      <h1 class="secret__title">パスワードが必要です</h1>
      <div class="secret__body"><p>このページを見るにはパスワードを入力してください。</p></div>
      <form class="lock__form">
        <input class="lock__input" type="password" placeholder="パスワード" autocomplete="off" aria-label="パスワード" autofocus />
        <button class="lock__btn" type="submit">解錠</button>
      </form>
      <p class="lock__err" hidden>パスワードが違います。</p>
    </section>
    <div class="secret-content" hidden></div>
  </div>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <span>© 2026 Human Research Collective</span>
      <div class="social">
        <a href="secret">community</a>
        <a href="https://humanresearchcollective.substack.com/" target="_blank" rel="noopener">Substack</a>
        <a href="https://hrc.theshop.jp/" target="_blank" rel="noopener">STORE</a>
      </div>
    </div>
  </footer>
  <script>
    var SALT="{salt}", IV="{iv}", CT="{ct}", ITER={iter};
    function b64d(s){{return Uint8Array.from(atob(s), function(c){{return c.charCodeAt(0);}});}}
    async function unlock(pw){{
      var enc=new TextEncoder();
      var base=await crypto.subtle.importKey("raw", enc.encode(pw), "PBKDF2", false, ["deriveKey"]);
      var key=await crypto.subtle.deriveKey(
        {{name:"PBKDF2", salt:b64d(SALT), iterations:ITER, hash:"SHA-256"}},
        base, {{name:"AES-GCM", length:256}}, false, ["decrypt"]);
      var pt=await crypto.subtle.decrypt({{name:"AES-GCM", iv:b64d(IV)}}, key, b64d(CT));
      return new TextDecoder().decode(pt);
    }}
    (function(){{
      var form=document.querySelector(".lock__form");
      var input=document.querySelector(".lock__input");
      var err=document.querySelector(".lock__err");
      var gate=document.querySelector(".lock");
      var out=document.querySelector(".secret-content");
      form.addEventListener("submit", async function(e){{
        e.preventDefault();
        err.hidden=true;
        try{{
          var htmlText=await unlock(input.value);
          out.innerHTML=htmlText;
          gate.hidden=true;
          out.hidden=false;
        }}catch(_){{
          err.hidden=false;
          input.value="";
          input.focus();
        }}
      }});
    }})();
  </script>
</body>
</html>
"""


def parse_md(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not m:
        raise SystemExit(f"{path.name}: frontmatter（--- で囲む title/date）が必要です。")
    meta_block, body_md = m.group(1), m.group(2)

    meta = {}
    for line in meta_block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        meta[key.strip()] = val

    for req in ("title", "date"):
        if req not in meta:
            raise SystemExit(f"{path.name}: '{req}' が frontmatter にありません。")

    # 見出しの # の直後に空白が無くても h タグにする（##Foo → ## Foo）
    body_md = re.sub(r"(?m)^(#{1,6})(?=\S)", r"\1 ", body_md)
    meta["body_html"] = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
    return meta


def date_ja(iso):
    try:
        y, mth, d = iso.split("-")
        return f"{int(y)}年{int(mth):02d}月{int(d):02d}日"
    except Exception:
        return iso


def build_article(meta):
    cat = meta.get("category", "").strip()
    cat_html = f'<span class="article__cat">{html.escape(cat)}</span>\n        ' if cat else ""
    return f"""<article class="article">
  <a href="./" class="article__back">← ブログ一覧へ戻る</a>
  <h1 class="article__title">{html.escape(meta["title"])}</h1>
  <div class="article__meta">
        {cat_html}<span class="article__date">{date_ja(meta["date"])}</span>
  </div>
  <div class="article__body">
{meta["body_html"]}
  </div>
</article>"""


def main():
    if not SRC.exists():
        raise SystemExit(f"{SRC} がありません。保護したい本文を Markdown で書いてください。")
    content = build_article(parse_md(SRC)).encode("utf-8")

    pw = os.environ.get("SECRET_PW") or getpass.getpass("パスワード: ")
    if not pw:
        raise SystemExit("パスワードが空です。")

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITERATIONS, dklen=32)
    ct = AESGCM(key).encrypt(iv, content, None)

    b64 = lambda b: base64.b64encode(b).decode()
    OUT.write_text(
        TEMPLATE.format(salt=b64(salt), iv=b64(iv), ct=b64(ct), iter=ITERATIONS),
        encoding="utf-8",
    )
    print(f"✅ {OUT.name} を生成しました（source: {SRC.name} / AES-256-GCM / PBKDF2 {ITERATIONS}）。")


if __name__ == "__main__":
    main()
