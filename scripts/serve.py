# -*- coding: utf-8 -*-
"""
香港職業安全資訊網 — 本機伺服器
================================
用法:  python scripts/serve.py [埠號]        (預設 8080)
然後瀏覽 http://127.0.0.1:8080

特點:
  - 純標準庫,無需安裝套件
  - 啟動時自動執行一次 update_data.py 更新資料
  - 提供 GET /api/status  (查詢資料更新時間)
  - 提供 GET /api/refresh (即時重新抓取,網站「立即更新」按鈕使用)
"""

import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "update_data.py"


def run_update():
    """執行更新腳本,回傳 (成功?, 輸出結尾)"""
    try:
        r = subprocess.run([sys.executable, str(SCRIPT)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300,
                           cwd=str(ROOT))
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out[-1500:]
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def end_headers(self):
        # html/json 不快取,確保更新後即時可見
        if self.path in ("/index.html", "/") or self.path.endswith(".json"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        if self.path.startswith("/api/status"):
            try:
                d = json.loads((ROOT / "data" / "news.json").read_text(encoding="utf-8"))
                body = {"ok": True, "generated_at": d.get("generated_at"),
                        "count": d.get("count", 0)}
            except Exception as e:
                body = {"ok": False, "error": str(e)}
            self._json(body)
        elif self.path.startswith("/api/refresh"):
            ok, out = run_update()
            try:
                d = json.loads((ROOT / "data" / "news.json").read_text(encoding="utf-8"))
                gen, cnt = d.get("generated_at"), d.get("count", 0)
            except Exception:
                gen, cnt = None, 0
            self._json({"ok": ok, "generated_at": gen, "count": cnt, "log": out})
        else:
            super().do_GET()

    def _json(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("香港職業安全資訊網 — 啟動中,先自動更新一次資料…")
    ok, out = run_update()
    print(out.strip() or ("更新完成" if ok else "更新失敗(將以現有資料啟動)"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"✓ 請用瀏覽器開啟  http://127.0.0.1:{port}   (按 Ctrl+C 停止)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
