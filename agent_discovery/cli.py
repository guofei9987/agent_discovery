"""
新闻聚合器命令行入口
"""

import argparse
import socket
import sys
import time
import threading
import os
from pathlib import Path
from loguru import logger


def check_port_available(port: int) -> bool:
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return True
        except OSError:
            return False


def start_frontend_server(port: int, backend_port: int = None):
    """启动前端服务器"""
    from agent_discovery.frontend.server import start_server
    start_server(port=port, backend_port=backend_port)


def start_backend_server(host: str, port: int, reload: bool = False):
    """启动后端 API 服务器"""
    import uvicorn
    uvicorn.run(
        "agent_discovery.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def init_config():
    """初始化配置文件"""
    from agent_discovery.config_loader import load_or_create_config, load_or_create_prompt
    load_or_create_config()
    load_or_create_prompt()
    logger.info("✅ 配置文件已初始化")


def cmd_api(args):
    """启动 API 服务器命令"""
    if not check_port_available(args.port):
        logger.error(f"❌ 端口 {args.port} 已被占用，请更换端口")
        sys.exit(1)

    # 确保配置文件存在
    init_config()

    logger.info(f"启动新闻聚合器API服务器 at {args.host}:{args.port}")
    start_backend_server(host=args.host, port=args.port, reload=True)


def cmd_start(args):
    """同时启动前后端服务"""
    # 检查端口
    if not check_port_available(args.backend_port):
        logger.error(f"❌ 后端端口 {args.backend_port} 已被占用，请更换端口")
        sys.exit(1)

    if not check_port_available(args.frontend_port):
        logger.error(f"❌ 前端端口 {args.frontend_port} 已被占用，请更换端口")
        sys.exit(1)

    logger.info("启动新闻聚合器...")

    # 确保配置文件存在
    init_config()

    # 启动后端服务（在子线程中）
    backend_thread = threading.Thread(
        target=start_backend_server,
        args=(args.backend_host, args.backend_port, False)
    )
    backend_thread.daemon = True
    backend_thread.start()

    # 等待后端启动
    time.sleep(2)

    # 启动前端服务（在主线程中，会阻塞）
    logger.info(f"前端服务: http://localhost:{args.frontend_port}")
    start_frontend_server(port=args.frontend_port, backend_port=args.backend_port)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog="agent-discovery",
        description="新闻聚合器 - 信息获取与新闻聚合工具"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # api 子命令
    api_parser = subparsers.add_parser(
        "api",
        help="启动后端API服务器"
    )
    api_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API服务器主机地址 (默认: 0.0.0.0)"
    )
    api_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API服务器端口 (默认: 8000)"
    )
    api_parser.set_defaults(func=cmd_api)

    # start 子命令
    start_parser = subparsers.add_parser(
        "start",
        help="同时启动前后端服务"
    )
    start_parser.add_argument(
        "--backend-host",
        default="0.0.0.0",
        help="后端API主机地址 (默认: 0.0.0.0)"
    )
    start_parser.add_argument(
        "--backend-port",
        type=int,
        default=8000,
        help="后端API端口 (默认: 8000)"
    )
    start_parser.add_argument(
        "--frontend-port",
        type=int,
        default=8080,
        help="前端服务端口 (默认: 8080)"
    )
    start_parser.set_defaults(func=cmd_start)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
