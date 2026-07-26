#!/usr/bin/env python3
"""
パスワード付き隠しページ secret.html を生成するスクリプト。

- 保護したい本文は secret_content.html（平文・Git管理外）に書く。
- パスワードは環境変数 SECRET_PW で渡す（未指定なら対話入力）。
- 本文を AES-256-GCM で暗号化し、salt/iv/暗号文だけを secret.html に埋め込む。
  → ソースを見ても暗号文しか見えず、正しいパスワード入力時のみブラウザ内で復号。

使い方:
    pip install cryptography
    SECRET_PW='あなたのパスワード' python3 make_secret.py
"""

import os
import base64
import getpass
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).parent
CONTENT = ROOT / "secret_content.html"
OUT = ROOT / "secret.html"
ITERATIONS = 200_000

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex, nofollow" />
  <title>secret | Human Research Collective</title>
  <link rel="stylesheet" href="style.css?v=3" />
  <style>
    .secret {{ max-width: 640px; margin: 0 auto; padding: 40px 0 24px; text-align: center; }}
    .secret__eyebrow {{ font-size: 12px; letter-spacing: 0.32em; text-transform: uppercase; color: var(--muted); font-weight: 700; }}
    .secret__mark {{ font-size: 56px; margin: 22px 0 6px; }}
    .secret__title {{ font-size: 30px; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 20px; }}
    .secret__body p {{ font-size: 16.5px; color: var(--text); margin: 14px 0; line-height: 1.85; }}
    .secret__quote {{ margin: 32px auto; padding: 4px 0; font-size: 18px; color: var(--cat); font-weight: 700; }}
    .secret__back {{ display: inline-block; margin-top: 28px; font-size: 14px; color: var(--muted); }}
    .secret__back:hover {{ color: var(--text); }}
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
          var html=await unlock(input.value);
          out.innerHTML=html;
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


def main():
    if not CONTENT.exists():
        raise SystemExit(f"{CONTENT.name} がありません。保護したい本文を書いてください。")
    plaintext = CONTENT.read_text(encoding="utf-8").encode("utf-8")

    pw = os.environ.get("SECRET_PW") or getpass.getpass("パスワード: ")
    if not pw:
        raise SystemExit("パスワードが空です。")

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITERATIONS, dklen=32)
    ct = AESGCM(key).encrypt(iv, plaintext, None)

    b64 = lambda b: base64.b64encode(b).decode()
    OUT.write_text(
        TEMPLATE.format(salt=b64(salt), iv=b64(iv), ct=b64(ct), iter=ITERATIONS),
        encoding="utf-8",
    )
    print(f"✅ {OUT.name} を生成しました（AES-256-GCM / PBKDF2 {ITERATIONS} 回）。")


if __name__ == "__main__":
    main()
