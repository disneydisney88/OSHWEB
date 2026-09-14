# -*- coding: utf-8 -*-
"""
香港職業安全資訊網 — 三語內容(繁體中文/簡體中文/English)
繁中為原文;英文為人工翻譯;簡中由繁中自動轉換(zhconv,未安裝則顯示繁中)。
每段內容均附「來源」說明。

區塊種類:
  ("p", pair)                    段落
  ("h", pair)                    小標
  ("table", headers_pair, rows_pair)   表格:pair 各為 {"tc":[...], "en":[...]}
  ("ul", pair) / ("ol", pair)    清單:pair 各為 {"tc":[...], "en":[...]}
  ("src", pair)                  來源行(markdown)
"""

try:
    from zhconv import convert as _zh_convert

    def tc2sc(text: str) -> str:
        return _zh_convert(text, "zh-hans")
except Exception:  # 未安裝 zhconv 時退回繁體
    def tc2sc(text: str) -> str:
        return text


def T(tc, en):
    """定義一段雙語文字;簡體於顯示時由繁體自動轉換。"""
    if isinstance(tc, list):
        return {"tc": list(tc), "en": list(en)}
    return {"tc": tc, "en": en}


def L(pair, lang):
    if lang == "en":
        return pair["en"]
    if lang == "sc":
        tc = pair["tc"]
        if isinstance(tc, list):
            return [tc2sc(x) for x in tc]
        return tc2sc(tc)
    return pair["tc"]


# ---------------------------------------------------------------- 介面文字
UI = {
    "app_title": T("香港職業安全資訊網", "HK OSH Information Portal"),
    "tagline": T("非官方資訊整合平台·自動更新·列明來源",
                 "Unofficial aggregator · auto-updated · sources cited"),
    "lang_label": T("語言 Language", "Language 語言"),
    "nav_home": T("🏠 主頁", "🏠 Home"),
    "nav_law": T("⚖️ 法例法規", "⚖️ Legislation"),
    "nav_cop": T("📘 工作守則 COP", "📘 Codes of Practice"),
    "nav_ppe": T("🧤 PPE 防護裝備", "🧤 PPE"),
    "nav_msds": T("🧪 化學品 MSDS", "🧪 Chemicals / MSDS"),
    "nav_tech": T("🤖 AI／4S 科技", "🤖 AI / 4S Technology"),
    "nav_news": T("📰 最新資訊", "📰 Latest News"),
    "nav_accident": T("🚑 工傷新聞", "🚑 Injury News"),
    "nav_fire": T("🔥 防火安全", "🔥 Fire Safety"),
    "nav_so": T("👷 安全主任", "👷 Safety Officers"),
    "nav_yt": T("▶️ YouTube 影片", "▶️ YouTube Videos"),
    "nav_member": T("👤 會員專區", "👤 Members"),
    "nav_files": T("📁 檔案資源庫", "📁 File Library"),
    "nav_sources": T("📚 資訊來源", "📚 Sources"),
    "nav_admin": T("⚙️ 網主設定", "⚙️ Admin"),
    "nav_ai": T("🤖 AI 職安助手", "🤖 AI OSH Assistant"),
    "grp_knowledge": T("📚 職安知識", "📚 OSH Knowledge"),
    "grp_news": T("📰 最新資訊", "📰 News"),
    "grp_inter": T("🤖 智能及互動", "🤖 Smart & Interactive"),
    "grp_about": T("ℹ️ 關於本站", "ℹ️ About"),
    "refresh": T("🔄 立即更新資料", "🔄 Refresh now"),
    "refreshing": T("正在向官方來源抓取最新資料…", "Fetching latest data from official sources…"),
    "updated_at": T("資料更新於", "Data updated at"),
    "auto_note": T("開站即自動更新,其後每30分鐘自動重抓;亦可按「立即更新」。",
                   "Auto-refresh on open, then every 30 minutes; click “Refresh now” to force."),
    "legal_alert": T("⚖️ **法例有更新**:勞工處職安法例頁面偵測到內容變更,請查看:",
                     "⚖️ **Legislation updated**: change detected on LD OSH legislation pages:"),
    "legal_ack": T("⚖️ 確認法例基準(清除警示)", "⚖️ Acknowledge legislation baseline (clear alert)"),
    "legal_watch_admin": T("⚖️ 法例變更監察", "⚖️ Legislation change watch"),
    "legal_none": T("未偵測到法例頁面變更。", "No legislation page changes detected."),
    "report_btn": T("📥 下載上月工傷新聞PDF報告", "📥 Download last month's injury-news PDF report"),
    "ai_intro": T("向 AI 職安助手提問,答案基於**本站收錄的法例、工作守則、PPE、MSDS、防火及安全主任內容**,並列出參考章節。AI 回答僅供參考,一切以官方來源為準。",
                  "Ask the AI OSH assistant — answers are grounded in this site's legislation, COP, PPE, MSDS, fire-safety and RSO content, with references cited. For reference only; official sources prevail."),
    "ai_no_key": T("尚未設定 AI 金鑰:請在 Streamlit Cloud「Settings → Secrets」加入 `LLM_API_KEY = \"你的GLM金鑰\"`(可選 `LLM_MODEL`,預設 glm-4-flash;GLM 接口為 OpenAI 兼容格式)。",
                   "No AI key configured: add `LLM_API_KEY = \"your GLM key\"` in Streamlit Cloud → Settings → Secrets (optional `LLM_MODEL`, default glm-4-flash; GLM uses the OpenAI-compatible API)."),
    "ai_thinking": T("正在翻查本站內容及生成回答…", "Searching site content and generating an answer…"),
    "ai_sources": T("參考本站章節", "Referenced sections"),
    "ai_upload": T("📷 上載工地相片(可選,JPG/PNG),AI會分析可見危險及可能涉及的法例",
                   "📷 Upload a site photo (optional, JPG/PNG) — the AI will analyse visible hazards and possible legal issues"),
    "ai_img_question": T("請以工作安全角度分析這張相片:畫面中有什麼危險?可能違反哪些香港職安法例(例如第509章、第59章及其規例)的要求?請逐項說明及建議改善方法。",
                         "Analyse this photo from a work-safety perspective: what hazards are visible, and which HK OSH legal requirements (Cap.509/Cap.59 and subs. regs.) might be engaged? List items and suggest improvements."),
    "ai_disclaimer": T("⚠️ **聲明:以上(及本助手所有)回答僅供參考,不構成法律或專業意見;實際安全事宜請諮詢註冊安全主任、合資格專業人士或勞工處職業安全及健康部,一切以官方最新公佈為準。**",
                       "⚠️ **Disclaimer: all answers are for reference only and are not legal or professional advice; consult an RSO, a competent professional or the LD OSH Division, and rely on the latest official publications.**"),
    "ai_err_401": T("AI金鑰無效(401):請檢查 Streamlit Secrets 的 LLM_API_KEY 是否為**完整GLM金鑰**(id.secret 兩段式全複製),或該金鑰是否已過期。",
                    "AI key invalid (401): check that LLM_API_KEY in Streamlit Secrets is a complete GLM key (both id.secret parts) and still valid."),
    "footer": T("本網為非官方資訊整合平台,內容僅供參考,一切以官方來源最新公佈為準。",
                "Unofficial aggregator for reference only; always refer to official sources."),
    "src_line": T("來源", "Source"),
    "none_yet": T("暫無資料,請按「立即更新」或稍後再試。", "No data yet — click “Refresh now” or try later."),
    "fallback_note": T("即時抓取失敗,現正顯示最近一次成功下載的資料。",
                       "Live fetch failed — showing the last successfully saved data."),
    "news_hk": T("🇭🇰 香港", "🇭🇰 Hong Kong"),
    "news_cn": T("🇨🇳 中國內地", "🇨🇳 Mainland China"),
    "news_intl": T("🌍 國際", "🌍 International"),
    "weather_now": T("🌤️ 天文台天氣警示(工作安排提示)", "🌤️ HKO Weather Warnings (work-arrangement alerts)"),
    "weather_tip": T("酷熱天氣請按勞工處防中暑指引安排補水及休息;八號風球或黑雨期間應暫停戶外及吊運等高危工序。",
                     "In hot weather follow LD heat-stress guidance (water & rest); suspend outdoor / lifting work during T8 or Black Rainstorm."),
    "accident_note": T("以下為從官方新聞來源自動以關鍵字(工傷、工業意外、致命、墮斃、觸電、倒塌等)篩選的報道,**並非官方工傷統計**;官方數據請參閱勞工處職業安全及健康部年報。",
                       "Auto-filtered from official news by keywords (work injury, industrial accident, fatal…). **Not official statistics** — see LD OSH annual reports for official data."),
    "member_only": T("會員專區", "Members' Area"),
    "admin_login": T("🔒 網主後台登入", "🔒 Admin login"),
    "admin_pw": T("管理員密碼", "Admin password"),
    "admin_ok": T("✅ 已登入網主後台", "✅ Admin logged in"),
    "admin_fail": T("密碼錯誤", "Wrong password"),
    "drive_btn": T("📁 開啟 Google Drive 資源庫", "📁 Open Google Drive library"),
    "latest": T("📌 最新動態", "📌 Latest updates"),
    "accidents_now": T("🚑 最新工傷／意外報道", "🚑 Latest injury / accident reports"),
    "rso_stat": T("👷 註冊安全主任人數(勞工處統計)", "👷 Registered Safety Officers (LD statistics)"),
    "quick_links": T("🛠️ 快速官方連結", "🛠️ Quick official links"),
    "see_all": T("查看全部", "See all"),
    "all": T("全部", "All"),
}

DRIVE_URL = "https://drive.google.com/drive/folders/17fBRgBi7aVPOJ7Il-nFBU0fMWKIlJ7oc?usp=sharing"

YT_CHANNELS = [
    ("職業安全健康局 OSHC", "https://www.youtube.com/user/OSHC2009",
     T("職安局官方頻道:職安健宣傳片、網上講堂,並轉載勞工處《職安警示》系列。",
       "OSHC official channel: OSH promo videos, online seminars, and LD “Safety Alert” series.")),
    ("勞工處職安警示播放清單", "https://www.youtube.com/playlist?list=PLER7fEcUu9f7Vg8z4zUYZiEZWBC9rA4Fc",
     T("勞工處製作之工業意外警示動畫及宣傳短片(本站「最新資訊」已自動同步此清單)。",
       "LD safety-alert animations & clips (auto-synced into this site's Latest News).")),
    ("CIC Channel(建造業議會)", "https://www.youtube.com/channel/UCsK1xjqkm-xHCZTe1E3B26Q",
     T("建造業安全、培訓及建築科技影片。", "Construction safety, training and construction-tech videos.")),
    ("香港建造學院 HKIC", "https://www.youtube.com/@hkic.official",
     T("建造業培訓課程及安全訓練資訊。", "Construction training programmes and safety courses.")),
    ("政府新聞處 ISD", "https://www.youtube.com/@isdgovhk",
     T("政府宣傳片,包括職安、消防及勞工權益主題。", "Government promos incl. OSH, fire safety and labour rights.")),
]

SECTIONS = {}

# ---------------------------------------------------------------- 法例
SECTIONS["law"] = {
    "title": T("⚖️ 香港職業安全法例法規", "⚖️ HK OSH Legislation"),
    "intro": T(
        "香港職安法例有兩大骨幹:**第509章《職業安全及健康條例》**(適用於幾乎所有工作場所)及**第59章《工廠及工業經營條例》**(適用於工業經營),其下設多項附屬規例。完整及最新文本一律以官方為準。",
        "Two pillars: **Cap. 509 Occupational Safety and Health Ordinance** (nearly all workplaces) and **Cap. 59 Factories and Industrial Undertakings Ordinance** (industrial undertakings), plus subsidiary regulations. Always rely on the official texts."),
    "panels": [
        {
            "h": T("主體條例", "Principal ordinances"),
            "blocks": [
                ("table",
                 T(["法例", "重點", "官方連結(來源)"], ["Ordinance", "Key points", "Official links"]),
                 T([
                     ["**第509章《職業安全及健康條例》**", "適用於幾乎所有工作場所。僱主須確保僱員工作安全與健康(第6條);處所佔用人須確保在處所受僱人士安全(第7條);僱員須照顧自己及他人並與僱主合作(第8條)。", "[勞工處介紹](https://www.labour.gov.hk/tc/legislat/content4.htm)｜[電子版法例](https://www.elegislation.gov.hk/hk/cap509)"],
                     ["**第59章《工廠及工業經營條例》**", "工業經營(工廠、建築地盤、貨櫃處理等)東主的一般安全責任(第6A條)及僱員責任(第6B條);授權訂立各行業安全規例。", "[勞工處介紹](https://www.labour.gov.hk/tc/legislat/content3.htm)｜[電子版法例](https://www.elegislation.gov.hk/hk/cap59)"],
                 ], [
                     ["**Cap. 509 OSH Ordinance**", "Applies to nearly all workplaces. Employers must ensure employees' safety and health so far as reasonably practicable (s.6); premises occupiers (s.7); employees must take care and co-operate (s.8).", "[LD page](https://www.labour.gov.hk/tc/legislat/content4.htm)｜[e-Legislation](https://www.elegislation.gov.hk/hk/cap509)"],
                     ["**Cap. 59 FIU Ordinance**", "General duties of proprietors of industrial undertakings (s.6A) and of persons employed (s.6B); empowers industry safety regulations.", "[LD page](https://www.labour.gov.hk/tc/legislat/content3.htm)｜[e-Legislation](https://www.elegislation.gov.hk/hk/cap59)"],
                 ])),
                ("src", T("來源:勞工處職安法例專頁及電子版香港法例。",
                          "Sources: LD legislation pages and HK e-Legislation.")),
            ],
        },
        {
            "h": T("常用附屬規例", "Key subsidiary regulations"),
            "blocks": [
                ("table",
                 T(["規例", "適用範圍／重點", "官方連結"], ["Regulation", "Scope / key points", "Official links"]),
                 T([
                     ["第59I章《建築地盤(安全)規例》", "建築地盤安全:棚架、洞口圍封、機械、用電、個人防護等。", "[勞工處法例一覽](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                     ["第59AF章《工廠及工業經營(安全管理)規例》", "指定工業經營(如大型承建商、造價指定金額以上工程)須建立含14項元素的安全管理制度,並按僱員人數進行安全審核/查核。", "[法例](https://www.elegislation.gov.hk/hk/cap59AF)｜[勞工處法例一覽](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                     ["第59Z章《工廠及工業經營(安全主任及安全督導員)規例》", "須僱用註冊安全主任／安全督導員的工業經營類別及註冊資格。", "[法例](https://www.elegislation.gov.hk/hk/cap59Z)｜[勞工處註冊指南](https://www.labour.gov.hk/tc/faq/oshq8_whole.html)"],
                     ["第509A章《職業安全及健康(顯示屏幕設備)規例》", "工作間使用顯示屏幕設備的工作環境及風險評估要求。", "[勞工處法例一覽](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                 ], [
                     ["Cap. 59I Construction Sites (Safety) Regulations", "Site safety: scaffolds, openings, machinery, electricity, PPE, etc.", "[LD list](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                     ["Cap. 59AF FIU (Safety Management) Regulation", "Specified undertakings (e.g. large contractors) must implement a 14-element safety management system with safety audits/reviews.", "[e-Leg](https://www.elegislation.gov.hk/hk/cap59AF)｜[LD list](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                     ["Cap. 59Z FIU (Safety Officers and Safety Supervisors) Regulations", "Undertakings required to employ RSOs / safety supervisors; registration criteria.", "[e-Leg](https://www.elegislation.gov.hk/hk/cap59Z)｜[LD guide](https://www.labour.gov.hk/tc/faq/oshq8_whole.html)"],
                     ["Cap. 509A OSH (Display Screen Equipment) Regulation", "Workstation environment and risk assessment for DSE work.", "[LD list](https://www.labour.gov.hk/tc/legislat/contentB3.htm)"],
                 ])),
            ],
        },
        {
            "h": T("📢 重要修例:《2023年職業安全及健康(修訂)條例》",
                   "📢 Key amendment: OSH (Miscellaneous Amendments) Ordinance 2023"),
            "blocks": [
                ("p", T("2023年4月28日生效,大幅提高職安違例的最高罰則(可公訴罪行最高罰款1,000萬元及監禁2年),並賦權法庭命令違者改善。",
                        "In force 28 Apr 2023; greatly raises maximum penalties (up to HK$10M fine and 2 years' imprisonment on indictment) and allows courts to order remediation.")),
                ("src", T("來源:[勞工處修例專頁](https://www.labour.gov.hk/tc/news/Amendment_Ordinance.htm)。",
                          "Source: [LD amendment page](https://www.labour.gov.hk/tc/news/Amendment_Ordinance.htm).")),
            ],
        },
        {
            "h": T("執行與罰則", "Enforcement and penalties"),
            "blocks": [
                ("table",
                 T(["機制／罰則", "說明"], ("Mechanism / penalty", "Description")),
                 T(
                     [("敦促改善通知書(Improvement Notice)", "勞工處職安人員發現違例,可發通知書飭令在限期內糾正。"),
                      ("暫時停工通知書(Suspension Notice)", "對有即時危險的活動/設備,可飭令暫時停工直至改善。"),
                      ("刑事檢控", "違例可被檢控。2023年修例後,可公訴罪行最高罰款1,000萬元及監禁2年;循簡易程序的罰款上限亦大幅提高(按不同條文而定)。"),
                      ("巡查及意外調查", "勞工處職業安全及健康部巡查工作場所;致命/嚴重意外會展開調查,並透過「職安警示」向業界發布個案及改善要點。")],
                     [("Improvement Notice", "OSH officers may serve notices requiring rectification within a deadline."),
                      ("Suspension Notice", "Activities/plant posing imminent danger may be suspended until remedied."),
                      ("Prosecution", "Post-2023 amendment: indictable offences up to HK$10M fine and 2 years' imprisonment; summary fine levels also substantially raised (varies by provision)."),
                      ("Inspections & accident investigations", "LD OSH Division inspects workplaces; fatal/serious accidents are investigated and publicised via “OSH Alerts”.")]
                 ),
             ),
                ("src", T("來源:勞工處職安法例專頁、[2023修例專頁](https://www.labour.gov.hk/tc/news/Amendment_Ordinance.htm);具體罰款額按各條文,以官方為準。",
                          "Sources: LD legislation pages and the [2023 amendment page](https://www.labour.gov.hk/tc/news/Amendment_Ordinance.htm); exact fine levels vary by provision — official texts prevail.")),
            ],
        },
        {
            "h": T("安全管理制度(第59AF章)與14項元素", "Safety Management System (Cap. 59AF) — 14 elements"),
            "blocks": [
                ("p", T("第59AF章《工廠及工業經營(安全管理)規例》要求指定工業經營(如大型承建商)建立**含14項元素的安全管理制度**,元素數目按僱員人數而定;達到指標者須就制度進行**安全審核**(註冊安全審核員)或**安全查核**。",
                        "Cap. 59AF FIU (Safety Management) Regulation requires specified undertakings (e.g. large contractors) to implement a **14-element safety management system**, with the number of elements scaled to worker headcount; larger undertakings must undergo periodic **safety audits** (registered safety auditors) or safety reviews.")),
                ("ul", T(
                    ["14項元素包括:**安全政策、安全職責架構、安全訓練、內部安全規則、安全委員會、危險情況視察計劃、工作危險分析、個人防護計劃、意外事故調查、緊急事故應變、採購安全、承辦商評估及管制、評估檢討及審核**等(完整清單見規例附表及《安全管理工作守則》)。",
                     "承建商/東主須承擔安全責任,部分職責可下放予經理及管工,但責任仍在東主。"],
                    ["The 14 elements include: **safety policy, safety structure, safety training, in-house safety rules, safety committee, inspection programme for hazardous conditions, job hazard analysis, personal protection programme, accident investigation, emergency preparedness, safety in purchasing, subcontractor evaluation & control, evaluation/review/audit**, etc. (full list in the Schedule and the COP).",
                     "Proprietors/contractors bear the duties; some may be delegated to managers/forepersons, but responsibility remains with the proprietor."])),
                ("src", T("來源:[第59AF章法例](https://www.elegislation.gov.hk/hk/cap59AF)、[《安全管理工作守則》(SM.pdf)](https://www.labour.gov.hk/tc/public/pdf/os/B/SM.pdf)、[職安局安全管理專頁](https://www.oshc.org.hk/tchi/main/hot/SMS/)。",
                          "Sources: [Cap. 59AF text](https://www.elegislation.gov.hk/hk/cap59AF), [COP on Safety Management (SM.pdf)](https://www.labour.gov.hk/tc/public/pdf/os/B/SM.pdf), [OSHC SMS corner](https://www.oshc.org.hk/tchi/main/hot/SMS/).")),
            ],
        },
        {
            "h": T("其他相關法例", "Other related ordinances"),
            "blocks": [
                ("ul", T([
                    "第282章《僱員補償條例》— 工傷補償([勞工處介紹](https://www.labour.gov.hk/tc/legislat/content1.htm))",
                    "第295章《危險品條例》— 危險品儲存及牌照(消防處執行)",
                    "第572章《消防安全(建築物)條例》、第502章《消防安全(商業處所)條例》— 見「防火安全」",
                    "全部法例:[電子版香港法例](https://www.elegislation.gov.hk)",
                ], [
                    "Cap. 282 Employees' Compensation Ordinance ([LD page](https://www.labour.gov.hk/tc/legislat/content1.htm))",
                    "Cap. 295 Dangerous Goods Ordinance (enforced by FSD)",
                    "Cap. 572 Fire Safety (Buildings) / Cap. 502 Fire Safety (Commercial Premises) — see Fire Safety tab",
                    "All ordinances: [HK e-Legislation](https://www.elegislation.gov.hk)",
                ])),
                ("src", T("⚖️ 法律條文如有修訂,一律以官方最新公佈為準。",
                          "⚖️ Always rely on the latest official texts.")),
            ],
        },
    ],
}

# ---------------------------------------------------------------- 工作守則
SECTIONS["cop"] = {
    "title": T("📘 工作守則(Codes of Practice)", "📘 Codes of Practice (COP)"),
    "intro": T(
        "工作守則由**勞工處處長**根據職安法例(第509章/第59章及其規例)發出,就安全工作方法提供**實務指引**。特點:①違反守則**本身並非罪行**;②但在法律程序中,守則可被接納為**證據**,用以證明或否定是否違反有關安全法例;③與「指引」(advisory,純建議)不同,守則具半法定地位。所有守則可於勞工處網頁**免費下載**,或於職業安全及健康部各辦事處免費索取。",
        "COPs are issued by the **Commissioner for Labour** under OSH law as practical guidance. Key points: ① breaching a COP is **not itself an offence**; ② yet COPs are **admissible in evidence** in proceedings to prove or disprove breaches of safety law; ③ unlike “guidelines” (purely advisory), COPs carry quasi-statutory status. All COPs are free to download from LD or collect at OSH offices."),
    "panels": [
        {
            "h": T("官方工作守則全清單(可免費下載)", "Complete official COP list (free downloads)"),
            "blocks": [
                ("table",
                 T(["工作守則", "主題／適用", "官方PDF"],
                   ("Code of Practice", "Topic / applies to", "Official PDF")),
                 T([
                     ["安全管理工作守則", "第59AF章安全管理制度:14項元素的建立、推行及審核/查核。", "[SM.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/SM.pdf)"],
                     ["密閉空間工作的安全與健康工作守則", "評估、許可證制度、氣體監測、監視人。", "[spacec.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/spacec.pdf)"],
                     ["金屬棚架工作安全守則", "金屬棚架的搭建、改動及拆卸。", "[MS.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/MS.pdf)"],
                     ["竹棚架工作安全守則", "竹棚架搭建及拆卸(另附2026年第1/2026號增編)。", "[Bamboo.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/Bamboo.pdf)"],
                     ["工作安全及健康守則(沿岸的陸上建築—防止工人墮下)", "高處工作防墮措施。", "[fall.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/fall.pdf)"],
                     ["安全使用和操作吊船工作守則", "吊船(懸吊式工作台)安全操作。", "[platform.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/platform.pdf)"],
                     ["安全使用塔式起重機工作守則", "塔吊的安裝、操作及拆卸。", "[crane.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/crane.pdf)"],
                     ["安全使用流動式起重機工作守則", "流動吊機安全使用。", "[PDF](https://www.labour.gov.hk/tc/public/pdf/os/B/CoP_for_Mobile_Cranes_TC.pdf)"],
                     ["安全使用挖土機工作守則", "挖土機安全操作。", "[excavator.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/excavator.pdf)"],
                     ["貨櫃場內機械處理安全工作守則", "貨櫃處理業機械作業(2022第二版)。", "[PDF](https://www.labour.gov.hk/tc/public/os/B/CoP(MHSCY)_2022(2nd%20edition)_TChi.pdf)"],
                     ["工作守則:氣體焊接及火焰切割工作的安全與健康", "焊接切割防火防爆、氣樽處理。", "[welding2.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/welding2.pdf)"],
                     ["工作守則:手工電弧焊接工作的安全與健康", "電焊安全、觸電防護、眼部保護。", "[welding3.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/welding3.pdf)"],
                     ["工作守則:石棉工作的安全與健康", "石棉拆除及處理、暴露量認可方法(第964號公告)。", "[asbestos.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/asbestos.pdf)"],
                     ["工作守則:工業潛水的工作安全與健康", "潛水作業計劃、潛水主任及潛水員要求。", "[diving.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/diving.pdf)"],
                     ["工作安全守則(升降機及自動梯)", "升降機/自動梯工程安全。", "[lift.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/lift.pdf)"],
                     ["惡劣天氣及「極端情況」下工作守則", "8號及以上颱風信號、黑雨及極端情況下的工作安排。", "[於守則清單頁下載](https://www.labour.gov.hk/tc/public/content2_8b.htm)"],
                 ], [
                     ["Safety Management", "14-element SMS under Cap. 59AF — implementation and audits/reviews.", "[SM.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/SM.pdf)"],
                     ["Safety & Health in Confined Spaces", "Assessment, permit-to-work, gas monitoring, standby person.", "[spacec.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/spacec.pdf)"],
                     ["Metal Scaffolding Safety", "Erection, alteration and dismantling.", "[MS.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/MS.pdf)"],
                     ["Bamboo Scaffolding Safety", "Bamboo scaffold work (with Addendum No.1/2026).", "[Bamboo.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/Bamboo.pdf)"],
                     ["S&H in Construction on Land along the Coast — Fall Prevention", "Work-at-height fall protection.", "[fall.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/fall.pdf)"],
                     ["Safe Use & Operation of Suspended Platforms", "Gondola safety.", "[platform.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/platform.pdf)"],
                     ["Safe Use of Tower Cranes", "Erection, operation and dismantling of tower cranes.", "[crane.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/crane.pdf)"],
                     ["Safe Use of Mobile Cranes", "Mobile crane safety.", "[PDF](https://www.labour.gov.hk/tc/public/pdf/os/B/CoP_for_Mobile_Cranes_TC.pdf)"],
                     ["Safe Use of Excavators", "Excavator safety.", "[excavator.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/excavator.pdf)"],
                     ["Safe Operation of Container Handling Machinery", "Container terminals (2022, 2nd ed.).", "[PDF](https://www.labour.gov.hk/tc/public/os/B/CoP(MHSCY)_2022(2nd%20edition)_TChi.pdf)"],
                     ["Gas Welding & Flame Cutting", "Fire/explosion prevention, cylinder handling.", "[welding2.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/welding2.pdf)"],
                     ["Manual Electric Arc Welding", "Electrical and eye protection.", "[welding3.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/welding3.pdf)"],
                     ["Asbestos Work", "Asbestos removal/handling; approved method (GN 964).", "[asbestos.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/asbestos.pdf)"],
                     ["Industrial Diving", "Diving operations, supervisor and diver requirements.", "[diving.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/diving.pdf)"],
                     ["Lift & Escalator Works", "Lift/escalator works safety.", "[lift.pdf](https://www.labour.gov.hk/tc/public/pdf/os/B/lift.pdf)"],
                     ["Adverse Weather & 'Extreme Conditions'", "Arrangements during T8+, black rainstorm and 'extreme conditions'.", "[via COP list page](https://www.labour.gov.hk/tc/public/content2_8b.htm)"],
                 ])),
                ("src", T("📖 來源(官方):勞工處「乙部:工作守則」完整清單 [www.labour.gov.hk/tc/public/content2_8b.htm](https://www.labour.gov.hk/tc/public/content2_8b.htm);清單會因應新守則/增編更新,以官方頁為準。",
                          "📖 Source (official): LD “Part B: Codes of Practice” [content2_8b.htm](https://www.labour.gov.hk/tc/public/content2_8b.htm); the list updates as new COPs/addenda are issued.")),
            ],
        },
        {
            "h": T("守則、指引與法例的分別", "COP vs guidance vs law"),
            "blocks": [
                ("table",
                 T(["類型", "法律性質", "例子"], ("Type", "Legal nature", "Examples")),
                 T(
                     [("法例及規例", "**強制**。違反即屬違法,可被檢控、罰款甚至監禁。", "第509章、第59章及其附屬規例。"),
                      ("工作守則(COP)", "本身非罪行,但法庭可引用作**證據**,判定有否違反相關法例的安全標準。", "安全管理工作守則、密閉空間守則等(上表)。"),
                      ("指引／小冊子", "純建議性質,協助合規的參考資料。", "勞工處[丙部:安全指引](https://www.labour.gov.hk/tc/public/content2_8c.htm)、職安局刊物。")],
                     [("Ordinances & regulations", "**Mandatory**. Breach is an offence: prosecution, fines, imprisonment.", "Cap. 509, Cap. 59 and subsidiary regulations."),
                      ("Codes of Practice", "Not an offence per se, but admissible as **evidence** of the safety standard.", "Safety Management, Confined Spaces COPs, etc."),
                      ("Guidelines / booklets", "Advisory references to help compliance.", "LD [Part C: Safety Guidelines](https://www.labour.gov.hk/tc/public/content2_8c.htm), OSHC publications.")]
                 ),
             ),
            ],
        },
        {
            "h": T("相關刊物", "Related publications"),
            "blocks": [
                ("p", T("勞工處另出版大量指引及小冊子(屬建議性質),並設季度《職業安全及健康訓練課程手冊》;職安局亦有豐富教材。除「乙部:守則」外,可一併瀏覽「丙部:安全指引」。",
                        "LD also publishes advisory guidance booklets and a quarterly OSH training courses handbook; OSHC provides extensive materials. Besides “Part B: COPs”, also see “Part C: Safety Guidelines”.")),
                ("src", T("來源:[勞工處出版物(乙部:守則)](https://www.labour.gov.hk/tc/public/content2_8b.htm)｜[丙部:安全指引](https://www.labour.gov.hk/tc/public/content2_8c.htm)｜[職安局 OSHC](https://www.oshc.org.hk)。",
                          "Sources: [LD publications Part B](https://www.labour.gov.hk/tc/public/content2_8b.htm)｜[Part C](https://www.labour.gov.hk/tc/public/content2_8c.htm)｜[OSHC](https://www.oshc.org.hk).")),
            ],
        },
    ],
}

# ---------------------------------------------------------------- PPE
SECTIONS["ppe"] = {
    "title": T("🧤 個人防護裝備(PPE)", "🧤 Personal Protective Equipment (PPE)"),
    "intro": T(
        "PPE 是在**消除、替代、工程控制、行政控制**之後的最後一道防線。僱主須先做風險評估,免費提供合適PPE並確保正確使用(第509章及第59章一般責任)。",
        "PPE is the LAST line of defence after elimination, substitution, engineering and administrative controls. Employers must risk-assess, provide suitable PPE free of charge and ensure proper use (general duties under Cap. 509 & 59)."),
    "panels": [
        {
            "h": T("各部位防護裝備與常見國際標準", "PPE types & common standards"),
            "blocks": [
                ("table",
                 T(["部位", "裝備", "常見標準", "選用／檢查要點"],
                   ["Body part", "Equipment", "Common standards", "Selection / checks"]),
                 T([
                     ["頭部", "安全帽", "EN 397／ANSI Z89.1／GB 2811", "檢查外殼裂紋及內襯;按製造商建議定期更換。"],
                     ["眼睛", "護目鏡／面罩", "EN 166／ANSI Z87.1", "按風險選防衝擊、防化學飛濺或防焊接弧光。"],
                     ["聽覺", "耳塞／耳罩", "EN 352", "噪音達法例行動水平(約85–90 dB(A),以現行法例為準)須採取措施;核對降噪值。"],
                     ["呼吸", "防塵口罩／呼吸器", "EN 149(FFP1/2/3)／NIOSH N95", "貼合測試;防有機蒸氣須用活性碳濾罐;缺氧環境須用氣瓶式。"],
                     ["手部", "安全手套", "EN 388(機械)／EN 374(化學)", "化學品手套須查滲透時間;轉動機械旁嚴禁戴手套。"],
                     ["腳部", "安全鞋", "EN ISO 20345(SB/S1/S3)", "鋼頭+防穿刺底(S3);濕滑環境選防滑底。"],
                     ["防墮", "全身安全帶+吸震帶+防墮器", "EN 361／EN 355／EN 360", "「100%掛靠」雙鉤交替;防懸吊創傷;使用前逐件檢查。"],
                     ["可見度", "反光衣", "EN ISO 20471", "夜間或車輛繁忙環境必須。"],
                 ], [
                     ["Head", "Safety helmet", "EN 397 / ANSI Z89.1 / GB 2811", "Check shell and harness; replace per manufacturer's guidance."],
                     ["Eyes", "Goggles / face shield", "EN 166 / ANSI Z87.1", "Choose impact / chemical / welding-rated protection."],
                     ["Hearing", "Ear plugs / muffs", "EN 352", "Required at statutory action levels (~85–90 dB(A)); check SNR/NRR."],
                     ["Breathing", "Masks / respirators", "EN 149 (FFP1/2/3) / NIOSH N95", "Fit test; organic-vapour cartridges for solvents; supplied-air in oxygen-deficient spaces."],
                     ["Hands", "Gloves", "EN 388 (mechanical) / EN 374 (chemical)", "Check permeation data; never wear near rotating machinery."],
                     ["Feet", "Safety boots", "EN ISO 20345 (SB/S1/S3)", "Toe cap + midsole penetration (S3); slip-resistant soles."],
                     ["Fall protection", "Full harness + energy absorber + fall arrester", "EN 361 / EN 355 / EN 360", "100% tie-off with twin lanyards; plan suspension-trauma rescue; inspect before use."],
                     ["Visibility", "Hi-vis vest", "EN ISO 20471", "Mandatory at night or near traffic."],
                 ])),
                ("src", T("標準以各標準機構最新版本為準。官方參考:職安局[個人防護裝備專頁](https://www.oshc.org.hk/tchi/main/hot/ppe/)｜勞工處[丙部:安全指引(含化學品PPE指引)](https://www.labour.gov.hk/tc/public/content2_8c.htm)。",
                          "Standards per latest editions. Official references: OSHC [PPE corner](https://www.oshc.org.hk/tchi/main/hot/ppe/)｜LD [Part C: Safety Guidelines (incl. chemical PPE)](https://www.labour.gov.hk/tc/public/content2_8c.htm).")),
            ],
        },
        {
            "h": T("PPE 管理六步曲", "Six steps of PPE management"),
            "blocks": [
                ("ol", T([
                    "**識別危害** — 風險評估確定所需防護",
                    "**選型** — 按標準選合規產品,注意認證標記",
                    "**試用** — 尺碼合身舒適,員工參與選擇",
                    "**培訓** — 正確佩戴、調整及拆卸方法",
                    "**檢查保養** — 使用前檢查、定期更換、清潔儲存",
                    "**紀錄監察** — 發放紀錄、監督使用、持續改善",
                ], [
                    "**Identify hazards** — risk assessment defines PPE needs",
                    "**Select** — certified products to standards",
                    "**Trial** — proper fit; involve workers",
                    "**Train** — donning, adjusting, doffing",
                    "**Inspect & maintain** — pre-use checks, replacement, storage",
                    "**Record & supervise** — issue logs, enforcement, improvement",
                ])),
            ],
        },
    ],
}

# ---------------------------------------------------------------- MSDS
SECTIONS["msds"] = {
    "title": T("🧪 化學品安全資料表(MSDS／SDS)", "🧪 Safety Data Sheets (MSDS / SDS)"),
    "intro": T(
        "MSDS 現國際通用名稱為 **SDS**,是化學品供應商／製造商編製的標準安全文件。香港跟隨**聯合國 GHS** 的16段格式;僱主按第509章一般責任須向僱員提供化學品危害資料、培訓及防護。",
        "MSDS is now internationally called **SDS** — the supplier's standardised safety document. Hong Kong follows the **UN GHS** 16-section format; employers must provide hazard information, training and protection (Cap. 509 duties)."),
    "ghs": T(["💥 爆炸物", "🔥 易燃物", "🟢 氧化物", "🫧 高壓氣體", "🧯 腐蝕性", "☠️ 急性毒性",
              "⚠️ 刺激／有害", "🫀 健康危害", "🌿 環境危害"],
             ["💥 Explosive", "🔥 Flammable", "🟢 Oxidising", "🫧 Gas under pressure", "🧯 Corrosive", "☠️ Acute toxicity",
              "⚠️ Irritant / harmful", "🫀 Health hazard", "🌿 Environmental hazard"]),
    "panels": [
        {
            "h": T("SDS 標準16段結構", "The 16 sections of an SDS"),
            "blocks": [
                ("table",
                 T(["段落", "內容"], ["Section", "Content"]),
                 T([
                     ["1", "化學品及企業標識"], ["2", "危險性概述(GHS分類及標籤元素)"], ["3", "成分／組成資料"],
                     ["4", "急救措施"], ["5", "消防措施"], ["6", "意外洩漏應急措施"],
                     ["7", "操作處置與儲存"], ["8", "接觸控制／個人防護"], ["9", "理化特性"],
                     ["10", "穩定性和反應性"], ["11", "毒理學資料"], ["12", "生態學資料"],
                     ["13", "廢棄處置"], ["14", "運輸資料"], ["15", "法規資料"], ["16", "其他資料(含編製日期)"],
                 ], [
                     ["1", "Identification of the substance and company"], ["2", "Hazards identification (GHS)"], ["3", "Composition / ingredients"],
                     ["4", "First-aid measures"], ["5", "Fire-fighting measures"], ["6", "Accidental release measures"],
                     ["7", "Handling and storage"], ["8", "Exposure controls / PPE"], ["9", "Physical and chemical properties"],
                     ["10", "Stability and reactivity"], ["11", "Toxicological information"], ["12", "Ecological information"],
                     ["13", "Disposal considerations"], ["14", "Transport information"], ["15", "Regulatory information"], ["16", "Other information (incl. revision date)"],
                 ])),
                ("src", T("格式依據:聯合國GHS／ISO 11014;香港參考勞工處及職安局化學品安全刊物。",
                          "Format per UN GHS / ISO 11014; HK references LD & OSHC chemical-safety publications.")),
            ],
        },
        {
            "h": T("使用 SDS 的要點", "Using SDS effectively"),
            "blocks": [
                ("ul", T([
                    "每種化學品進場前**先索取SDS**(供應商責任)",
                    "重點看第2段(危害)、第4段(急救)、第7段(儲存)、第8段(PPE)",
                    "核對第16段**編製／修訂日期**,過期版本要求更新",
                    "存檔讓員工可隨時查閱;配合標籤與化學品清單使用",
                ], [
                    "Obtain the SDS **before** any chemical enters site (supplier's duty)",
                    "Focus on §2 hazards, §4 first aid, §7 storage, §8 PPE",
                    "Check §16 **revision date**; request updates when outdated",
                    "Keep accessible; use with labels and a chemical inventory",
                ])),
                ("src", T("⚠️ 網上資料庫僅供參考,具體產品一律以供應商發出的SDS為準。查詢:[PubChem](https://pubchem.ncbi.nlm.nih.gov/)｜[職安局](https://www.oshc.org.hk)。",
                          "⚠️ Online databases are indicative only — the supplier's SDS prevails. Databases: [PubChem](https://pubchem.ncbi.nlm.nih.gov/)｜[OSHC](https://www.oshc.org.hk).")),
            ],
        },
    ],
}

# ---------------------------------------------------------------- AI/4S
SECTIONS["tech"] = {
    "title": T("🤖 AI／4S 安全智慧科技", "🤖 AI / 4S Smart-safety Technology"),
    "intro": T(
        "**4S = Site Safety Smart System(安全智慧工地系統)**。根據發展局《工務技術通告第3/2023號》,自2023年起造價超過3,000萬元的工務工程合約須採用4S,並逐步擴展至更多合約;建造業議會另設「4S標籤計劃」及資助。",
        "**4S = Site Safety Smart System**. Under DEVB Technical Circular (Works) No. 3/2023, public works contracts over HK$30M must adopt 4S since 2023, with wider coverage since; CIC runs a 4S Labelling Scheme and funding."),
    "panels": [
        {
            "h": T("4S 系統四大核心", "Four pillars of 4S"),
            "blocks": [
                ("table",
                 T(["核心", "內容"], ["Pillar", "Description"]),
                 T([
                     ["📍 智能定位", "智能安全帽／UWB定位標籤,實時掌握工人位置,進入危險區自動警報。"],
                     ["📹 AI 影像監察", "攝影機+AI識別未戴安全帽、進入吊運範圍、臨邊無圍封等高危行為。"],
                     ["🖥️ 中央監控平台", "工地實況儀表板、警報紀錄及數據分析,管理層即時督導。"],
                     ["🌐 環境感測", "氣體、噪音、微氣候(中暑風險)等感測器聯動警報。"],
                 ], [
                     ["📍 Smart positioning", "Smart helmets / UWB tags track workers in real time; auto-alerts on entering danger zones."],
                     ["📹 AI video analytics", "Cameras + AI detect missing helmets, entry into lifting zones, unprotected edges."],
                     ["🖥️ Central dashboard", "Live site dashboard, alert logs and analytics for management."],
                     ["🌐 Environmental sensing", "Gas, noise and heat-stress sensors with linked alerts."],
                 ])),
                ("src", T("來源:發展局[「廣泛應用4S 提升工地安全」局長隨筆](https://www.devb.gov.hk/tc/home/my_blog/index_id_1558.html)、[工務技術通告TC(W)第3/2023號](https://www.devb.gov.hk)(devb.gov.hk技術通告欄)｜建造業議會[4S標籤計劃](https://www.cic.hk)。",
                          "Sources: DEVB [blog “Extensive Adoption of 4S”](https://www.devb.gov.hk/tc/home/my_blog/index_id_1558.html), [TC(W) No. 3/2023](https://www.devb.gov.hk) (Technical Circulars section)｜CIC [4S Labelling Scheme](https://www.cic.hk).")),
            ],
        },
        {
            "h": T("AI 於職業安全的應用", "AI applications in OSH"),
            "blocks": [
                ("table",
                 T(["技術", "應用場景"], ["Technology", "Use cases"]),
                 T([
                     ["電腦視覺", "PPE穿戴偵測、危險區域入侵偵測、不安全行為自動警示。"],
                     ["物聯網 IoT", "密閉空間氣體監測、噪音／微氣候監測、機械振動監察。"],
                     ["可穿戴裝置", "智能安全帽、心率/體溫監測(防中暑)、跌倒偵測。"],
                     ["無人機 UAV", "高空／密閉空間巡查代替人手、棚架及外牆檢查。"],
                     ["BIM+數碼分身", "施工階段安全模擬、危險工序預演。"],
                     ["VR／AR 培訓", "沉浸式高空工作、密閉空間、火警應變訓練。"],
                     ["機械人／自動化", "機械人取代高危工序(噴漿、拆卸、管道檢測)。"],
                     ["AI 聊天助手", "即時查詢法例守則、風險評估草擬、安全文件輔助。"],
                 ], [
                     ["Computer vision", "PPE detection, danger-zone intrusion, unsafe-act alerts."],
                     ["IoT sensors", "Confined-space gas, noise / heat monitoring, machine vibration."],
                     ["Wearables", "Smart helmets, heart-rate / core-temperature (heat stress), fall detection."],
                     ["Drones (UAV)", "Aerial and confined-space inspection replacing manual entry."],
                     ["BIM + digital twin", "Construction-phase safety simulation and rehearsal."],
                     ["VR / AR training", "Immersive work-at-height, confined space, fire response drills."],
                     ["Robotics", "Robots replace high-risk tasks (spraying, demolition, pipe inspection)."],
                     ["AI assistants", "Instant Q&A on law/COP, draft risk assessments, document aid."],
                 ])),
            ],
        },
        {
            "h": T("推行提示", "Implementation tips"),
            "blocks": [
                ("ul", T([
                    "科技是**輔助**:仍須以風險評估和安全管理制度為本",
                    "注意個人資料私隱(影像／定位),參考[私隱專員公署](https://www.pcpd.org.hk)指引",
                    "先單點試行(如吊運區監察)→ 驗證成效 → 全面推廣",
                ], [
                    "Technology assists — risk assessment and SMS remain the foundation",
                    "Mind privacy of video / location data; see [PCPD](https://www.pcpd.org.hk) guidance",
                    "Pilot single use-cases first, verify results, then scale",
                ])),
            ],
        },
    ],
}

# ---------------------------------------------------------------- 防火
SECTIONS["fire"] = {
    "title": T("🔥 防火安全", "🔥 Fire Safety"),
    "intro": T(
        "消防法例由消防處執行;工作場所的火警危險亦受職安法例規管。消防裝置須由註冊承辦商每年至少檢查一次。",
        "Fire safety law is enforced by the Fire Services Department; workplace fire hazards also fall under OSH law. Fire service installations must be checked by Registered Contractors at least annually."),
    "panels": [
        {
            "h": T("消防法例", "Fire legislation"),
            "blocks": [
                ("table",
                 T(["法例", "重點"], ["Ordinance", "Key points"]),
                 T([
                     ["第572章《消防安全(建築物)條例》", "1987年3月1日或之後建成/重建的綜合用途及住用建築物:消防裝置、逃生途徑改善指令。"],
                     ["第502章《消防安全(商業處所)條例》", "訂明商業處所的防火保障措施。"],
                     ["第295章《危險品條例》", "危險品(石油氣、易燃液體等)儲存、運送及牌照。"],
                 ], [
                     ["Cap. 572 Fire Safety (Buildings) Ordinance", "FSIs and means-of-escape improvement directions for composite/residential buildings built or rebuilt on or after 1 Mar 1987."],
                     ["Cap. 502 Fire Safety (Commercial Premises) Ordinance", "Fire safety measures for prescribed commercial premises."],
                     ["Cap. 295 Dangerous Goods Ordinance", "Storage, conveyance and licensing of dangerous goods."],
                 ])),
                ("src", T("來源:[電子版香港法例](https://www.elegislation.gov.hk/hk/cap572)｜[消防處](https://www.fsd.gov.hk)。",
                          "Sources: [e-Legislation](https://www.elegislation.gov.hk/hk/cap572)｜[FSD](https://www.fsd.gov.hk).")),
            ],
        },
        {
            "h": T("滅火筒類型速查", "Extinguisher types"),
            "blocks": [
                ("table",
                 T(["火警類別", "燃燒物", "適用滅火筒", "切勿使用"],
                   ["Class", "Fuel", "Use", "Never use"]),
                 T([
                     ["A類", "固體(木、紙、布)", "水、AFFF泡沫、乾粉", "—"],
                     ["B類", "易燃液體(油、溶劑)", "泡沫、乾粉、CO₂", "水(蔓延火勢)"],
                     ["C類", "氣體(石油氣、天然氣)", "乾粉(先截斷氣源!)", "—"],
                     ["D類", "金屬(鎂、鈉)", "專用D類滅火劑", "水、CO₂"],
                     ["F／K類", "食用油脂(廚房)", "濕化學式(Wet Chemical)", "水(劇烈沸溢)"],
                     ["帶電設備", "電器火警", "CO₂、乾粉", "水、泡沫(導電)"],
                 ], [
                     ["Class A", "Solids (wood, paper, cloth)", "Water, AFFF foam, dry powder", "—"],
                     ["Class B", "Flammable liquids", "Foam, dry powder, CO₂", "Water (spreads fire)"],
                     ["Class C", "Flammable gas", "Dry powder (isolate supply first!)", "—"],
                     ["Class D", "Metals (Mg, Na)", "Specialist Class-D agent", "Water, CO₂"],
                     ["Class F/K", "Cooking oils", "Wet chemical", "Water (violent eruption)"],
                     ["Electrical", "Energised equipment", "CO₂, dry powder", "Water, foam (conductive)"],
                 ])),
            ],
        },
        {
            "h": T("火警應變口訣 R.A.C.E.", "Fire response: R.A.C.E."),
            "blocks": [
                ("ol", T([
                    "**R — Rescue** 救人:協助有需要人士撤離",
                    "**A — Alarm** 報警:按動火警鐘並致電999",
                    "**C — Contain** 遏止:關上防火門、截斷氣源電源",
                    "**E — Extinguish/Evacuate**:僅在火勢細小及有退路時用滅火筒,否則立即撤離",
                ], [
                    "**R — Rescue**: assist those in danger",
                    "**A — Alarm**: sound the fire alarm and call 999",
                    "**C — Contain**: close fire doors, isolate gas/power",
                    "**E — Extinguish/Evacuate**: only fight small fires with an escape route; otherwise evacuate",
                ])),
                ("src", T("來源:消防處防火守則及職安局教材;機構應自訂火警應變計劃並定期演練。",
                          "Sources: FSD fire-safety codes and OSHC materials; organisations must maintain and drill their own fire action plan.")),
            ],
        },
        {
            "h": T("工作場所防火檢查清單(節錄)", "Workplace fire checklist (excerpt)"),
            "blocks": [
                ("ul", T([
                    "☐ 走火通道暢通,防火門保持關閉、無上鎖",
                    "☐ 出口指示牌及應急照明正常",
                    "☐ 滅火筒有效期內,每年由註冊承辦商檢查",
                    "☐ 易燃品不超量存放於核准危險品倉",
                    "☐ 電線無破損、無亂接拖板、下班關電",
                    "☐ 員工知道兩條逃生路線及集合點;定期火警演練",
                ], [
                    "☐ Escape routes clear; fire doors closed and unlocked",
                    "☐ Exit signs and emergency lighting working",
                    "☐ Extinguishers in date; annual registered-contractor check",
                    "☐ Flammables within limits in licensed stores",
                    "☐ Wiring sound; no daisy-chained adapters; switch off after hours",
                    "☐ Staff know two escape routes and assembly point; regular drills",
                ])),
            ],
        },
    ],
}

# ---------------------------------------------------------------- 安全主任
SECTIONS["so"] = {
    "title": T("👷 註冊安全主任(RSO)", "👷 Registered Safety Officer (RSO)"),
    "intro": T(
        "根據**第59Z章《工廠及工業經營(安全主任及安全督導員)規例》**,指明類別工業經營(如大型建築地盤、船廠、貨櫃碼頭)東主須僱用註冊安全主任,協助視察工作環境、提出改善建議及推行安全管理制度。",
        "Under **Cap. 59Z FIU (Safety Officers and Safety Supervisors) Regulations**, specified industrial undertakings (large construction sites, shipyards, container terminals) must employ an RSO to inspect, advise and help implement the safety management system."),
    "panels": [
        {
            "h": T("註冊資格(概要)", "Registration criteria (summary)"),
            "blocks": [
                ("ul", T([
                    "持有**認可的安全學歷**(勞工處認可學位/文憑/職安局課程等)",
                    "具**認可的相關工作經驗**",
                    "向勞工處職業安全及健康部申請並獲批准註冊",
                    "詳細準則、認可課程及表格:[勞工處官方FAQ](https://www.labour.gov.hk/tc/faq/oshq8_whole.html)",
                ], [
                    "Recognised safety qualification (LD-accredited degree/diploma/OSHC courses)",
                    "Recognised relevant experience",
                    "Apply to LD OSH Branch and be registered",
                    "Full criteria, accredited courses and forms: [LD official FAQ](https://www.labour.gov.hk/tc/faq/oshq8_whole.html)",
                ])),
                ("src", T("查詢:荃灣西樓角路1-17號新領域廣場8樓｜☎️ 2151 3615｜✉️ dso_rst_2@labour.gov.hk(來源:勞工處/政府電話簿)",
                          "Enquiries: 8/F, Frontier Centre, 1-17 Tsuen Wan Yeung King Road｜☎️ 2151 3615｜✉️ dso_rst_2@labour.gov.hk (source: LD/Gov directory)")),
            ],
        },
        {
            "h": T("進修及行業組織", "Training and professional bodies"),
            "blocks": [
                ("ul", T([
                    "[職業安全健康局 OSHC](https://www.oshc.org.hk) — 認可安全課程、安全審核員課程",
                    "本地大學職業安全及健康學位/碩士課程",
                    "[建造業議會 CIC](https://www.cic.hk) — 平安卡等建造業安全培訓",
                    "[註冊安全主任協會 SRSO](https://www.srso.org.hk)",
                ], [
                    "[OSHC](https://www.oshc.org.hk) — accredited safety courses, safety auditor training",
                    "Local universities' OSH degrees / master's programmes",
                    "[CIC](https://www.cic.hk) — Green Card and construction safety training",
                    "[SRSO — Society of Registered Safety Officers](https://www.srso.org.hk)",
                ])),
            ],
        },
    ],
}

# ---------------------------------------------------------------- YouTube
SECTIONS["yt"] = {
    "title": T("▶️ YouTube 職安影片", "▶️ OSH Videos on YouTube"),
    "intro": T(
        "下方影片由**自動同步**官方播放清單(勞工處《職安警示》)及**網主精選**組成;另附官方頻道連結。",
        "Videos below are **auto-synced** from the official LD Safety Alert playlist plus owner picks; official channels linked."),
    "src": T("來源:YouTube — [職安局 OSHC](https://www.youtube.com/user/OSHC2009)、[CIC Channel](https://www.youtube.com/channel/UCsK1xjqkm-xHCZTe1E3B26Q)。",
             "Sources: YouTube — [OSHC](https://www.youtube.com/user/OSHC2009), [CIC Channel](https://www.youtube.com/channel/UCsK1xjqkm-xHCZTe1E3B26Q)."),
}

# ---------------------------------------------------------------- 會員
SECTIONS["member"] = {
    "title": T("👤 會員專區(預留)", "👤 Members' Area (reserved)"),
    "intro": T(
        "會員系統為**預留功能(留位)**:可註冊及登入,目前提供 Google Drive 資源庫入口及預留個人化欄位;日後可擴充收藏、報名、證書到期提醒等。示範用途,資料只儲存在本機容器,請勿輸入真實密碼。",
        "The membership system is a **reserved placeholder**: register and log in to access the Google Drive library and reserved personal features (collections, enrolments, certificate reminders later). Demo only — data stays in the app container; do not use a real password."),
}

# ---------------------------------------------------------------- 檔案庫
SECTIONS["files"] = {
    "title": T("📁 檔案資源庫(Google Drive)", "📁 File Library (Google Drive)"),
    "intro": T("網主的外部檔案庫,存放課程筆記、表格、指引等,按下方按鈕開啟:",
               "The owner's external library with notes, forms and guides — open via the button below:"),
    "src": T("內容由網主於 Google Drive 管理,與本站設定互相獨立。",
             "Managed by the owner on Google Drive, independent of this site's settings."),
}

# ---------------------------------------------------------------- 資訊來源
SECTIONS["sources"] = {
    "title": T("📚 資訊來源說明", "📚 Information Sources"),
    "intro": T(
        "本網**不自行生產任何官方資訊**:新聞、影片及統計全部來自下列官方來源並自動抓取;參考內容(法例簡介、PPE標準、防火知識等)均列明出處。每條新聞亦顯示其來源機構。",
        "This site **produces no official information**: news, videos and statistics are auto-fetched from the official sources below; reference content cites its sources, and every news item shows its origin."),
    "panels": [
        {
            "h": T("來源機構一覽", "Source organisations"),
            "blocks": [
                ("table",
                 T(["機構", "提供內容", "本網更新方式", "官方網址"],
                   ["Organisation", "Content", "How updated", "Website"]),
                 T([
                     ["香港特區政府**勞工處**(職安部)", "職安法例、守則、刊物、統計、註冊安全主任、新聞公報", "新聞公報RSS + 靜態連結", "[labour.gov.hk](https://www.labour.gov.hk)"],
                     ["政府新聞公報(政府新聞處)", "全政府部門新聞公報", "RSS + 關鍵字篩選", "[info.gov.hk](https://www.info.gov.hk)"],
                     ["香港政府新聞網", "頭條、法律及治安、施政新聞", "RSS", "[news.gov.hk](https://www.news.gov.hk)"],
                     ["香港電台 RTHK", "本地/國際新聞", "RSS + 關鍵字篩選", "[news.rthk.hk](https://news.rthk.hk)"],
                     ["星島頭條", "本地新聞(關鍵字篩選職安相關)", "RSS + 關鍵字篩選", "[stheadline.com](https://www.stheadline.com)"],
                     ["東方日報·東網 on.cc", "本地新聞(關鍵字篩選職安相關)", "網頁抓取(按月列表)", "[hk.on.cc](https://hk.on.cc)"],
                     ["中國**應急管理部**", "內地安全生產新聞", "網頁抓取", "[mem.gov.cn](https://www.mem.gov.cn)"],
                     ["美國 **OSHA**", "美國職安新聞發布", "網頁抓取", "[osha.gov](https://www.osha.gov)"],
                     ["英國 **HSE**", "英國職安新聞(新聞中心)", "RSS", "[hse.gov.uk](https://www.hse.gov.uk)"],
                     ["勞工處年報 × DATA.GOV.HK", "註冊安全主任歷年數目(2015起,年報章節)+ 安全主任/審核員統計(開放數據)", "年報頁解析 + XLSX 自動下載", "[年報存檔](https://www.labour.gov.hk/tc/public/AnnualReportArchived.htm)｜[數據集](https://data.gov.hk/tc-data/dataset/hk-ld-rstd-rstd-keystats)"],
                     ["香港天文台", "天氣警示(酷熱、颱風、暴雨)", "RSS", "[hko.gov.hk](https://www.hko.gov.hk)"],
                     ["YouTube(職安局/CIC)", "職安警示及安全培訓影片", "YouTube RSS", "[OSHC頻道](https://www.youtube.com/user/OSHC2009)"],
                 ], [
                     ["HK **Labour Department** (OSH)", "Legislation, COPs, publications, statistics, RSO, press releases", "Press RSS + static links", "[labour.gov.hk](https://www.labour.gov.hk)"],
                     ["HK Gov Press Releases (ISD)", "All-government press releases", "RSS + keyword filter", "[info.gov.hk](https://www.info.gov.hk)"],
                     ["HK Gov News", "Top stories, law and order, administration", "RSS", "[news.gov.hk](https://www.news.gov.hk)"],
                     ["RTHK", "Local / international news", "RSS + keyword filter", "[news.rthk.hk](https://news.rthk.hk)"],
                     ["Sing Tao Headline", "Local news (OSH-filtered)", "RSS + keyword filter", "[stheadline.com](https://www.stheadline.com)"],
                     ["Oriental Daily · on.cc", "Local news (OSH-filtered)", "HTML scrape (monthly index)", "[hk.on.cc](https://hk.on.cc)"],
                     ["China **MEM** (Emergency Management)", "Mainland work-safety news", "HTML scrape", "[mem.gov.cn](https://www.mem.gov.cn)"],
                     ["US **OSHA**", "US OSH news releases", "HTML scrape", "[osha.gov](https://www.osha.gov)"],
                     ["UK **HSE**", "UK OSH news (media centre)", "RSS", "[hse.gov.uk](https://www.hse.gov.uk)"],
                     ["HK **Labour Department** annual reports × DATA.GOV.HK", "RSO numbers by year (2015–, from AR chapters) + RSO/auditor statistics (open data)", "AR page parsing + XLSX auto-download", "[AR archive](https://www.labour.gov.hk/tc/public/AnnualReportArchived.htm)｜[dataset](https://data.gov.hk/tc-data/dataset/hk-ld-rstd-rstd-keystats)"],
                     ["HK Observatory", "Weather warnings (heat, typhoon, rainstorm)", "RSS", "[hko.gov.hk](https://www.hko.gov.hk)"],
                     ["YouTube (OSHC/CIC)", "Safety alerts and training videos", "YouTube RSS", "[OSHC channel](https://www.youtube.com/user/OSHC2009)"],
                 ])),
            ],
        },
        {
            "h": T("⚠️ 免責聲明", "⚠️ Disclaimer"),
            "blocks": [
                ("ul", T([
                    "本網為**非官方**資訊整合平台,與香港特區政府或任何機構無關。",
                    "所有資訊僅供參考;法律、技術及統計事宜一律**以官方來源最新公佈為準**。",
                    "自動抓取的新聞標題及連結版權屬原本機構;點擊連結即前往原文。",
                    "「工傷新聞」為關鍵字自動分類,可能遺漏或誤分,不作官方統計用途。",
                    "會員系統為示範用途,請勿輸入真實個人資料或密碼。",
                ], [
                    "This is an **unofficial** aggregator, unaffiliated with the HKSAR Government or any organisation.",
                    "For reference only; legal, technical and statistical matters follow the latest official publications.",
                    "Headlines and links belong to their original publishers.",
                    "'Injury news' is keyword-classified and may miss or mis-tag items — not official statistics.",
                    "The membership system is a demo — do not enter real personal data or passwords.",
                ])),
            ],
        },
    ],
}

# ---------------------------------------------------------------- 新聞頁
SECTIONS["news"] = {
    "title": T("📰 最新 OSH 資訊(自動更新)", "📰 Latest OSH News (auto-updated)"),
    "intro": T(
        "由本站腳本自動抓取官方來源(政府新聞公報、政府新聞網、香港電台、中國應急管理部、美國OSHA、英國HSE),**每條均標明來源**;點擊標題前往原文。",
        "Auto-fetched from official sources (HK Gov press releases, news.gov.hk, RTHK, China MEM, US OSHA, UK HSE) — **every item cites its source**; click a headline for the original."),
}

SECTIONS["accident"] = {
    "title": T("🚑 工傷／工作意外新聞(自動更新)", "🚑 Work-injury / Accident News (auto-updated)"),
    "intro": T("以下為關鍵字自動分類的意外相關報道,詳見分類說明。",
               "Keyword-classified accident reports — see the classification note."),
}
