# -*- coding: utf-8 -*-
"""
月度工傷新聞報告生成器
======================
讀取 data/news.json,彙總指定月份的工傷/意外報道,輸出 PDF(中文)。
用法:
  python scripts/monthly_report.py              # 上個月
  python scripts/monthly_report.py 2026 9       # 指定年月
依賴:reportlab(GitHub Actions / Streamlit 版已安裝;本機請 pip install reportlab)
"""

import io
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
HKT = timezone(timedelta(hours=8))


def month_range(year, month):
    start = date(year, month, 1)
    end = date(year + (month == 12), (month % 12) + 1, 1)
    return start, end


def collect(year, month, items=None):
    """取該月工傷/意外報道(item.date 或 fetched 落於月份)。"""
    if items is None:
        items = json.loads((DATA / "news.json").read_text(encoding="utf-8"))["items"]
    start, end = month_range(year, month)
    out = []
    for it in items:
        if it.get("category") != "accident":
            continue
        ds = (it.get("date") or it.get("fetched") or "")[:10]
        try:
            d = datetime.strptime(ds, "%Y-%m-%d").date()
        except ValueError:
            continue
        if start <= d < end:
            out.append(it)
    return out


def _pdf_lib():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    for fname in ("MSung-Light", "STSong-Light"):  # 繁體優先,退回簡體字庫
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(fname))
            return A4, colors, ParagraphStyle, fname, (SimpleDocTemplate, Paragraph,
                                                       Spacer, Table, TableStyle)
        except Exception:
            continue
    raise RuntimeError("reportlab CID 字體註冊失敗,請 pip install -U reportlab")


def build_pdf(year, month, items):
    A4, colors, ParagraphStyle, font, (SimpleDocTemplate, Paragraph,
                                       Spacer, Table, TableStyle) = _pdf_lib()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"工傷新聞月報 {year}-{month:02d}")
    base = ParagraphStyle("base", fontName=font, fontSize=10.5, leading=15,
                          wordWrap="CJK")
    h1 = ParagraphStyle("h1", parent=base, fontSize=17, leading=22, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=base, fontSize=13, leading=18,
                        spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#0b4f8a"))
    small = ParagraphStyle("small", parent=base, fontSize=8.5, leading=12,
                           textColor=colors.HexColor("#64748b"))

    story = [
        Paragraph(f"香港工傷／工作意外新聞月報({year}年{month}月)", h1),
        Paragraph("本報告由香港職業安全資訊網自動彙總:來源為政府新聞公報、政府新聞網、香港電台等"
                  "官方來源,經關鍵字(工傷、工業意外、致命、墮斃、觸電、倒塌等)自動分類,"
                  "**並非官方工傷統計**;正式數據請參閱勞工處職業安全及健康部公佈。", base),
        Spacer(1, 8),
    ]

    by_src, by_region = {}, {}
    for it in items:
        by_src[it["source_label"]] = by_src.get(it["source_label"], 0) + 1
        by_region[it.get("region", "HK")] = by_region.get(it.get("region", "HK"), 0) + 1
    story.append(Paragraph(f"本月共收錄 <b>{len(items)}</b> 條相關報道。", h2))
    stat_rows = [["來源", "條數"]] + [[k, str(v)] for k, v in sorted(by_src.items(),
                                                                            key=lambda x: -x[1])]
    t = Table(stat_rows, colWidths=[380, 80])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dde5ec")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b4f8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fa")]),
    ]))
    story += [t, Spacer(1, 10), Paragraph("報道清單(依日期)", h2)]
    if not items:
        story.append(Paragraph("本月無收錄報道。", base))
    for it in sorted(items, key=lambda x: (x.get("date") or x["fetched"]), reverse=True):
        d = (it.get("date") or it.get("fetched"))[:10]
        story.append(Paragraph(
            f"<b>{d}</b>｜{it['title']}<br/><font size=8.5 color=#64748b>"
            f"來源:{it['source_label']}｜<link href=\"{it['url']}\">{it['url'][:90]}</link></font>",
            base))
        story.append(Spacer(1, 3))

    story += [Spacer(1, 12),
              Paragraph(f"生成時間:{datetime.now(HKT).strftime('%Y-%m-%d %H:%M')}（香港時間）"
                        f"｜香港職業安全資訊網(非官方)", small)]
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    today = datetime.now(HKT).date()
    if len(sys.argv) >= 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])
    else:
        year, month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
    items = collect(year, month)
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / f"injury-report-{year}-{month:02d}.pdf"
    path.write_bytes(build_pdf(year, month, items))
    print(f"✓ 已生成 {path}({len(items)} 條報道)")


if __name__ == "__main__":
    main()
