# -*- coding: utf-8 -*-
"""洗翠攻略本地服务器：静态文件 + 进度保存接口（进度默认存到这台电脑的磁盘）

启动：python serve.py [端口]   （默认 8000）

接口：
  GET  /api/save  -> 返回本机保存的进度 JSON（尚无保存返回 204）
  POST /api/save  -> 把请求体 JSON 写入本机 save.json（进度持久化，同一局域网内
                     电脑/iPad 打开同一个地址即共享这份数据；刷新/换浏览器不丢）

线上部署（GitHub Pages 等）没有该接口时，页面自动降级为浏览器 localStorage。
"""
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(ROOT, "save.json")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 只服务本项目目录下的文件
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if urlparse(self.path).path == "/api/save":
            if os.path.exists(SAVE_FILE):
                body = open(SAVE_FILE, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(204)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path == "/api/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                obj = json.loads(raw.decode("utf-8"))  # 校验是合法 JSON
                tmp = SAVE_FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(json.dumps(obj, ensure_ascii=False))
                os.replace(tmp, SAVE_FILE)  # 原子替换，避免半写
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"ok":false}')
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("Hisui Guide server ready:")
    print("  PC   : http://localhost:%d/index.html" % PORT)
    print("  iPad : http://<本机局域网IP>:%d/index.html （同一WiFi）" % PORT)
    print("  progress -> %s" % SAVE_FILE)
    server.serve_forever()
