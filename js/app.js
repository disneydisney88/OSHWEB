/* 香港職業安全資訊網 — 前端邏輯 */
"use strict";

const $ = (sel, root) => (root || document).querySelector(sel);
const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

let NEWS = null;   // data/news.json
let RSO = null;    // data/rso_stats.json

/* ---------------- 頁籤路由 ---------------- */
function showSection(id) {
  $$(".tab-section").forEach(s => { s.hidden = s.id !== id; });
  $$(".nav-link").forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + id));
  window.scrollTo({ top: 0 });
}

function initRouter() {
  const route = () => {
    const id = (location.hash || "#home").slice(1);
    showSection(document.getElementById(id) ? id : "home");
  };
  window.addEventListener("hashchange", route);
  route();
}

/* ---------------- 工具 ---------------- */
function fmtDate(d) {
  if (!d) return "—";
  const m = String(d).match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${m[1]}/${m[2]}/${m[3]}` : d;
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}

/* ---------------- 新聞渲染 ---------------- */
function newsItemHTML(it, compact) {
  const acc = it.category === "accident";
  const badge = acc ? '<span class="badge accident">工傷/意外</span>' : "";
  const src = `<span class="badge src-${esc(it.source_id)}">${esc(shortSrc(it.source_label))}</span>`;
  const sum = (!compact && it.summary) ? `<div class="news-meta">${esc(it.summary.slice(0, 90))}</div>` : "";
  return `<div class="news-item${compact ? " compact" : ""}">
    <span class="news-date">${fmtDate(it.date || it.fetched)}</span>
    <div class="news-body">
      <a class="news-title" href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.title)}</a>
      <div class="news-meta">${src}${badge}<span>來源：${esc(it.source_label)}</span></div>
      ${sum}
    </div>
  </div>`;
}

function shortSrc(label) {
  if (label.includes("新聞公報")) return "政府公報";
  if (label.includes("頭條")) return "政府新聞網";
  if (label.includes("法律及治安")) return "政府新聞網";
  if (label.includes("政府施政")) return "政府新聞網";
  if (label.includes("國際")) return "港台國際";
  if (label.includes("本地")) return "港台本地";
  if (label.includes("應急管理")) return "應急管理部";
  return label.slice(0, 6);
}

function renderNewsRegion(region, targetSel) {
  const el = $(targetSel);
  if (!NEWS) { el.innerHTML = fallbackHTML(); return; }
  const items = NEWS.items.filter(i => i.region === region).slice(0, 40);
  el.innerHTML = items.length
    ? items.map(i => newsItemHTML(i, false)).join("")
    : `<p class="muted">此分區暫無資料。請按「立即更新」或直接瀏覽來源網站（見「資訊來源」）。</p>`;
}

function fallbackHTML() {
  return `<div class="alert-box">⚠️ 未能載入 <code>data/news.json</code>。請先執行更新腳本：
  <code>python scripts/update_data.py</code>，或用 <code>python scripts/serve.py</code> 啟動本網站（會自動更新）。
  官方資訊請直接瀏覽 <a href="https://www.labour.gov.hk" target="_blank" rel="noopener">勞工處</a>。</div>`;
}

/* ---------------- 安全主任統計 ---------------- */
function renderRsoStats() {
  const tableEl = $("#rso-table"), chartEl = $("#rso-chart"), homeEl = $("#home-rso-latest");
  if (!RSO || !Array.isArray(RSO.rows) || !RSO.rows.length) {
    [tableEl, chartEl, homeEl].forEach(el => {
      if (el) el.innerHTML = '<p class="muted">暫未取得統計數據。執行更新腳本後會自動下載勞工處開放數據（XLSX）。</p>';
    });
    return;
  }
  const rows = RSO.rows.map(r => r.map(c => String(c).trim()));
  // 表格
  const thead = `<tr>${rows[0].map(h => `<th>${esc(h)}</th>`).join("")}</tr>`;
  const tbody = rows.slice(1).map(r =>
    `<tr>${r.map(c => `<td>${esc(c)}</td>`).join("")}</tr>`).join("");
  tableEl.innerHTML = `<div style="overflow-x:auto"><table class="tbl">${thead}${tbody}</table></div>`;

  // 圖表欄位:優先「安全主任人數」欄,否則最後一個數字欄
  let numCol = -1;
  for (let c = 0; c < rows[0].length; c++) {
    if (String(rows[0][c]).includes("安全主任") && String(rows[0][c]).includes("人數")) { numCol = c; break; }
  }
  if (numCol < 0) {
    for (let c = rows[0].length - 1; c >= 1; c--) {
      const vals = rows.slice(1).map(r => parseFloat(String(r[c]).replace(/,/g, "")));
      const ok = vals.filter(v => !isNaN(v)).length;
      if (ok >= Math.ceil(vals.length * 0.6)) { numCol = c; break; }
    }
  }
  if (numCol > 0) {
    const data = rows.slice(1)
      .map(r => ({ label: r[0], val: parseFloat(String(r[numCol]).replace(/,/g, "")) }))
      .filter(d => !isNaN(d.val))
      .slice(-12);
    const max = Math.max(...data.map(d => d.val)) || 1;
    chartEl.innerHTML = data.map(d => `
      <div class="bar-row">
        <span class="bar-label">${esc(d.label)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${(d.val / max * 100).toFixed(1)}%"></div></div>
        <span class="bar-val">${d.val.toLocaleString("en-US")}</span>
      </div>`).join("");
    const latest = data[data.length - 1];
    if (latest && homeEl) {
      homeEl.innerHTML = `${latest.val.toLocaleString("en-US")}<br><small>${esc(latest.label)}｜來源：勞工處</small>`;
    }
  }
}

/* ---------------- 資訊來源狀態表 ---------------- */
function renderSourceStatus() {
  const el = $("#src-status-table");
  if (!el) return;
  const feeds = [
    { id: "rso_stats", label: "註冊安全主任統計（勞工處開放數據）", method: "XLSX 下載解析", url: "https://www.labour.gov.hk/datagovhk/resource/rstd/rstd-keystats_tc.xlsx", status: RSO ? "ok" : "未取得", count: RSO ? RSO.rows.length + " 行" : "0" },
  ].concat(NEWS ? NEWS.sources.map(s => ({
    id: s.id, label: s.label, method: s.method, url: s.url, status: s.status, count: s.count + " 條"
  })) : []);
  el.innerHTML = `<div style="overflow-x:auto"><table class="tbl">
    <thead><tr><th>來源</th><th>方式</th><th>最近抓取</th><th>新增</th><th>狀態</th><th>連結</th></tr></thead>
    <tbody>${feeds.map(f => `<tr>
      <td>${esc(f.label)}</td><td>${esc(f.method)}</td>
      <td>${esc(NEWS ? NEWS.generated_at : "—")}</td><td>${esc(f.count)}</td>
      <td>${String(f.status).startsWith("ok") ? "✅ 正常" : "⚠️ " + esc(f.status)}</td>
      <td><a href="${esc(f.url)}" target="_blank" rel="noopener">來源</a></td>
    </tr>`).join("")}</tbody></table></div>`;
}

/* ---------------- 立即更新 ---------------- */
async function doRefresh(btn) {
  btn.disabled = true;
  btn.textContent = "更新中…";
  try {
    const r = await fetch("/api/refresh", { cache: "no-store" });
    if (!r.ok) throw new Error("server");
    await loadData();
    btn.textContent = "✓ 已更新";
  } catch (e) {
    alert("無法即時更新（可能未以 scripts/serve.py 啟動）。\n\n請改執行：python scripts/update_data.py\n或啟動本站：python scripts/serve.py");
    btn.textContent = "⟳ 立即更新";
  }
  btn.disabled = false;
  setTimeout(() => { btn.textContent = "⟳ 立即更新"; }, 2500);
}

/* ---------------- 資料載入 ---------------- */
async function loadData() {
  const bust = "ts=" + Date.now();
  try {
    NEWS = await (await fetch("data/news.json?" + bust, { cache: "no-store" })).json();
  } catch (e) { NEWS = null; }
  try {
    RSO = await (await fetch("data/rso_stats.json?" + bust, { cache: "no-store" })).json();
  } catch (e) { RSO = null; }

  // 最後更新時間
  const lu = $("#last-updated");
  if (lu) {
    lu.innerHTML = NEWS
      ? `📡 資料更新：<b>${esc(NEWS.generated_at)}</b>（${NEWS.count} 條）`
      : "📡 尚未有更新資料";
  }

  // 主頁區塊
  const hn = $("#home-news");
  if (hn) {
    hn.innerHTML = NEWS
      ? NEWS.items.slice(0, 6).map(i => newsItemHTML(i, true)).join("")
      : fallbackHTML();
  }
  const ha = $("#home-accident");
  if (ha) {
    const acc = NEWS ? NEWS.items.filter(i => i.category === "accident").slice(0, 5) : [];
    ha.innerHTML = acc.length ? acc.map(i => newsItemHTML(i, true)).join("")
      : '<p class="muted">暫無工傷／意外分類報道。</p>';
  }

  renderNewsRegion($("#news-list") ? currentRegion : "HK", "#news-list");
  const al = $("#accident-list");
  if (al) {
    const acc = NEWS ? NEWS.items.filter(i => i.category === "accident").slice(0, 60) : [];
    al.innerHTML = acc.length ? acc.map(i => newsItemHTML(i, false)).join("") : fallbackHTML();
  }
  const yt = $("#yt-latest");
  if (yt) {
    const vids = NEWS ? NEWS.items.filter(i => i.kind === "video") : [];
    yt.innerHTML = vids.length ? vids.map(i =>
      `<div class="news-item"><span class="news-date">${fmtDate(i.date || i.fetched)}</span>
       <div class="news-body"><a class="news-title" href="${esc(i.url)}" target="_blank" rel="noopener">▶️ ${esc(i.title)}</a>
       <div class="news-meta"><span class="badge src-yt_alert">YouTube</span><span>來源:${esc(i.source_label)}</span></div></div></div>`).join("")
      : '<p class="muted">暫無影片資料,請按「立即更新」。</p>';
  }
  renderRsoStats();
  renderSourceStatus();
}

/* ---------------- 新聞分區小頁籤 ---------------- */
let currentRegion = "HK";
function initSubTabs() {
  $$(".sub-tab").forEach(b => {
    b.addEventListener("click", () => {
      $$(".sub-tab").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      currentRegion = b.dataset.newsRegion;
      renderNewsRegion(currentRegion, "#news-list");
    });
  });
}

/* ---------------- 啟動 ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  initRouter();
  initSubTabs();
  $("#btn-refresh").addEventListener("click", e => doRefresh(e.currentTarget));
  loadData();
  // 若以 serve.py 啟動,每6小時自動刷新一次資料
  setInterval(async () => {
    try {
      await fetch("/api/refresh", { cache: "no-store" });
      await loadData();
    } catch (e) { /* 非 serve 模式,略過 */ }
  }, 6 * 60 * 60 * 1000);
});
