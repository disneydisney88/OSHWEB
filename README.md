# 香港職業安全資訊網 HK OSH Information Portal

非官方一站式香港職業安全資訊平台:整合**勞工處職安**官方資訊、法例、工作守則(COP)、
個人防護裝備(PPE)、化學品安全資料(MSDS/SDS)、AI／4S 安全智慧科技、香港・內地・海外
OSH 最新資訊、工傷新聞、防火安全、註冊安全主任資訊及**人數統計**,全部**自動更新**並
**逐項列明資訊來源**。支援**繁體中文／简体中文／English** 三語。

---

## 🚀 網上部署(Streamlit Community Cloud)

1. 本專案已推送至 GitHub:`https://github.com/disneydisney88/OSHWEB`
   *(注意:repo 須為 **Public**,否則 Community Cloud 會出現 "You can only have one private app per workspace" 錯誤)*
2. 開啟 <https://share.streamlit.io/deploy>
   - Repository:`disneydisney88/OSHWEB`
   - Branch:`main`
   - **Main file path:`streamlit_app.py`**
3. 按 Deploy,約 2-3 分鐘後即獲得 `https://oshweb-xxxx.streamlit.app` 網址。

## 🔒 網主後台(後門登入)

- 側欄底部「**🔒 網主後台登入**」,登入後出現「**⚙️ 網主設定**」頁,可管理:
  - 📢 主頁公告(新增/停用/刪除)
  - 🎬 YouTube 影片(網主精選影片、自選影片清單)
  - 🔗 主頁自訂快速連結
  - 🔑 更改管理員密碼
  - 👥 查看會員名單
  - 💾 設定匯出/匯入(JSON 備份)
- **預設密碼:`oshweb-admin`** — 請立即在後台更改,或在 Streamlit Cloud
  「Settings → Secrets」加入:
  ```toml
  ADMIN_PASSWORD = "你的強密碼"
  ```
- ⚠️ Streamlit Cloud 檔案系統屬暫存,重新部署後檔案型設定可能還原;請常用
  「匯出設定 JSON」備份。

## 👤 會員專區(留位)

側欄「👤 會員專區」提供註冊/登入(示範級,密碼以 SHA-256 儲存於 `data/members.json`),
現有功能:Google Drive 檔案資源庫入口;
預留擴充:收藏、課程報名、證書到期提醒。**請勿輸入真實密碼。**

## 📁 檔案資源庫

[Google Drive 資料夾](https://drive.google.com/drive/folders/17fBRgBi7aVPOJ7Il-nFBU0fMWKIlJ7oc?usp=sharing)
已接入主頁、會員專區及「檔案資源庫」頁。

---

## 🔄 自動更新機制(三重)

| 機制 | 適用 | 說明 |
| --- | --- | --- |
| **即時快取** | Streamlit 版 | 新聞/統計每小時自動重抓(`st.cache_data(ttl=3600)`);側欄「🔄 立即更新資料」可即時強制重抓 |
| **GitHub Actions** | repo | `.github/workflows/update-data.yml` 每日 07:30(香港)自動執行 `scripts/update_data.py` 並 commit 最新 `data/*.json`,首次部署即有資料 |
| **本機排程** | 靜態版 | 見下方 Windows/cron 設定 |

### 資料來源(全部列明於站內「資訊來源」頁)

政府新聞公報(info.gov.hk RSS)、政府新聞網(news.gov.hk RSS)、香港電台(RTHK RSS)、
中國應急管理部(網頁抓取)、美國 OSHA(網頁抓取)、英國 HSE(新聞中心 RSS)、
勞工處開放數據:註冊安全主任統計(XLSX 自動下載)、香港天文台天氣警示(RSS)、
YouTube 職安警示播放清單(RSS)。

## 🤖 自動化功能明細

| 功能 | 運作方式 |
| --- | --- |
| **開站自動更新** | 每個瀏覽 session 首次載入即強制重抓全部來源(約30-60秒,有進度提示);其後每30分鐘自動重抓;側欄按鈕可即時重抓 |
| **法例變更監察** | 每次更新時對勞工處[修例專頁](https://www.labour.gov.hk/tc/news/Amendment_Ordinance.htm)及[法例一覽](https://www.labour.gov.hk/tc/legislat/contentB3.htm)計算內容雜湊,有變更即在主頁顯示「⚖️ 法例有更新」;網主於後台確認後清除警示 |
| **月度工傷PDF報告** | 每月1日 GitHub Actions 自動彙總上月工傷新聞成 PDF 存入 `reports/`;站內「工傷新聞」頁亦可即時生成下載 |
| **AI 職安助手** | 「🤖 AI 職安助手」頁:以 GLM(OpenAI兼容接口)回答職安問題,檢索範圍為本站法例/守則/PPE/MSDS/防火/安全主任內容並列明參考章節 |

### AI 助手設定(Streamlit Cloud → Settings → Secrets)

```toml
LLM_API_KEY = "你的GLM金鑰"            # 必填,https://open.bigmodel.cn 申請
LLM_MODEL = "glm-4-flash"              # 可選,預設 glm-4-flash(免費)
LLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"   # 可選,預設 GLM;可換任何 OpenAI 兼容接口
```

### 線上監控(UptimeRobot 免費)

1. 到 <https://uptimerobot.com> 免費註冊(50個監測點、5分鐘間隔)。
2. 「Add New Monitor」→ Monitor Type:**HTTP(s)** → Friendly Name:`OSHWEB` →
   URL:`https://klchoyhkosh.streamlit.app`(換成你的實際網址)→ interval 5 分鐘。
3. 「Alert Contacts To Notify」加入你的 Email;網站掛線/恢復會自動收到通知。
4. 建議同時加一個 **Keyword** 監測(關鍵字填 `香港職業安全資訊網`),防止「頁面開到但應用壞掉」的情況。

## 💻 本機執行

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py        # Streamlit 版(建議)
# 或靜態版:
python scripts/serve.py               # http://127.0.0.1:8080(啟動時自動更新資料)
python scripts/update_data.py         # 單獨更新 data/*.json(只用量標準庫)
```

### Windows 定時自動更新(靜態版)

```bat
schtasks /Create /TN "HKOSH更新" /SC DAILY /ST 07:30 /TR "python C:\path\to\hk-osh-portal\scripts\update_data.py"
```

### macOS / Linux cron

```bash
30 7 * * * /usr/bin/python3 /path/to/hk-osh-portal/scripts/update_data.py
```

## 📂 專案結構

```
streamlit_app.py      Streamlit 主應用(三語、後台、會員、YouTube)
content.py            三語內容(繁中原文/英文翻譯/簡中自動轉換 zhconv)
index.html + css/ + js/   純靜態版(可配合 scripts/serve.py)
scripts/update_data.py    資料抓取核心(RSS/HTML/XLSX,只用量標準庫)
scripts/serve.py          靜態版本機伺服器(含 /api/refresh)
data/news.json            最新資訊(自動生成,亦 committed 作後備)
data/rso_stats.json       安全主任統計(自動生成)
.github/workflows/        每日自動更新數據
```

## 📚 主要資訊來源

勞工處 labour.gov.hk(法例、[工作守則清單](https://www.labour.gov.hk/tc/public/content2_8b.htm)、
[安全主任註冊](https://www.labour.gov.hk/tc/faq/oshq8_whole.html))、
[電子版香港法例](https://www.elegislation.gov.hk)、職安局 oshc.org.hk、
消防處 fsd.gov.hk、發展局 devb.gov.hk、建造業議會 cic.hk、
應急管理部 mem.gov.cn、OSHA、HSE、ILO、DATA.GOV.HK。

## ⚠️ 免責聲明

本網為**非官方**資訊整合平台,與香港特區政府或任何機構無關;所有資訊僅供參考,
法律、技術及統計事宜一律以官方來源最新公佈為準。「工傷新聞」為關鍵字自動分類,
不作官方統計用途。會員系統為示範用途。
