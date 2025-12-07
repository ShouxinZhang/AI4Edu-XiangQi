#!/bin/bash
# restart.sh - 重启前后端服务（只释放自己使用的端口）

set -e

# 配置
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🛑 正在停止服务..."

# 只释放后端端口
PORT_PID=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
if [ -n "$PORT_PID" ]; then
    echo "  释放端口 $BACKEND_PORT (PID: $PORT_PID)"
    kill -9 $PORT_PID 2>/dev/null || true
fi

# 只释放前端端口
PORT_PID=$(lsof -ti:$FRONTEND_PORT 2>/dev/null || true)
if [ -n "$PORT_PID" ]; then
    echo "  释放端口 $FRONTEND_PORT (PID: $PORT_PID)"
    kill -9 $PORT_PID 2>/dev/null || true
fi

sleep 1

echo ""
echo "🚀 启动后端服务器 (端口 8000)..."
cd "$(dirname "$0")/backend"
nohup uvicorn server:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
echo "   后端 PID: $!"

sleep 2

echo ""
echo "🚀 启动前端开发服务器..."
cd "$(dirname "$0")"
nohup npm run dev > /tmp/frontend.log 2>&1 &
echo "   前端 PID: $!"

sleep 3

echo ""
echo "✅ 服务已启动!"
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo ""
echo "📄 日志文件:"
echo "   后端: /tmp/backend.log"
echo "   前端: /tmp/frontend.log"
