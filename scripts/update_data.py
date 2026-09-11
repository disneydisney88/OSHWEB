# -*- coding: utf-8 -*-
"""
香港職業安全資訊網 — 資料自動更新腳本
========================================
只使用 Python 標準庫,無需安裝任何套件。

功能:
  1. 抓取官方 RSS / 網頁列表 → data/news.json (最新職安資訊、工傷新聞)
  2. 下載勞工處「註冊安全主任及安全審核員主要統計數字」開放數據 (XLSX)
     → data/rso_stats.json (安全主任數目)

所有資料均標明來源機構、來源網址及抓取時間;單一來源失敗不影響其他來源,
失敗狀況會記錄在 JSON 的 sources[].status 之中,網站會如實顯示。

排程自動更新:見 README.md(Windows 工作排程器 / cron)。
"""

import hashlib
import html
import io
import json
import re
import sys
import urllib.request
import urllib.error
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HKT = timezone(timedelta(hours=8))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TIMEOUT = 30

# ---------------------------------------------------------------- 關鍵字分類
# 職安/勞工相關關鍵字(用於過濾綜合新聞源,只保留與職業安全相關的報道)
OSH_KEYWORDS = [
    "職安", "職業安全", "職業健康", "勞工處", "工傷", "工業意外", "意外",
    "致命", "奪命", "墮斃", "墮樓", "墮海", "壓斃", "觸電", "不治", "送院",
    "昏迷", "被困", "火警", "火災", "爆炸", "洩漏", "倒塌", "中毒",
    "安全事故", "消防", "建造業", "工地", "棚架", "吊運", "密閉空間",
    "註冊安全主任", "安全主任", "僱員", "僱主", "勞工", "檢控", "定罪",
    "安全智慧工地", "個人防護裝備",
]
# 工傷/意外類關鍵字(較嚴格,用於「工傷新聞」分類)
ACCIDENT_KEYWORDS = [
    "工傷", "工業意外", "意外", "致命", "奪命", "墮斃", "墮樓", "墮海",
    "壓斃", "觸電", "不治", "送院", "昏迷", "被困", "倒塌", "中毒",
    "爆炸", "火警", "火災", "安全事故", "洩漏",
]

# ---------------------------------------------------------------- 資料來源
# region: HK=香港 / CN=中國內地 / INTL=國際
# method: rss=RSS訂閱 / html=網頁抓取
SOURCES = [
    {"id": "gia", "region": "HK", "label": "香港政府新聞公報(含勞工處)",
     "method": "rss", "url": "https://www.info.gov.hk/gia/rss/general_zh.xml",
     "home": "https://www.info.gov.hk", "filter": True, "cap": 40},
    {"id": "news_top", "region": "HK", "label": "香港政府新聞網·頭條",
     "method": "rss", "url": "https://www.news.gov.hk/tc/common/html/topstories.rss.xml",
     "home": "https://www.news.gov.hk", "filter": True, "cap": 25},
    {"id": "news_law", "region": "HK", "label": "香港政府新聞網·法律及治安",
     "method": "rss", "url": "https://www.news.gov.hk/tc/categories/law_order/html/articlelist.rss.xml",
     "home": "https://www.news.gov.hk", "filter": False, "cap": 30},
    {"id": "news_admin", "region": "HK", "label": "香港政府新聞網·政府施政",
     "method": "rss", "url": "https://www.news.gov.hk/tc/categories/admin/html/articlelist.rss.xml",
     "home": "https://www.news.gov.hk", "filter": True, "cap": 25},
    {"id": "rthk_local", "region": "HK", "label": "香港電台·本地新聞",
     "method": "rss", "url": "https://rthk9.rthk.hk/rthk/news/rss/c_expressnews_clocal.xml",
     "home": "https://news.rthk.hk", "filter": True, "cap": 25},
    {"id": "rthk_intl", "region": "INTL", "label": "香港電台·國際新聞",
     "method": "rss", "url": "https://rthk9.rthk.hk/rthk/news/rss/c_expressnews_cinternational.xml",
     "home": "https://news.rthk.hk", "filter": True, "cap": 20},
    {"id": "mem_cn", "region": "CN", "label": "中華人民共和國應急管理部",
     "method": "html", "url": "https://www.mem.gov.cn/xw/bndt/",
     "home": "https://www.mem.gov.cn", "filter": False, "cap": 20},
    {"id": "yt_alert", "region": "HK", "kind": "video", "label": "YouTube·勞工處職安警示(職安局頻道)",
     "method": "rss", "url": "https://www.youtube.com/feeds/videos.xml?playlist_id=PLER7fEcUu9f7Vg8z4zUYZiEZWBC9rA4Fc",
     "home": "https://www.youtube.com/user/OSHC2009", "filter": False, "cap": 12},
    {"id": "hko_warn", "region": "HK", "kind": "weather", "label": "天文台·天氣警示",
     "method": "rss", "url": "https://rss.weather.gov.hk/rss/WeatherWarningSummaryv2_uc.xml",
     "home": "https://www.hko.gov.hk", "filter": False, "cap": 6},
    {"id": "osha", "region": "INTL", "label": "美國職業安全健康局(OSHA)",
     "method": "html", "url": "https://www.osha.gov/news/newsreleases",
     "home": "https://www.osha.gov", "filter": False, "cap": 15},
    {"id": "hse", "region": "INTL", "label": "英國健康與安全局(HSE)",
     "method": "rss", "url": "https://press.hse.gov.uk/feed/",
     "home": "https://www.hse.gov.uk", "filter": False, "cap": 15},
]

# 明顯非新聞的錨點標題(小寫比對)
JUNK_TITLES = {
    "establishment search", "search", "home", "menu", "news", "contact",
    "subscribe", "log in", "login", "skip to content", "more", "read more",
}

RSO_STATS = {
    "id": "rso_stats",
    "label": "勞工處開放數據:註冊安全主任及安全審核員主要統計數字",
    "xlsx_url": "https://www.labour.gov.hk/datagovhk/resource/rstd/rstd-keystats_tc.xlsx",
    "dataset_page": "https://data.gov.hk/tc-data/dataset/hk-ld-rstd-rstd-keystats",
}


def now_hkt():
    return datetime.now(HKT).strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- 網絡抓取
def fetch(url):
    """下載 URL,自動處理 gzip,按 utf-8 → gbk 順序解碼。"""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Language": "zh-HK,zh-TW;q=0.9,en;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding", "").lower() == "gzip":
            import gzip
            raw = gzip.decompress(raw)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(raw, url=None):
    """盡力從 pubDate 或網址(如 /202609/)推斷日期,回傳 ISO 字串或 None。"""
    if raw:
        try:
            return parsedate_to_datetime(raw.strip()).astimezone(HKT).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    if url:
        m = re.search(r"/(\d{6})/", url)
        if m:
            ym = m.group(1)
            return f"{ym[:4]}-{ym[4:6]}"
    return None


# ---------------------------------------------------------------- RSS 解析
def parse_rss(text, source, fetched):
    items = []
    # RSS 2.0 / Atom 皆兼容的最簡提取
    for block in re.findall(r"<item[ >].*?</item>|<entry[ >].*?</entry>", text, re.S):
        title_m = re.search(r"<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.S)
        link_m = re.search(r"<link[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", block, re.S) \
            or re.search(r"<link[^>]*href=[\"']([^\"']+)", block)
        date_m = re.search(r"<pubDate[^>]*>(.*?)</pubDate>|<updated[^>]*>(.*?)</updated>|<published[^>]*>(.*?)</published>", block, re.S)
        desc_m = re.search(r"<description[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>|<summary[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</summary>", block, re.S)
        title = strip_tags(title_m.group(1)) if title_m else ""
        link = (link_m.group(1) if link_m.lastindex else link_m.group(1)).strip() if link_m else ""
        if not title or not link:
            continue
        raw_date = None
        if date_m:
            raw_date = next(g for g in date_m.groups() if g)
        date = parse_date(raw_date, link)
        summary = strip_tags(desc_m.group(1) or desc_m.group(2) or "")[:160] if desc_m else ""
        items.append(make_item(title, link, source, date, summary, fetched))
    return items


# ---------------------------------------------------------------- HTML 抓取
NAV_JUNK = re.compile(
    r"(index|default|about|contact|search|login|register|sitemap|rss|"
    r"javascript:|#|^mailto:|^tel:)", re.I)


def parse_html_list(text, base_url, source, fetched, min_title=8):
    items, seen = [], set()
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.S | re.I):
        href, inner = m.group(1).strip(), m.group(2)
        # 標題:優先 title 屬性,否則錨點文字
        tm = re.search(r'title=["\']([^"\']+)["\']', m.group(0))
        title = html.unescape(tm.group(1)).strip() if tm else strip_tags(inner)
        if not title or len(title) < min_title:
            continue
        if title.lower() in JUNK_TITLES:
            continue
        if NAV_JUNK.search(href):
            continue
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(base_url, href)
        elif href.startswith("./"):
            from urllib.parse import urljoin
            href = urljoin(base_url, href[2:])
        elif not href.startswith("http"):
            continue
        # 必須是指向文章內容的連結(.htm/.html/.shtml/.aspx 或含日期路徑)
        if not re.search(r"\.(s?html?|aspx|php)([?#].*)?$", href) and "/20" not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        items.append(make_item(title, href, source, parse_date(None, href), "", fetched))
    return items


def make_item(title, link, source, date, summary, fetched):
    item_id = hashlib.md5(link.encode("utf-8")).hexdigest()[:12]
    blob = title + " " + summary
    is_acc = any(k in blob for k in ACCIDENT_KEYWORDS) and source["region"] == "HK"
    return {
        "id": item_id,
        "title": title,
        "url": link,
        "source_id": source["id"],
        "source_label": source["label"],
        "region": source["region"],
        "kind": source.get("kind", "news"),
        "date": date,
        "fetched": fetched,
        "summary": summary,
        "category": "accident" if is_acc else "news",
    }


# ---------------------------------------------------------------- XLSX(僅標準庫)
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def col_index(ref):
    letters = re.match(r"([A-Z]+)", ref or "A")
    n = 0
    for ch in letters.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx_rows(data, max_rows=120):
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.iter(NS + "si"):
            shared.append("".join(t.text or "" for t in si.iter(NS + "t")))
    sheets = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    if not sheets:
        raise ValueError("XLSX 內找不到工作表")
    root = ET.fromstring(z.read(sheets[0]))
    rows = []
    for row in root.iter(NS + "row"):
        vals = {}
        for c in row.iter(NS + "c"):
            idx = col_index(c.get("r"))
            t = c.get("t")
            if t == "s":
                v_el = c.find(NS + "v")
                v = shared[int(v_el.text)] if v_el is not None and v_el.text else ""
            elif t == "inlineStr":
                v = "".join(tt.text or "" for tt in c.iter(NS + "t"))
            else:
                v_el = c.find(NS + "v")
                v = v_el.text if v_el is not None and v_el.text else ""
            vals[idx] = (v or "").strip()
        if vals:
            width = max(vals) + 1
            rows.append([vals.get(i, "") for i in range(width)])
        if len(rows) >= max_rows:
            break
    return rows


# ---------------------------------------------------------------- 主流程
def fetch_source(src, fetched):
    try:
        text = fetch(src["url"])
        if src["method"] == "rss":
            items = parse_rss(text, src, fetched)
        else:
            items = parse_html_list(text, src["url"], src, fetched)
        if src.get("filter"):
            filtered = [i for i in items if any(k in i["title"] + i["summary"] for k in OSH_KEYWORDS)]
            items = filtered or items[:3]  # 全部不合關鍵字時保留前3條作參考
        items = items[: src.get("cap", 30)]
        return items, "ok"
    except Exception as e:  # 單一來源失敗不影響整體
        return [], f"失敗:{type(e).__name__}: {e}"


def sort_items(items):
    """有日期的按日期新→舊排前面,無日期的排其後(按抓取時間)。"""
    dated = sorted([i for i in items if i.get("date")], key=lambda x: x["date"], reverse=True)
    undated = sorted([i for i in items if not i.get("date")], key=lambda x: x["fetched"], reverse=True)
    return dated + undated


def collect_news(fetched=None):
    """抓取全部新聞來源,回傳 (items, source_status)。供本腳本及 Streamlit 應用共用。"""
    fetched = fetched or now_hkt()
    all_items, seen_links, source_status = [], set(), []
    for src in SOURCES:
        items, status = fetch_source(src, fetched)
        added = 0
        for it in items:
            key = it["url"].split("?")[0].rstrip("/")
            if key in seen_links:
                continue
            seen_links.add(key)
            all_items.append(it)
            added += 1
        source_status.append({
            "id": src["id"], "label": src["label"], "region": src["region"],
            "method": "RSS 訂閱" if src["method"] == "rss" else "網頁抓取",
            "url": src["url"], "status": status, "count": added, "fetched": fetched,
        })
        print(f"  [{'✓' if status == 'ok' else '✗'}] {src['label']}:新增 {added} 條 ({status})")
    return sort_items(all_items)[:400], source_status


def collect_rso(fetched=None):
    """下載勞工處「註冊安全主任及安全審核員主要統計數字」XLSX。失敗回傳 None。"""
    fetched = fetched or now_hkt()
    req = urllib.request.Request(RSO_STATS["xlsx_url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        rows = read_xlsx_rows(resp.read())
    rows = [r for r in rows if any(c.strip() for c in r)]
    return {
        "generated_at": fetched,
        "source_label": RSO_STATS["label"],
        "source_url": RSO_STATS["xlsx_url"],
        "dataset_page": RSO_STATS["dataset_page"],
        "retrieved": fetched,
        "note": "數據由勞工處按年更新;本表為自動下載之原始統計,以勞工處公佈為準。",
        "rows": rows,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fetched = now_hkt()
    print(f"[{fetched}] 開始更新香港職業安全資訊網資料…")

    all_items, source_status = collect_news(fetched)
    (DATA_DIR / "news.json").write_text(
        json.dumps({
            "generated_at": fetched,
            "description": "由 scripts/update_data.py 自動抓取之官方來源資訊,全部內容版權屬原本機構。",
            "sources": source_status,
            "count": len(all_items),
            "items": all_items,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  ✓ data/news.json:共 {len(all_items)} 條")

    try:
        stats = collect_rso(fetched)
        (DATA_DIR / "rso_stats.json").write_text(
            json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  ✓ data/rso_stats.json:{len(stats['rows'])} 行")
    except Exception as e:
        print(f"  ✗ 安全主任統計下載失敗:{e}")

    print(f"[{datetime.now(HKT).strftime('%Y-%m-%d %H:%M')}] 更新完成。")


if __name__ == "__main__":
    main()
