#!/usr/bin/env python3
"""
Instagram ストーリー告知画像ジェネレーター（Human Research Collective）

新しいエッセイを公開したときの告知用。タイトルと引用（あれば著者・カテゴリ）を
差し替えるだけで、ブランドに合わせた 1080x1920 の縦長画像を書き出す。
サイトのコード（Jekyll ビルド）には一切影響しない、ローカル用の道具。

使い方:
    pip install Pillow
    python3 tools/make_story.py \
      --title "村上春樹のカキフライと僕のジントニック" \
      --quote "距離のないところに、物語は宿らない。" \
      --author "渡辺浩太朗" \
      --category "エッセイ" \
      --out ~/Desktop/story.png

--out を省略すると tools/out/<タイトル>.png に書き出す。
"""

import argparse
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG = "#ffffff"
INK = "#111214"
MUTED = "#8a8d91"
LINE = "#e6e6e7"

# 上下の安全マージン。
# 上：Instagram 側の時計・アイコン類、下：返信欄＋リンクスタンプの置き場を確保する。
TOP_SAFE = 300
BOTTOM_SAFE = 420
SIDE_MARGIN = 96
CONTENT_W = W - SIDE_MARGIN * 2

HELVETICA = "/System/Library/Fonts/Helvetica.ttc"
HIRAGINO = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"   # 太字寄り（見出し用）
HIRAGINO_MED = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"  # 本文寄り


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def is_latin(ch):
    return ord(ch) < 0x2E80  # 日本語・記号の手前まではラテン圏として扱う


def char_width(draw, ch, f_latin, f_cjk):
    f = f_latin if is_latin(ch) else f_cjk
    return draw.textlength(ch, font=f)


def wrap_mixed(draw, text, f_latin, f_cjk, max_width):
    """英数字はなるべく単語単位、日本語は文字単位で折り返す。"""
    text = unicodedata.normalize("NFC", text)
    words = re.findall(r"[A-Za-z0-9.,!?'\"\-]+|.", text, re.UNICODE)
    lines, cur, cur_w = [], "", 0
    for w in words:
        seg_w = sum(char_width(draw, c, f_latin, f_cjk) for c in w)
        if cur and cur_w + seg_w > max_width:
            lines.append(cur)
            cur, cur_w = "", 0
        cur += w
        cur_w += seg_w
    if cur:
        lines.append(cur)
    return lines


def draw_centered_lines(draw, lines, f_latin, f_cjk, top, line_h, fill):
    y = top
    for line in lines:
        w = sum(char_width(draw, c, f_latin, f_cjk) for c in line)
        x = (W - w) / 2
        cx = x
        for ch in line:
            f = f_latin if is_latin(ch) else f_cjk
            draw.text((cx, y), ch, font=f, fill=fill)
            cx += draw.textlength(ch, font=f)
        y += line_h
    return y


def fit_title(draw, title, f_latin_path, f_cjk_path, max_width, max_lines=4,
              start_size=88, min_size=52):
    size = start_size
    while size >= min_size:
        f_latin = font(f_latin_path, size, index=1)
        f_cjk = font(f_cjk_path, size)
        lines = wrap_mixed(draw, title, f_latin, f_cjk, max_width)
        if len(lines) <= max_lines:
            return lines, f_latin, f_cjk, size
        size -= 4
    return lines, f_latin, f_cjk, size


def make_story(title, quote, author, category, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    y = TOP_SAFE

    # ---- カテゴリ（eyebrow） ----
    if category:
        f_cat = font(HIRAGINO_MED, 34)
        w = d.textlength(category, font=f_cat)
        d.text(((W - w) / 2, y), category, font=f_cat, fill=MUTED)
        y += 34 + 36

    # ---- タイトル ----
    title_lines, f_t_latin, f_t_cjk, title_size = fit_title(
        d, title, HELVETICA, HIRAGINO, CONTENT_W
    )
    title_line_h = int(title_size * 1.32)
    y = draw_centered_lines(d, title_lines, f_t_latin, f_t_cjk, y, title_line_h, INK)
    y += 44

    # ---- 区切り線 ----
    d.line([(W / 2 - 46, y), (W / 2 + 46, y)], fill=LINE, width=3)
    y += 60

    # ---- 引用 ----
    if quote:
        q = quote.strip()
        if not q.startswith("「"):
            q = "「" + q
        if not q.endswith("」"):
            q = q + "」"
        f_q_latin = font(HELVETICA, 52)
        f_q_cjk = font(HIRAGINO_MED, 52)
        q_lines = wrap_mixed(d, q, f_q_latin, f_q_cjk, CONTENT_W - 40)
        y = draw_centered_lines(d, q_lines, f_q_latin, f_q_cjk, y, 82, INK)

    # ---- フッター（ワードマーク・著者名）：下の安全域のすぐ上に固定 ----
    footer_top = H - BOTTOM_SAFE - 120
    d.line([(SIDE_MARGIN, footer_top), (W - SIDE_MARGIN, footer_top)], fill=LINE, width=2)

    f_brand = font(HELVETICA, 34, index=1)
    brand = "Human Research Collective"
    bw = d.textlength(brand, font=f_brand)
    d.text(((W - bw) / 2, footer_top + 34), brand, font=f_brand, fill=INK)

    if author:
        f_author = font(HIRAGINO_MED, 30)
        a = author
        aw = d.textlength(a, font=f_author)
        d.text(((W - aw) / 2, footer_top + 34 + 48), a, font=f_author, fill=MUTED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True)
    ap.add_argument("--quote", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--category", default="")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.out:
        out_path = Path(args.out).expanduser()
    else:
        slug = re.sub(r"[^\w\-]+", "_", args.title).strip("_")[:40] or "story"
        out_path = Path(__file__).parent / "out" / f"{slug}.png"

    result = make_story(args.title, args.quote, args.author, args.category, out_path)
    print(f"✅ 書き出しました: {result}")


if __name__ == "__main__":
    main()
