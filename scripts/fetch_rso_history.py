# -*- coding: utf-8 -*-
"""
從勞工處年報(HK Labour Department Annual Report)抓取歷年
「截至年底持有有效註冊的安全主任人數」,更新 data/rso_history.json。
年報網頁:https://www.labour.gov.hk/tc/public/AnnualReportArchived.htm
          → /tc/public/iprd/{年份}/chapterN.html(第四章:工作安全與健康)
句子格式:「截至年底,共有NNNN名安全主任持有有效的註冊」
最新兩年另以開放數據 XLSX 交叉核對(update_data.py)。
只使用標準庫。
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "rso_history.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126"
BASE = "https://www.labour.gov.hk/tc/public/iprd/{year}/chapter{n}.html"
YEARS = range(2015, 2025)          # 勞工處官網提供的年報年份
CHAPTERS = range(1, 8)             # 逐章掃描,避免章號改動
PATTERN = re.compile(
    r"截至年底[，,]?\s*共有\s*([\d,]{3,6})\s*名安全主任持有有效的註冊")
# 兼容:「共有 4 409 名」(法式空格)等寫法
PATTERN2 = re.compile(
    r"([\d][\d,\s]{2,7})\s*名安全主任持有有效的註冊")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean(text):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    import html as _html
    text = _html.unescape(text)
    return re.sub(r"[\s\u00a0]", "", text)


def extract_year(year):
    for n in CHAPTERS:
        try:
            body = clean(fetch(BASE.format(year=year, n=n)))
        except Exception:
            continue
        m = PATTERN.search(body) or PATTERN2.search(body)
        if m:
            count = int(re.sub(r"[,\s]", "", m.group(1)))
            return count, BASE.format(year=year, n=n)
    return None, None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    history = {}
    try:
        history = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        pass
    series = history.get("series", {})
    for year in YEARS:
        if str(year) in series:            # 已有則不重抓
            continue
        count, url = extract_year(year)
        if count:
            series[str(year)] = {"count": count, "source": url}
            print(f"  ✓ {year}:{count:,}")
        else:
            print(f"  ✗ {year}:未能從年報解析(該年或無此句式)")
    series_sorted = dict(sorted(series.items(), key=lambda kv: kv[0]))
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    history = {
        "generated_at": now,
        "source_label": "香港勞工處年報「工作安全與健康」章節(官網 iprd 存檔)",
        "source_home": "https://www.labour.gov.hk/tc/public/AnnualReportArchived.htm",
        "note": "歷年「截至年底持有有效註冊的安全主任」人數,逐句解析自勞工處年報官方網頁;"
                "最近兩年以勞工處開放數據 XLSX 自動更新並交叉核對。",
        "series": series_sorted,
    }
    OUT.write_text(json.dumps(history, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ data/rso_history.json 共 {len(series_sorted)} 個年份")


if __name__ == "__main__":
    main()
