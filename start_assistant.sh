#!/bin/bash

# AI Assistant Memory Server Startup Script

echo "🤖 启动AI助理记忆服务器..."

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 激活虚拟环境..."
    source .venv/bin/activate
fi

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "请创建 .env 文件并添加你的 MEM0_API_KEY"
    echo "示例: MEM0_API_KEY=your_api_key_here"
    exit 1
fi

# 检查依赖是否安装
echo "🔍 检查依赖..."
if ! python -c "import mem0" 2>/dev/null; then
    echo "📥 安装依赖..."
    uv pip install -e .
fi

# 启动服务器
echo "🚀 启动服务器在 http://0.0.0.0:8080"
echo "📡 SSE端点: http://0.0.0.0:8080/sse"
echo ""
echo "在Cursor中连接到此端点即可使用AI助理记忆功能"
echo "按 Ctrl+C 停止服务器"
echo ""

uv run main.py 