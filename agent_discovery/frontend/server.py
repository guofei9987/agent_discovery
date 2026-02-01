"""
简单的前端开发服务器
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time

# 设置端口
PORT = 8080

# 获取前端目录路径
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()


def start_server():
    """启动开发服务器"""
    try:
        with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
            print(f"前端开发服务器启动 at http://localhost:{PORT}")
            print(f"前端目录: {FRONTEND_DIR}")
            print("按 Ctrl+C 停止服务器")

            # 在新线程中每2秒检查一次是否需要打开浏览器
            def open_browser():
                time.sleep(2)
                webbrowser.open(f"http://localhost:{PORT}/index.html")

            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

            # 启动服务器
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")


if __name__ == "__main__":
    start_server()