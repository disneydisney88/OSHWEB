# -*- coding: utf-8 -*-
"""
香港職業安全資訊網 — Streamlit 應用
====================================
部署:GitHub repo 上以 Streamlit Community Cloud 直接部署,Main file = streamlit_app.py
功能:三語(繁/簡/英)、自動更新(RSS/XLSX,每小時快取+手動立即更新)、
      YouTube職安影片專區、網主後台(公告/影片/連結/密碼)、會員專區(預留)、
      Google Drive 檔案庫、資訊來源說明。
"""
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import content as C  # noqa: E402
import update_data as updater  # noqa: E402

DATA = ROOT / "data"
SETTINGS_FILE = DATA / "settings.json"
MEMBERS_FILE = DATA / "members.json"
DEFAULT_ADMIN_PW = "oshweb-admin"

DEFAULT_SETTINGS = {
    "announcements": [],      # [{ "text": str, "active": bool }]
    "custom_links": [],       # [{ "name": str, "url": str }]
    "owner_video": "",        # 網主影片 YouTube URL
    "extra_videos": [],       # [{ "title": str, "url": str }]
    "admin_password_sha256": "",
}

st.set_page_config(
    page_title="香港職業安全資訊網 | HK OSH Info Portal",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- 基本狀態
if "lang" not in st.session_state:
    st.session_state.lang = "tc"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "member" not in st.session_state:
    st.session_state.member = None

LANG = st.session_state.lang


def t(key):
    return C.L(C.UI[key], LANG)


# ---------------------------------------------------------------- 設定/會員存取
def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, obj):
    DATA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def get_settings():
    s = dict(DEFAULT_SETTINGS)
    s.update(load_json(SETTINGS_FILE, {}))
    return s


def save_settings(s):
    save_json(SETTINGS_FILE, s)


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def check_admin_pw(pw):
    s = get_settings()
    if s["admin_password_sha256"]:
        return sha256(pw) == s["admin_password_sha256"]
    try:
        secret = st.secrets.get("ADMIN_PASSWORD", None)
    except Exception:
        secret = None
    expected = secret or os.environ.get("ADMIN_PASSWORD") or DEFAULT_ADMIN_PW
    return pw == expected


def using_default_pw():
    s = get_settings()
    if s["admin_password_sha256"]:
        return False
    try:
        if st.secrets.get("ADMIN_PASSWORD"):
            return False
    except Exception:
        pass
    return not os.environ.get("ADMIN_PASSWORD")


# ---------------------------------------------------------------- 資料抓取(自動更新)
@st.cache_data(ttl=1800, show_spinner="🔄 開站自動更新:正在向官方來源抓取最新資料…(首次約30-60秒)")
def _live_data():
    fetched_ts = updater.now_hkt()
    try:
        items, src_status = updater.collect_news(fetched_ts)
    except Exception:
        items, src_status = [], []
    try:
        rso = updater.collect_rso(fetched_ts)
    except Exception:
        rso = None
    return {"items": items, "sources": src_status, "rso": rso,
            "generated_at": fetched_ts, "live": bool(items)}


@st.cache_data(ttl=1800, show_spinner=False)
def _legal_watch(ts, baseline):
    return updater.watch_legals(ts, baseline)


def load_file_fallback():
    news = load_json(DATA / "news.json", {})
    rso = load_json(DATA / "rso_stats.json", None)
    return {"items": news.get("items", []), "sources": news.get("sources", []),
            "rso": rso, "generated_at": news.get("generated_at", "—"), "live": False}


def get_data():
    live = _live_data()
    if live["live"] and len(live["items"]) >= 5:
        return live
    fb = load_file_fallback()
    merged = {i["id"]: i for i in live["items"]}
    for i in fb["items"]:
        merged.setdefault(i["id"], i)
    out = dict(live)
    out["items"] = list(merged.values())
    if not out["items"]:
        out.update(fb)
    out["partial_fallback"] = not live["live"]
    return out


def get_legal_watch():
    baseline = load_json(DATA / "legal_watch.json", {})
    d = get_data()
    return _legal_watch(d["generated_at"], baseline)


def news_items(d):
    return [i for i in d["items"] if i.get("kind", "news") == "news"]


# ---------------------------------------------------------------- 渲染工具
def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


def render_panel(panel):
    st.subheader(C.L(panel["h"], LANG))
    for block in panel.get("blocks", []):
        kind = block[0]
        if kind == "p":
            st.markdown(C.L(block[1], LANG))
        elif kind == "table":
            headers = C.L(block[1], LANG)
            rows = C.L(block[2], LANG)
            st.markdown(md_table(headers, rows))
        elif kind == "ul":
            st.markdown("\n".join("- " + x for x in C.L(block[1], LANG)))
        elif kind == "ol":
            st.markdown("\n".join(f"{n}. {x}" for n, x in enumerate(C.L(block[1], LANG), 1)))
        elif kind == "src":
            st.markdown(f"<small>🔗 {C.L(block[1], LANG)}</small>", unsafe_allow_html=True)


def render_section(sec_id):
    sec = C.SECTIONS[sec_id]
    st.markdown(C.L(sec["intro"], LANG))
    st.divider()
    if sec_id == "msds":
        ghs = C.L(sec["ghs"], LANG)
        st.markdown("**GHS** ｜ " + " ｜ ".join(ghs))
        st.divider()
    for panel in sec.get("panels", []):
        render_panel(panel)


def news_html(it):
    date = (it.get("date") or it.get("fetched") or "")[:10]
    src = C.L(C.UI["src_line"], LANG)
    return (f"- **{date}** ｜ [{it['title']}]({it['url']})  \n"
            f"  <small>{src}:{it['source_label']}</small>")


def news_block(items, empty_key="none_yet"):
    if not items:
        st.info(t(empty_key))
        return
    st.markdown("\n".join(news_html(i) for i in items), unsafe_allow_html=True)


# ---------------------------------------------------------------- 頁面:主頁
def pg_home():
    d = get_data()
    if d.get("partial_fallback"):
        st.warning(t("fallback_note"))

    # 法例變更監察警示
    changed = [w for w in get_legal_watch() if w.get("changed")]
    if changed:
        lines = " ｜ ".join(f"[{w['label']}]({w['url']})" for w in changed)
        st.error(t("legal_alert") + " " + lines, icon="⚖️")

    # 網主公告
    for a in get_settings()["announcements"]:
        if a.get("active", True):
            st.success("📢 " + a["text"])

    sec = C.SECTIONS
    st.markdown("## " + C.L(C.T(
        "一站式香港職業安全資訊平台", "One-stop HK OSH information portal"), LANG))
    st.markdown(C.L(C.T(
        "整合**勞工處職安**官方資訊、法例與工作守則、PPE、化學品MSDS、AI／4S安全智慧科技、"
        "香港・內地・海外職安新聞、工傷新聞、防火安全、註冊安全主任資訊及統計。"
        "所有新聞及統計**自動更新**並逐項**列明資訊來源**。",
        "Aggregates official **LD OSH** information, legislation & COPs, PPE, MSDS, AI/4S smart-safety tech, "
        "HK/China/international OSH news, injury news, fire safety, and Registered Safety Officer info & statistics. "
        "Everything is **auto-updated** with **sources cited** item by item."), LANG))
    st.markdown(f"`{t('auto_note')}`")

    # 天氣警示(職安相關:中暑/惡劣天氣)
    wx = [i for i in d["items"] if i.get("kind") == "weather"]
    if wx:
        with st.expander(t("weather_now"), icon="🌤️"):
            for w in wx[:3]:
                st.markdown(f"**{w['title']}** ｜ <small>{w['source_label']} · {w['url']}</small>",
                            unsafe_allow_html=True)
            st.caption(t("weather_tip"))

    # 最新動態
    st.subheader(t("latest"))
    news_block(news_items(d)[:8])

    c1, c2, c3 = st.columns([1, 1, 1.2], gap="medium")
    with c1:
        st.subheader(t("rso_stat"))
        rso = d.get("rso")
        if rso and rso.get("rows"):
            rows = rso["rows"]
            headers = rows[0]
            col = rso_value_col(headers)
            latest = rows[-1]
            val = latest[col] if col is not None and col < len(latest) else "—"
            label = latest[0]
            st.metric(label=str(label), value=f"{val}")
            st.caption(f"{C.L(C.UI['src_line'], LANG)}:{rso['source_label']} ({rso['retrieved'][:10]})")
        else:
            st.info(t("none_yet"))
    with c2:
        st.subheader(t("accidents_now"))
        acc = [i for i in news_items(d) if i.get("category") == "accident"][:5]
        if acc:
            st.markdown("\n".join(f"- [{i['title']}]({i['url']})  \n  <small>{i['source_label']}</small>"
                                  for i in acc), unsafe_allow_html=True)
        else:
            st.info(t("none_yet"))
    with c3:
        st.subheader(t("quick_links"))
        links = [
            ("勞工處:職安法例一覽", "https://www.labour.gov.hk/tc/legislat/contentB3.htm"),
            ("勞工處:工作守則清單", "https://www.labour.gov.hk/tc/public/content2_8b.htm"),
            ("勞工處:安全主任註冊", "https://www.labour.gov.hk/tc/faq/oshq8_whole.html"),
            ("職業安全健康局 OSHC", "https://www.oshc.org.hk"),
            ("電子版香港法例", "https://www.elegislation.gov.hk"),
        ] + [(x["name"], x["url"]) for x in get_settings()["custom_links"]]
        for name, url in links:
            st.markdown(f"- [{name}]({url})")

    st.link_button(t("drive_btn"), C.DRIVE_URL, use_container_width=True)


def rso_value_col(headers):
    """找出「安全主任人數」欄;否則用最後一欄。"""
    for idx, h in enumerate(headers):
        if "安全主任" in str(h) and "人數" in str(h):
            return idx
    return len(headers) - 1


# ---------------------------------------------------------------- 頁面:內容分區
def pg_law():
    st.markdown("## " + C.L(C.SECTIONS["law"]["title"], LANG))
    render_section("law")


def pg_cop():
    st.markdown("## " + C.L(C.SECTIONS["cop"]["title"], LANG))
    render_section("cop")


def pg_ppe():
    st.markdown("## " + C.L(C.SECTIONS["ppe"]["title"], LANG))
    render_section("ppe")


def pg_msds():
    st.markdown("## " + C.L(C.SECTIONS["msds"]["title"], LANG))
    render_section("msds")


def pg_tech():
    st.markdown("## " + C.L(C.SECTIONS["tech"]["title"], LANG))
    render_section("tech")


def pg_fire():
    st.markdown("## " + C.L(C.SECTIONS["fire"]["title"], LANG))
    render_section("fire")


# ---------------------------------------------------------------- 頁面:新聞
def _region_selector():
    labels = [t("news_hk"), t("news_cn"), t("news_intl"), t("all")]
    vals = ["HK", "CN", "INTL", "ALL"]
    pick = st.segmented_control("region", labels, selection_mode="single",
                                default=labels[0], label_visibility="collapsed")
    return vals[labels.index(pick)] if pick else "HK"


def pg_news():
    st.markdown("## " + C.L(C.SECTIONS["news"]["title"], LANG))
    st.markdown(C.L(C.SECTIONS["news"]["intro"], LANG))
    d = get_data()
    region = _region_selector()
    items = [i for i in news_items(d) if region == "ALL" or i["region"] == region]
    st.caption(f"{len(items)} " + ("條" if LANG != "en" else "items") +
               f" ｜ {t('updated_at')}: {d['generated_at']}")
    news_block(items[:60])


def pg_accident():
    st.markdown("## " + C.L(C.SECTIONS["accident"]["title"], LANG))
    st.info(t("accident_note"))
    d = get_data()
    acc = [i for i in news_items(d) if i.get("category") == "accident"]
    st.caption(f"{len(acc)} " + ("條" if LANG != "en" else "items"))

    # 月度 PDF 報告
    try:
        import monthly_report
        today = updater.datetime.now(updater.HKT).date()
        y, m = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        with st.expander(t("report_btn"), icon="📄"):
            with st.spinner(t("ai_thinking")):
                pdf = monthly_report.build_pdf(y, m, monthly_report.collect(y, m, d["items"]))
            st.download_button(t("report_btn"), pdf,
                               file_name=f"injury-report-{y}-{m:02d}.pdf",
                               mime="application/pdf")
            st.caption(C.L(C.T(
                "報告來源:政府新聞公報/政府新聞網/香港電台(關鍵字自動分類,非官方統計);"
                "每月1日亦會由 GitHub Actions 自動生成並存入 repo 的 reports/。",
                "Sources: official news, keyword-classified (not official statistics); "
                "regenerated automatically on the 1st monthly by GitHub Actions into reports/."),
                LANG))
    except ImportError:
        st.caption("📄 reportlab 未安裝,PDF 報告功能停用(pip install reportlab)。")

    news_block(acc[:80])


# ---------------------------------------------------------------- 頁面:安全主任
def pg_so():
    st.markdown("## " + C.L(C.SECTIONS["so"]["title"], LANG))
    render_section("so")
    st.divider()
    d = get_data()
    rso = d.get("rso")
    st.subheader("📊 " + C.L(C.T("註冊安全主任數目(自動更新)", "RSO numbers (auto-updated)"), LANG))
    if rso and rso.get("rows"):
        rows = rso["rows"]
        st.dataframe(pd.DataFrame(rows[1:], columns=rows[0]), width="stretch",
                     hide_index=True)
        col = rso_value_col(rows[0])
        labels = [r[0] for r in rows[1:]]
        vals = pd.to_numeric(pd.Series([r[col] if col < len(r) else None for r in rows[1:]]
                                       ).astype(str).str.replace(",", ""), errors="coerce")
        chart = pd.DataFrame({"value": vals.values}, index=labels)
        st.bar_chart(chart, height=280, x_label=rows[0][0], y_label=str(rows[0][col]))
        st.caption(f"{rso['note']} ｜ {C.L(C.UI['src_line'], LANG)}:"
                   f"[DATA.GOV.HK]({rso['dataset_page']})({rso['retrieved'][:10]}抓取)")
    else:
        st.info(t("none_yet"))


# ---------------------------------------------------------------- 頁面:YouTube
def yt_id(url):
    import re
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def pg_yt():
    st.markdown("## " + C.L(C.SECTIONS["yt"]["title"], LANG))
    st.markdown(C.L(C.SECTIONS["yt"]["intro"], LANG))

    s = get_settings()
    if s["owner_video"]:
        st.markdown("### 🎬 " + C.L(C.T("網主精選影片", "Owner's featured video"), LANG))
        try:
            st.video(s["owner_video"])
        except Exception:
            st.markdown(f"[{s['owner_video']}]({s['owner_video']})")
    for v in s["extra_videos"]:
        try:
            st.video(v["url"])
            st.caption(v.get("title", ""))
        except Exception:
            st.markdown(f"- [{v.get('title') or v['url']}]({v['url']})")

    st.markdown("### 🔄 " + C.L(C.T("最新《職安警示》影片(自動同步)", "Latest Safety Alert videos (auto-synced)"), LANG))
    d = get_data()
    vids = [i for i in d["items"] if i.get("kind") == "video"]
    if vids:
        for v in vids[:2]:
            try:
                st.video(v["url"])
            except Exception:
                st.markdown(f"- [{v['title']}]({v['url']})")
            st.caption(f"{v['title']} ｜ {v['source_label']}")
        if len(vids) > 2:
            st.markdown("#### " + C.L(C.T("更多影片", "More videos"), LANG))
            st.markdown("\n".join(f"- [{v['title']}]({v['url']})" for v in vids[2:]))
    else:
        st.info(t("none_yet"))

    st.markdown("### 📺 " + C.L(C.T("官方職安頻道", "Official OSH channels"), LANG))
    for name, url, desc in C.YT_CHANNELS:
        st.markdown(f"**[{name}]({url})** ｜ {C.L(desc, LANG)}")
    st.markdown(f"<small>🔗 {C.L(C.SECTIONS['yt']['src'], LANG)}</small>", unsafe_allow_html=True)


# ---------------------------------------------------------------- 頁面:AI 職安助手
def _llm_config():
    try:
        api_key = st.secrets.get("LLM_API_KEY", None)
    except Exception:
        api_key = None
    api_key = api_key or os.environ.get("LLM_API_KEY")
    try:
        base = st.secrets.get("LLM_BASE_URL", None) or os.environ.get("LLM_BASE_URL") \
            or "https://open.bigmodel.cn/api/paas/v4"
    except Exception:
        base = os.environ.get("LLM_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4"
    try:
        model = st.secrets.get("LLM_MODEL", None) or os.environ.get("LLM_MODEL") or "glm-4-flash"
    except Exception:
        model = os.environ.get("LLM_MODEL") or "glm-4-flash"
    return api_key, base, model


@st.cache_data(show_spinner=False)
def build_corpus():
    """把本站內容拆成知識塊,供檢索。"""
    chunks = []
    for sid, sec in C.SECTIONS.items():
        title = C.L(sec["title"], "tc")
        texts = [C.L(sec.get("intro") or C.T("", ""), "tc")] if sec.get("intro") else []
        for panel in sec.get("panels", []):
            parts = [C.L(panel["h"], "tc")]
            for b in panel.get("blocks", []):
                kind = b[0]
                if kind == "p":
                    parts.append(C.L(b[1], "tc"))
                elif kind == "table":
                    parts.extend(" / ".join(map(str, r)) for r in C.L(b[2], "tc"))
                elif kind in ("ul", "ol"):
                    parts.extend(C.L(b[1], "tc"))
                elif kind == "src":
                    parts.append("來源:" + C.L(b[1], "tc"))
            texts.append("\n".join(parts))
        chunks.append({"id": sid, "title": title,
                       "text": title + "\n" + "\n".join(t for t in texts if t)})
    return chunks


def _tokens(q):
    import re
    q = q.strip()
    toks = set(re.findall(r"[A-Za-z]{2,}", q.upper()))
    cn = re.findall(r"[\u4e00-\u9fff]", q)
    toks |= {a + b for a, b in zip(cn, cn[1:])} if len(cn) > 1 else set(cn)
    return toks


def retrieve(question, k=4):
    toks = _tokens(question)
    scored = []
    for ch in build_corpus():
        score = sum(1 for tk in toks if tk in ch["text"])
        if score:
            scored.append((score, ch))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]


def ask_llm(question, context):
    api_key, base, model = _llm_config()
    body = json.dumps({
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content":
                "你是香港職業安全資訊網的AI職安助手。只用「參考資料」及通用職安常識回答,"
                "回答須简明、列出參考的本站章節;法律事宜提醒以勞工處/官方最新公佈為準。"
                "用戶語言:繁體中文優先,若用戶用英文則以英文回答。"},
            {"role": "user", "content":
                f"參考資料:\n{context}\n\n問題:{question}"},
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def pg_ai():
    st.markdown("## " + t("nav_ai"))
    st.markdown(t("ai_intro"))
    api_key, base, model = _llm_config()
    if not api_key:
        st.warning(t("ai_no_key"))
        return
    st.caption(f"模型:`{model}`")

    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []
    for m in st.session_state.ai_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input(C.L(C.T("例如:安全主任註冊要求是什麼?密閉空間工作要注意什麼?",
                              "e.g. What are the RSO registration requirements?"), LANG))
    if q:
        st.session_state.ai_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        refs = retrieve(q)
        ctx = "\n\n---\n\n".join(f"【{r['title']}】\n{r['text']}" for r in refs) \
            or "(無特定章節,以通用職安常識回答)"
        with st.chat_message("assistant"):
            with st.spinner(t("ai_thinking")):
                try:
                    answer = ask_llm(q, ctx)
                except Exception as e:
                    answer = f"⚠️ {type(e).__name__}: {e}"
            st.markdown(answer)
            if refs:
                st.caption(t("ai_sources") + ":" + "、".join(r["title"] for r in refs))
        st.session_state.ai_history.append({"role": "assistant", "content": answer})


# ---------------------------------------------------------------- 頁面:會員
def pg_member():
    sec = C.SECTIONS["member"]
    st.markdown("## " + C.L(sec["title"], LANG))
    st.markdown(C.L(sec["intro"], LANG))
    members = load_json(MEMBERS_FILE, {})

    if st.session_state.get("member"):
        m = st.session_state.member
        st.success(f"👋 {C.L(C.T('歡迎','Welcome'), LANG)},{m['name']}({m['email']})")
        st.link_button(t("drive_btn"), C.DRIVE_URL)
        st.markdown("### " + C.L(C.T("預留功能(開發中)", "Reserved features (coming)"), LANG))
        st.markdown(C.L(C.T("- 🔖 我的收藏\n- 📝 課程報名\n- 📅 證書到期提醒",
                            "- 🔖 My bookmarks\n- 📝 Course enrolment\n- 📅 Certificate expiry reminders"), LANG))
        if st.button(C.L(C.T("登出", "Log out"), LANG)):
            st.session_state.member = None
            st.rerun()
        return

    tab_login, tab_reg = st.tabs([C.L(C.T("登入", "Log in"), LANG),
                                  C.L(C.T("註冊", "Register"), LANG)])
    with tab_login:
        with st.form("login_form"):
            email = st.text_input(C.L(C.T("電郵", "Email"), LANG), key="li_email")
            pw = st.text_input(C.L(C.T("密碼", "Password"), LANG), type="password", key="li_pw")
            if st.form_submit_button(C.L(C.T("登入", "Log in"), LANG), type="primary"):
                rec = members.get(email.strip().lower())
                if rec and rec["pw"] == sha256(pw):
                    st.session_state.member = {"name": rec["name"], "email": email.strip().lower()}
                    st.rerun()
                else:
                    st.error(C.L(C.T("電郵或密碼不正確", "Invalid email or password"), LANG))
    with tab_reg:
        with st.form("reg_form"):
            name = st.text_input(C.L(C.T("稱呼", "Name"), LANG), key="rg_name")
            email = st.text_input(C.L(C.T("電郵", "Email"), LANG), key="rg_email")
            pw = st.text_input(C.L(C.T("密碼(示範用,請勿用真實密碼)", "Password (demo — not a real one!)"),
                                  LANG), type="password", key="rg_pw")
            if st.form_submit_button(C.L(C.T("註冊", "Register"), LANG)):
                e = email.strip().lower()
                if not name or not e or not pw:
                    st.warning(C.L(C.T("請填妥所有欄位", "Please fill in all fields"), LANG))
                elif e in members:
                    st.warning(C.L(C.T("此電郵已註冊", "Email already registered"), LANG))
                else:
                    members[e] = {"name": name.strip(), "pw": sha256(pw),
                                  "joined": updater.now_hkt()}
                    save_json(MEMBERS_FILE, members)
                    st.session_state.member = {"name": name.strip(), "email": e}
                    st.rerun()


# ---------------------------------------------------------------- 頁面:檔案庫
def pg_files():
    sec = C.SECTIONS["files"]
    st.markdown("## " + C.L(sec["title"], LANG))
    st.markdown(C.L(sec["intro"], LANG))
    st.link_button(t("drive_btn"), C.DRIVE_URL, use_container_width=True)
    st.caption(C.L(sec["src"], LANG))


# ---------------------------------------------------------------- 頁面:資訊來源
def pg_sources():
    st.markdown("## " + C.L(C.SECTIONS["sources"]["title"], LANG))
    render_section("sources")
    st.divider()
    st.subheader("📡 " + C.L(C.T("自動更新即時狀態", "Live auto-update status"), LANG))
    d = get_data()
    rows = [{"source": s["label"], "method": s["method"], "count": s["count"],
             "status": s["status"], "fetched": s["fetched"], "url": s["url"]}
            for s in d["sources"]]
    if d.get("rso"):
        rows.append({"source": d["rso"]["source_label"], "method": "XLSX",
                     "count": len(d["rso"]["rows"]), "status": "ok",
                     "fetched": d["rso"]["retrieved"], "url": d["rso"]["source_url"]})
    df = pd.DataFrame(rows)
    df["link"] = df["url"].apply(lambda u: f"[來源]({u})")
    st.markdown(md_table(["來源" if LANG != "en" else "Source", "方式" if LANG != "en" else "Method",
                          "新增" if LANG != "en" else "New", "狀態" if LANG != "en" else "Status",
                          "抓取時間" if LANG != "en" else "Fetched", "連結" if LANG != "en" else "Link"],
                         df[["source", "method", "count", "status", "fetched", "link"]]
                         .values.tolist()))
    st.caption(f"{t('updated_at')}: {d['generated_at']}")


# ---------------------------------------------------------------- 頁面:網主設定
def pg_admin():
    st.markdown("## " + t("nav_admin"))
    s = get_settings()

    st.markdown("### " + t("legal_watch_admin"))
    watch = get_legal_watch()
    baseline = load_json(DATA / "legal_watch.json", {})
    for w in watch:
        if w.get("error"):
            st.caption(f"⚠️ {w['label']}:抓取失敗({w['error']})")
        else:
            icon = "🔴" if w.get("changed") else "🟢"
            st.markdown(f"{icon} **{w['label']}** ｜ {C.L(C.UI['src_line'], LANG)}: <{w['url']}>"
                        f" ｜ {C.L(C.UI['updated_at'], LANG)}:{w['last_checked']}",
                        unsafe_allow_html=True)
    if any(w.get("changed") for w in watch):
        if st.button(t("legal_ack"), type="primary"):
            now = updater.now_hkt()
            for w in watch:
                baseline[w["url"]] = {"hash": w["hash"], "acked_at": now,
                                      "first_seen": w.get("first_seen", now)}
            save_json(DATA / "legal_watch.json", baseline)
            _legal_watch.clear()
            st.rerun()
    else:
        st.caption(t("legal_none"))
    st.divider()

    st.markdown("### 📢 " + C.L(C.T("公告管理(主頁頂部顯示)", "Announcements (shown on home)"), LANG))
    for i, a in enumerate(s["announcements"]):
        cc1, cc2, cc3 = st.columns([6, 1, 1])
        cc1.markdown(f"{'🟢' if a.get('active') else '⚪'} {a['text']}")
        if cc2.button("停/啟" if LANG != "en" else "on/off", key=f"tg{i}"):
            s["announcements"][i]["active"] = not a.get("active", True)
            save_settings(s)
            st.rerun()
        if cc3.button("✕", key=f"del{i}"):
            s["announcements"].pop(i)
            save_settings(s)
            st.rerun()
    with st.form("ann_form", border=True):
        txt = st.text_input(C.L(C.T("新公告內容", "New announcement"), LANG))
        if st.form_submit_button(C.L(C.T("加入公告", "Add"), LANG)) and txt.strip():
            s["announcements"].append({"text": txt.strip(), "active": True})
            save_settings(s)
            st.rerun()

    st.markdown("### 🎬 " + C.L(C.T("YouTube 影片管理", "YouTube video manager"), LANG))
    ow = st.text_input(C.L(C.T("網主精選影片網址(主頁/影片頁頂部)", "Owner's featured video URL"), LANG),
                       value=s["owner_video"], key="ow_vid")
    cc1, cc2 = st.columns([1, 3])
    if cc1.button(C.L(C.T("儲存", "Save"), LANG), key="save_ov"):
        s["owner_video"] = ow.strip()
        save_settings(s)
        st.rerun()
    for i, v in enumerate(s["extra_videos"]):
        vv1, vv2 = st.columns([6, 1])
        vv1.markdown(f"▶️ [{v.get('title') or v['url']}]({v['url']})")
        if vv2.button("✕", key=f"dv{i}"):
            s["extra_videos"].pop(i)
            save_settings(s)
            st.rerun()
    with st.form("vid_form", border=True):
        vt = st.text_input(C.L(C.T("影片標題", "Video title"), LANG), key="nv_t")
        vu = st.text_input(C.L(C.T("影片網址(YouTube)", "Video URL (YouTube)"), LANG), key="nv_u")
        if st.form_submit_button(C.L(C.T("加入影片", "Add video"), LANG)) and vu.strip():
            s["extra_videos"].append({"title": vt.strip(), "url": vu.strip()})
            save_settings(s)
            st.rerun()

    st.markdown("### 🔗 " + C.L(C.T("自訂快速連結(主頁顯示)", "Custom quick links (home)"), LANG))
    for i, lk in enumerate(s["custom_links"]):
        ll1, ll2 = st.columns([6, 1])
        ll1.markdown(f"- [{lk['name']}]({lk['url']})")
        if ll2.button("✕", key=f"dl{i}"):
            s["custom_links"].pop(i)
            save_settings(s)
            st.rerun()
    with st.form("link_form", border=True):
        ln = st.text_input(C.L(C.T("名稱", "Name"), LANG), key="nl_n")
        lu = st.text_input(C.L(C.T("網址", "URL"), LANG), key="nl_u")
        if st.form_submit_button(C.L(C.T("加入連結", "Add link"), LANG)) and ln.strip() and lu.strip():
            s["custom_links"].append({"name": ln.strip(), "url": lu.strip()})
            save_settings(s)
            st.rerun()

    st.markdown("### 🔑 " + C.L(C.T("更改管理員密碼", "Change admin password"), LANG))
    if using_default_pw():
        st.warning(C.L(C.T("現正使用預設密碼 oshweb-admin(或在 Streamlit Secrets 設 ADMIN_PASSWORD)。請立即更改。",
                           "Using default password oshweb-admin (or set ADMIN_PASSWORD in Streamlit Secrets). Please change it now."), LANG))
    with st.form("pw_form", border=True):
        p1 = st.text_input(C.L(C.T("新密碼", "New password"), LANG), type="password", key="np1")
        p2 = st.text_input(C.L(C.T("確認新密碼", "Confirm password"), LANG), type="password", key="np2")
        if st.form_submit_button(C.L(C.T("更改密碼", "Change password"), LANG)):
            if p1 and p1 == p2:
                s["admin_password_sha256"] = sha256(p1)
                save_settings(s)
                st.success(C.L(C.T("✅ 密碼已更改", "✅ Password changed"), LANG))
            else:
                st.error(C.L(C.T("兩次輸入不一致", "Passwords do not match"), LANG))

    st.markdown("### 👥 " + C.L(C.T("會員名單", "Members"), LANG))
    members = load_json(MEMBERS_FILE, {})
    if members:
        st.dataframe(pd.DataFrame(
            [{"email": e, "name": r["name"], "joined": r.get("joined", "")}
             for e, r in members.items()]), width="stretch", hide_index=True)
    else:
        st.caption(C.L(C.T("暫無會員", "No members yet"), LANG))

    st.markdown("### 💾 " + C.L(C.T("設定備份(匯出/匯入)", "Settings backup (export/import)"), LANG))
    st.download_button(C.L(C.T("匯出設定 JSON", "Export settings JSON"), LANG),
                       json.dumps(s, ensure_ascii=False, indent=1),
                       file_name="oshweb-settings.json")
    up = st.file_uploader(C.L(C.T("匯入設定", "Import settings"), LANG), type="json")
    if up is not None and st.button(C.L(C.T("套用匯入", "Apply import"), LANG)):
        try:
            save_settings(json.loads(up.read().decode("utf-8")))
            st.rerun()
        except Exception as e:
            st.error(str(e))

    st.caption(C.L(C.T(
        "提示:Streamlit Cloud 的檔案系統屬暫存,重新部署後設定可能還原;重要設定請匯出備份,或在 repo 的 data/ 內直接維護。",
        "Note: Streamlit Cloud filesystem is ephemeral — settings may reset on redeploy. Export backups or maintain data/ in the repo."), LANG))


# ---------------------------------------------------------------- 側邊欄
def sidebar():
    # 一開網自動更新:每個瀏覽 session 首次載入即強制重抓官方來源
    if "initial_refresh_done" not in st.session_state:
        st.session_state.initial_refresh_done = True
        _live_data.clear()
        _legal_watch.clear()
    with st.sidebar:
        st.markdown(f"## 🦺 {C.L(C.UI['app_title'], LANG)}")
        st.caption(C.L(C.UI["tagline"], LANG))

        langs = {"tc": "繁體中文", "sc": "简体中文", "en": "English"}
        pick = st.segmented_control(
            t("lang_label"), list(langs.keys()),
            format_func=lambda k: langs[k],
            selection_mode="single", default=LANG, label_visibility="visible")
        if pick and pick != LANG:
            st.session_state.lang = pick
            st.rerun()

        if st.button(t("refresh"), width="stretch", type="primary"):
            _live_data.clear()
            st.cache_data.clear()
            st.rerun()
        d_hint = load_json(DATA / "news.json", {})
        st.caption(f"{t('updated_at')}: {get_data()['generated_at']}")

        # 會員狀態
        if st.session_state.get("member"):
            st.markdown(f"👤 **{st.session_state.member['name']}**")
        # 網主登入(後門)
        with st.expander(t("admin_login"), expanded=False):
            if st.session_state.is_admin:
                st.success(t("admin_ok"))
                if st.button(C.L(C.T("登出後台", "Log out admin"), LANG)):
                    st.session_state.is_admin = False
                    st.rerun()
            else:
                pw = st.text_input(t("admin_pw"), type="password", key="admin_pw_input")
                if st.button(C.L(C.T("登入", "Log in"), LANG), key="admin_login_btn"):
                    if check_admin_pw(pw):
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error(t("admin_fail"))
        st.caption("📝 " + C.L(C.UI["footer"], LANG))


# ---------------------------------------------------------------- 導航
def build_app():
    sidebar()
    admin = st.session_state.is_admin
    pages = [
        st.Page(pg_home, title=t("nav_home"), icon=":material/home:", default=True),
        st.Page(pg_law, title=t("nav_law"), icon=":material/gavel:"),
        st.Page(pg_cop, title=t("nav_cop"), icon=":material/menu_book:"),
        st.Page(pg_ppe, title=t("nav_ppe"), icon=":material/health_and_safety:"),
        st.Page(pg_msds, title=t("nav_msds"), icon=":material/science:"),
        st.Page(pg_tech, title=t("nav_tech"), icon=":material/smart_toy:"),
        st.Page(pg_ai, title=t("nav_ai"), icon=":material/forum:"),
        st.Page(pg_news, title=t("nav_news"), icon=":material/newspaper:"),
        st.Page(pg_accident, title=t("nav_accident"), icon=":material/emergency:"),
        st.Page(pg_fire, title=t("nav_fire"), icon=":material/local_fire_department:"),
        st.Page(pg_so, title=t("nav_so"), icon=":material/engineering:"),
        st.Page(pg_yt, title=t("nav_yt"), icon=":material/play_circle:"),
        st.Page(pg_files, title=t("nav_files"), icon=":material/folder:"),
        st.Page(pg_member, title=t("nav_member"), icon=":material/person:"),
        st.Page(pg_sources, title=t("nav_sources"), icon=":material/library_books:"),
    ]
    if admin:
        pages.append(st.Page(pg_admin, title=t("nav_admin"), icon=":material/settings:"))
    nav = st.navigation(pages, position="sidebar")
    nav.run()
    st.divider()
    st.caption(f"🦺 {C.L(C.UI['app_title'], LANG)} — {C.L(C.UI['footer'], LANG)}")


build_app()
