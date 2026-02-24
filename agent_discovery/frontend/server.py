"""
简单的前端开发服务器（支持 API 代理）
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time
import urllib.request
import json

# 默认端口
DEFAULT_PORT = 8080

# 获取前端目录路径
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 后端 API 地址（通过 start_server 设置）
_backend_url = None


class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """支持 API 代理的 HTTP 请求处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        """处理 GET 请求"""
        # API 代理路径
        if self.path.startswith('/api/'):
            self._proxy_request('GET')
        else:
            super().do_GET()

    def do_POST(self):
        """处理 POST 请求"""
        if self.path.startswith('/api/'):
            self._proxy_request('POST')
        else:
            self.send_error(405, "Method Not Allowed")

    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS 预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def _proxy_request(self, method):
        """代理请求到后端 API"""
        global _backend_url

        if not _backend_url:
            self.send_error(500, "Backend URL not configured")
            return

        # 构建后端 URL
        backend_path = self.path[4:]  # 移除 '/api' 前缀
        backend_url = f"{_backend_url}{backend_path}"

        try:
            # 读取请求体（如果是 POST）
            body = None
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)

            # 创建请求
            req = urllib.request.Request(
                backend_url,
                data=body,
                method=method,
                headers={
                    'Content-Type': self.headers.get('Content-Type', 'application/json'),
                    'Accept': self.headers.get('Accept', '*/*'),
                }
            )

            # 发送请求到后端
            with urllib.request.urlopen(req, timeout=30) as response:
                # 返回响应给客户端
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(500, f"Proxy error: {str(e)}")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()


def start_server(port: int = DEFAULT_PORT, backend_port: int = None, open_browser_flag: bool = True):
    """启动开发服务器

    Args:
        port: 前端服务器端口，默认8080
        backend_port: 后端API端口，如果提供则启用API代理
        open_browser_flag: 是否自动打开浏览器
    """
    global _backend_url

    # 设置后端 URL
    if backend_port:
        _backend_url = f"http://localhost:{backend_port}"
        print(f"API 代理已启用: 前端 /api/* -> {_backend_url}/*")

    try:
        with socketserver.TCPServer(("", port), ProxyHTTPRequestHandler) as httpd:
            print(f"前端开发服务器启动 at http://localhost:{port}")
            print(f"前端目录: {FRONTEND_DIR}")
            print("按 Ctrl+C 停止服务器")

            # 在新线程中打开浏览器
            if open_browser_flag:
                def open_browser():
                    time.sleep(2)
                    webbrowser.open(f"http://localhost:{port}/index.html")

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
