# -*- coding: utf-8 -*-
"""わたしの蔵書館 — Streamlit版"""
import hashlib
import html
import json
import os

import streamlit as st

# ============================================================
# 基本設定
# ============================================================
st.set_page_config(page_title="わたしの蔵書館", page_icon="📚", layout="centered")

DATA_FILE = os.path.join("data", "library.json")
SHELVES_PER_CASE = 5      # 一つの本棚は五段
SHELF_MAX_PX = 640        # 一段に並べられる幅(px)

TYPE_INFO = {
    "site":  {"label": "ウェブサイト", "color": "#2f4a6b"},
    "video": {"label": "動画",         "color": "#7a2e2a"},
    "file":  {"label": "ファイル",     "color": "#3c5a3a"},
    "memo":  {"label": "メモ",         "color": "#a8842c"},
}
COLORS = [
    ("藍",   "#2f4a6b"), ("えんじ", "#7a2e2a"), ("松葉", "#3c5a3a"),
    ("芥子", "#a8842c"), ("茄子",   "#4a3457"), ("浅葱", "#2d6e72"),
    ("珊瑚", "#b25e4a"), ("墨",     "#3a3733"),
]
DECOS = [("label", "紙ラベル"), ("gold", "金線"), ("plain", "無地")]
DEFAULT_WALLS = ["北の壁", "東の壁", "南の壁", "西の壁"]
SAMPLES = [
    {"title": "旅の写真 2025", "type": "file", "size": 18},
    {"title": "作業用BGM集", "type": "video", "size": 8, "url": "https://example.com"},
    {"title": "レシピのまとめ", "type": "site", "size": 3, "url": "https://example.com"},
    {"title": "確定申告メモ", "type": "memo", "size": 1},
    {"title": "映画の感想ノート", "type": "memo", "size": 2},
    {"title": "家計簿データ", "type": "file", "size": 6},
    {"title": "よく見るニュース", "type": "site", "size": 2, "url": "https://example.com"},
    {"title": "卒業式の動画", "type": "video", "size": 24, "url": "https://example.com"},
]

# ============================================================
# データの読み書き
# ============================================================
def default_data():
    return {
        "walls": [{"name": n} for n in DEFAULT_WALLS],
        "books": [],
        "total_gb": 512,
    }


def load_data():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            d = json.load(f)
        if not d.get("walls"):
            d["walls"] = [{"name": n} for n in DEFAULT_WALLS]
        d.setdefault("books", [])
        d.setdefault("total_gb", 512)
        return d
    except Exception:
        return default_data()


def save_data(d):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


data = load_data()
walls = data["walls"]
books = data["books"]
used_gb = sum(b["size"] for b in books)

# ============================================================
# 見た目(CSS)
# ============================================================
st.markdown("""
<style>
.stApp{
  background:
    radial-gradient(ellipse at 50% -10%, rgba(255,220,150,.18), transparent 60%),
    linear-gradient(#33402f, #27311f);
}
.lib-header{
  font-family:"Hiragino Mincho ProN","Yu Mincho",serif;
  letter-spacing:.35em;font-size:1.5rem;color:#f3e9d2;text-align:center;margin:.2rem 0 0;
}
.lib-sub{
  letter-spacing:.3em;font-size:.6rem;color:#c9a227;text-align:center;margin-bottom:.8rem;
}
.gauge-label{font-size:.72rem;letter-spacing:.1em;color:#f3e9d2;opacity:.9;
  display:flex;justify-content:space-between;margin-bottom:4px;font-family:serif}
.gauge-bar{height:12px;border:1px solid #c9a227;border-radius:7px;
  background:rgba(0,0,0,.35);overflow:hidden;box-shadow:inset 0 1px 3px rgba(0,0,0,.6);margin-bottom:1rem}
.gauge-fill{height:100%;background:linear-gradient(90deg,#8a6d1f,#c9a227,#e8c95a)}
.bookcase{
  background:linear-gradient(#5b3c20,#4a311a);
  border:6px solid #5b3c20;border-radius:8px;
  box-shadow:0 18px 40px rgba(0,0,0,.55), inset 0 0 30px rgba(0,0,0,.5);
  padding:10px 12px 4px;margin-top:.4rem;
}
.shelf{
  position:relative;min-height:150px;
  display:flex;align-items:flex-end;gap:2px;
  padding:6px 8px 0;
  background:linear-gradient(rgba(0,0,0,.35), rgba(0,0,0,.15));
  border-bottom:14px solid #7a5230;
}
.shelf-empty{
  position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:.7rem;letter-spacing:.25em;color:rgba(243,233,210,.25);font-family:serif;
}
.book{
  position:relative;border-radius:2px 2px 0 0;
  display:inline-flex;align-items:flex-start;justify-content:center;
  writing-mode:vertical-rl;
  font-family:"Hiragino Mincho ProN","Yu Mincho",serif;
  font-size:.72rem;letter-spacing:.08em;
  color:rgba(255,250,235,.92) !important;
  padding-top:16px;overflow:hidden;flex-shrink:0;
  box-shadow:inset -3px 0 5px rgba(0,0,0,.45), inset 2px 0 3px rgba(255,255,255,.12);
  text-shadow:0 0 2px rgba(0,0,0,.6);
  text-decoration:none !important;
  transition:transform .18s ease;
}
.book:hover{transform:translateY(-8px);z-index:2}
.book .band{position:absolute;top:0;left:0;right:0;height:11px;background:rgba(243,233,210,.85)}
.book .gline{position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,#8a6d1f,#e8c95a,#8a6d1f)}
.book .gline.t{top:8px}
.book .gline.b{bottom:10px}
.book.hit{outline:3px solid #ffe9a0;outline-offset:2px}
.book .title{max-height:104px;overflow:hidden}
.detail-card{
  background:linear-gradient(#fbf4e2,#efe3c5);color:#1c1714;
  border:1px solid #c9b88a;border-radius:10px;padding:16px 18px;margin-top:1rem;
  font-family:serif;
}
.detail-card h3{margin:.2rem 0 .4rem;letter-spacing:.15em;color:#4a3417}
.detail-type{display:inline-block;font-size:.68rem;letter-spacing:.2em;
  padding:3px 10px;border-radius:99px;color:#fffdf6}
.detail-meta{font-size:.8rem;color:#6b5430;margin:.3rem 0}
.preview-book{
  position:relative;display:inline-flex;justify-content:center;
  width:34px;height:90px;border-radius:3px 3px 0 0;overflow:hidden;
  writing-mode:vertical-rl;font-size:.55rem;color:rgba(255,250,235,.95);
  padding-top:12px;box-shadow:inset -3px 0 4px rgba(0,0,0,.4);
  text-shadow:0 0 2px rgba(0,0,0,.6);font-family:serif;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 部品
# ============================================================
def esc(s):
    return html.escape(str(s))


def book_width(size):
    return int(22 + size * 2.2)


def book_height(seed):
    h = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16)
    return 118 + (h % 28)


def deco_html(deco):
    if deco == "label":
        return '<span class="band"></span>'
    if deco == "gold":
        return '<span class="gline t"></span><span class="gline b"></span>'
    return ""


def spine_bg(color):
    return f"linear-gradient(180deg, {color} 0%, rgba(0,0,0,.35) 140%), {color}"


def spine_html(b, hit=False):
    w = book_width(b["size"])
    h = book_height(b["title"] + str(b["id"]))
    cls = "book hit" if hit else "book"
    return (
        f'<a class="{cls}" href="?book={esc(b["id"])}" target="_self" '
        f'style="width:{w}px;height:{h}px;background:{spine_bg(b["color"])}">'
        f'{deco_html(b.get("deco", "label"))}'
        f'<span class="title">{esc(b["title"])}</span></a>'
    )


def bookcase_html(wall_idx, hit_id=None):
    wall_books = [b for b in books if b.get("wall", 0) == wall_idx]
    rows = [{"w": 0, "items": []} for _ in range(SHELVES_PER_CASE)]
    overflow = 0
    for b in wall_books:
        w = book_width(b["size"])
        placed = False
        for r in rows:
            if r["w"] + w <= SHELF_MAX_PX:
                r["w"] += w + 2
                r["items"].append(b)
                placed = True
                break
        if not placed:
            overflow += 1
    parts = ['<div class="bookcase">']
    for r in rows:
        parts.append('<div class="shelf">')
        if not r["items"]:
            parts.append('<div class="shelf-empty">— 空きの棚 —</div>')
        for b in r["items"]:
            parts.append(spine_html(b, hit=(b["id"] == hit_id)))
        parts.append("</div>")
    parts.append("</div>")
    return "".join(parts), overflow


def new_id():
    import time, random
    return f"{int(time.time()*1000)}{random.randint(0, 999)}"


def add_book(title, btype, url, size, color, deco, wall_idx):
    if used_gb + size > data["total_gb"]:
        return False, "書庫の容量が足りません。何か処分しましょう"
    books.append({
        "id": new_id(), "title": title, "type": btype, "url": url,
        "size": size, "wall": wall_idx, "color": color, "deco": deco,
    })
    save_data(data)
    return True, "棚に並べました"


# ============================================================
# ヘッダー(題字と容量ゲージ)
# ============================================================
st.markdown('<div class="lib-header">わたしの蔵書館</div>'
            '<div class="lib-sub">VIRTUAL LIBRARY</div>', unsafe_allow_html=True)

pct = min(100, used_gb / max(1, data["total_gb"]) * 100)
st.markdown(
    f'<div class="gauge-label"><span>書庫の容量</span>'
    f'<span>{used_gb} GB / {data["total_gb"]} GB</span></div>'
    f'<div class="gauge-bar"><div class="gauge-fill" style="width:{pct}%"></div></div>',
    unsafe_allow_html=True,
)

# ============================================================
# 検索と、選ばれている本(URLの ?book= から)
# ============================================================
selected_book = None
book_param = st.query_params.get("book")
if book_param:
    selected_book = next((b for b in books if str(b["id"]) == str(book_param)), None)

search_q = st.text_input("蔵書をさがす", placeholder="題名の一部を入力…", label_visibility="collapsed")
hit_book = None
if search_q.strip():
    hit_book = next((b for b in books if search_q.strip() in b["title"]), None)
    if hit_book is None:
        st.caption("見つかりませんでした")

# ============================================================
# 本棚の選択(◀ ▶ と一覧)
# ============================================================
n_walls = len(walls)
if "wall_idx" not in st.session_state:
    st.session_state.wall_idx = 0
# 検索で見つかった本・選択中の本がある棚へ自動で移動
if hit_book is not None:
    st.session_state.wall_idx = hit_book.get("wall", 0)
elif selected_book is not None:
    st.session_state.wall_idx = selected_book.get("wall", 0)
st.session_state.wall_idx = min(st.session_state.wall_idx, n_walls - 1)

c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("◀", use_container_width=True):
        st.session_state.wall_idx = (st.session_state.wall_idx - 1) % n_walls
with c3:
    if st.button("▶", use_container_width=True):
        st.session_state.wall_idx = (st.session_state.wall_idx + 1) % n_walls
with c2:
    st.session_state.wall_idx = st.selectbox(
        "本棚", range(n_walls),
        index=st.session_state.wall_idx,
        format_func=lambda i: walls[i]["name"],
        label_visibility="collapsed",
    )
wall_idx = st.session_state.wall_idx

# ============================================================
# 本棚の表示
# ============================================================
case_html, overflow = bookcase_html(wall_idx, hit_id=(hit_book or {}).get("id"))
st.markdown(case_html, unsafe_allow_html=True)
if overflow:
    st.warning(f"この本棚は満杯です({overflow}冊が置けません)。別の本棚へどうぞ")

# ============================================================
# 本の詳細(背表紙をクリックすると表示)
# ============================================================
if selected_book:
    b = selected_book
    t = TYPE_INFO.get(b["type"], TYPE_INFO["memo"])
    st.markdown(
        f'<div class="detail-card">'
        f'<span class="detail-type" style="background:{b["color"]}">{t["label"]}</span>'
        f'<h3>{esc(b["title"])}</h3>'
        f'<div class="detail-meta">厚み:{b["size"]} GB / '
        f'置き場所:{esc(walls[b.get("wall", 0)]["name"])}</div>'
        f'<div class="detail-meta">{esc(b["url"]) if b.get("url") else "(URLなし)"}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    d1, d2, d3 = st.columns(3)
    with d1:
        if b.get("url"):
            st.link_button("開く", b["url"], use_container_width=True)
    with d2:
        if st.button("処分する", use_container_width=True):
            data["books"] = [x for x in books if x["id"] != b["id"]]
            save_data(data)
            st.query_params.clear()
            st.rerun()
    with d3:
        if st.button("閉じる", use_container_width=True):
            st.query_params.clear()
            st.rerun()

# ============================================================
# サイドバー:本を増やす
# ============================================================
with st.sidebar:
    st.header("📖 本を増やす")
    with st.form("add_book", clear_on_submit=True):
        f_title = st.text_input("タイトル", max_chars=40, placeholder="例:お気に入りの料理動画")
        f_type = st.selectbox("種類", list(TYPE_INFO.keys()),
                              format_func=lambda k: TYPE_INFO[k]["label"])
        f_url = st.text_input("URL(サイト・動画の場合)", placeholder="https://…")
        f_color_name = st.radio("背表紙の色", [c[0] for c in COLORS], horizontal=True)
        f_deco_key = st.radio("背表紙の飾り", [d[0] for d in DECOS], horizontal=True,
                              format_func=lambda k: dict(DECOS)[k])
        f_size = st.slider("本の厚み = 容量(GB)", 1, 40, 5)
        f_wall = st.selectbox("置く本棚", range(n_walls),
                              index=wall_idx, format_func=lambda i: walls[i]["name"])
        f_color = dict(COLORS)[f_color_name]
        st.markdown(
            f'<div style="font-size:.75rem;color:#c9a227;letter-spacing:.1em">仕上がり:</div>'
            f'<div class="preview-book" style="background:{spine_bg(f_color)}">'
            f'{deco_html(f_deco_key)}<span>{esc(f_title or "題名")}</span></div>',
            unsafe_allow_html=True,
        )
        if st.form_submit_button("棚に置く", use_container_width=True, type="primary"):
            if not f_title.strip():
                st.error("タイトルを入れてください")
            else:
                ok, msg = add_book(f_title.strip(), f_type, f_url.strip(),
                                   f_size, f_color, f_deco_key, f_wall)
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

    st.divider()
    st.header("🗄 本棚の管理")
    with st.form("rename_wall"):
        new_name = st.text_input("この本棚の名前を変える", value=walls[wall_idx]["name"], max_chars=14)
        if st.form_submit_button("名前を変える", use_container_width=True):
            if new_name.strip():
                walls[wall_idx]["name"] = new_name.strip()
                save_data(data)
                st.rerun()
    with st.form("add_wall", clear_on_submit=True):
        wall_name = st.text_input("新しい本棚をつくる", placeholder=f"本棚 {n_walls + 1}", max_chars=14)
        if st.form_submit_button("＋ 本棚を追加", use_container_width=True):
            walls.append({"name": wall_name.strip() or f"本棚 {n_walls + 1}"})
            save_data(data)
            st.session_state.wall_idx = len(walls) - 1
            st.rerun()

    st.divider()
    st.header("⚙ 設定")
    with st.form("settings"):
        total = st.number_input("書庫の総容量(GB)", min_value=10, max_value=100000,
                                value=int(data["total_gb"]), step=10,
                                help="お使いのパソコンの容量に合わせて設定してください")
        if st.form_submit_button("保存", use_container_width=True):
            data["total_gb"] = int(total)
            save_data(data)
            st.rerun()

    if st.button("見本を並べる", use_container_width=True):
        for s in SAMPLES:
            loads = [sum(b["size"] for b in books if b.get("wall", 0) == i) for i in range(n_walls)]
            target = loads.index(min(loads))
            add_book(s["title"], s["type"], s.get("url", ""), s["size"],
                     TYPE_INFO[s["type"]]["color"], "label", target)
        st.rerun()

    st.divider()
    st.header("💾 バックアップ")
    st.caption("Streamlit Cloudは再起動でデータが消えることがあります。ときどき保存しておきましょう。")
    st.download_button(
        "蔵書データをダウンロード",
        data=json.dumps(data, ensure_ascii=False, indent=1),
        file_name="library-backup.json",
        mime="application/json",
        use_container_width=True,
    )
    up = st.file_uploader("バックアップから復元", type=["json"])
    if up is not None and st.button("この内容で復元する", use_container_width=True):
        try:
            d = json.loads(up.read().decode("utf-8"))
            assert "books" in d and "walls" in d
            save_data(d)
            st.success("復元しました")
            st.rerun()
        except Exception:
            st.error("ファイルの形式が違うようです")
