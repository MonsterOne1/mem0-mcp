#!/usr/bin/env python3
"""
测试 MCP 记忆服务器是否正常工作
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any

async def test_mcp_server():
    """测试 MCP 服务器连接和功能"""
    
    base_url = "http://localhost:8080"
    
    print("🧪 开始测试 MCP 记忆服务器...")
    print(f"📍 服务器地址: {base_url}")
    print("-" * 50)
    
    # 测试 1: 检查服务器是否运行
    print("1️⃣ 测试服务器连接...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/sse") as response:
                if response.status == 200:
                    print("✅ 服务器连接成功!")
                else:
                    print(f"❌ 服务器响应异常: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保服务器正在运行: ./start_assistant.sh")
        return False
    
    # 测试 2: 测试 SSE 连接
    print("\n2️⃣ 测试 SSE 连接...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/sse") as response:
                if response.status == 200:
                    print("✅ SSE 连接成功!")
                else:
                    print(f"❌ SSE 连接失败: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ SSE 连接错误: {e}")
        return False
    
    # 测试 3: 测试工具列表 (通过模拟 MCP 请求)
    print("\n3️⃣ 测试工具可用性...")
    try:
        # 模拟 MCP 初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/messages/", json=init_request) as response:
                if response.status == 200:
                    print("✅ MCP 协议通信正常!")
                else:
                    print(f"⚠️  MCP 协议测试: {response.status}")
    except Exception as e:
        print(f"⚠️  MCP 协议测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 服务器测试完成!")
    print("\n📋 下一步:")
    print("1. 在 Chatwise 中添加 MCP 服务器:")
    print("   - 名称: mem0-mcp")
    print("   - URL: http://localhost:8080/sse")
    print("   - 传输类型: SSE")
    print("\n2. 重启 Chatwise 并测试记忆功能")
    print("\n3. 尝试告诉 AI: '记住我喜欢喝咖啡'")
    
    return True

async def test_memory_functions():
    """测试记忆功能 (需要实际的 MCP 客户端)"""
    print("\n🔍 记忆功能测试:")
    print("由于需要完整的 MCP 客户端，请在 Chatwise 中测试以下功能:")
    print("\n📝 测试存储记忆:")
    print("   '记住我的名字是张三，我喜欢摄影'")
    print("\n🔍 测试搜索记忆:")
    print("   '你还记得我喜欢什么吗？'")
    print("\n📋 测试获取所有记忆:")
    print("   '告诉我你记得关于我的所有信息'")

if __name__ == "__main__":
    print("🚀 MCP 记忆服务器测试工具")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_mcp_server())
    asyncio.run(test_memory_functions())
    
    print("\n✨ 测试完成! 如果所有测试都通过，你的服务器就可以在 Chatwise 中使用了。") 