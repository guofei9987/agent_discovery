#!/bin/bash

# 新闻聚合器启动脚本

# 清理函数
cleanup() {
    echo "正在停止服务..."
    if [[ -n $API_PID ]]; then
        kill $API_PID 2>/dev/null
    fi
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    # 等待进程完全终止
    sleep 2
    # 强制杀死可能残留的进程
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    exit 0
}

# 捕获中断信号
trap cleanup INT TERM

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否需要安装依赖
if [ ! -f "venv/installed" ]; then
    echo "安装依赖包..."
    pip install -r requirements.txt
    touch venv/installed
fi

# 杀死可能存在的僵尸进程
echo "清理可能存在的僵尸进程..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
sleep 2

# 启动后端API服务器
echo "启动后端API服务器..."
python main.py api &
API_PID=$!

# 等待API服务器启动
sleep 5

# 检查API服务器是否成功启动
if ! lsof -ti:8000 >/dev/null; then
    echo "错误: API服务器启动失败，端口8000已被占用或启动出错"
    cleanup
    exit 1
fi

# 启动前端开发服务器
echo "启动前端开发服务器..."
python agent_discovery/frontend/server.py &
FRONTEND_PID=$!

# 等待前端服务器启动
sleep 3

# 检查前端服务器是否成功启动
if ! lsof -ti:8080 >/dev/null; then
    echo "错误: 前端服务器启动失败，端口8080已被占用或启动出错"
    cleanup
    exit 1
fi

# 显示访问信息
echo ""
echo "======================================"
echo "新闻聚合器已启动!"
echo "后端API: http://localhost:8000"
echo "前端界面: http://localhost:8080"
echo "======================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待所有后台进程
wait $API_PID $FRONTEND_PID
