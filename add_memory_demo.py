#!/usr/bin/env python3
"""
记忆添加演示脚本
展示如何直接调用记忆功能
"""

import asyncio
import json
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

# 初始化 mem0 客户端
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"

async def add_memory_demo():
    """演示如何添加记忆"""
    
    print("🧠 记忆添加演示")
    print("=" * 50)
    
    # 示例记忆内容
    memories = [
        "我的名字是张三，我喜欢喝美式咖啡，每天早晨都会喝一杯",
        "我的生日是3月15日，我妻子的生日是7月22日",
        "我会说中文和英语，正在学习日语。我喜欢摄影和旅行",
        "我的朋友李四在北京工作，是做软件开发的，他的电话是138-xxxx-xxxx",
        "我想在今年内学会弹吉他，并且计划去日本旅行",
        "我下周要准备一个关于AI的演讲，需要准备PPT",
        "我最近了解到地中海饮食对健康很有好处，包括橄榄油、鱼类和蔬菜"
    ]
    
    print("📝 添加示例记忆...")
    
    for i, memory in enumerate(memories, 1):
        try:
            messages = [{"role": "user", "content": memory}]
            mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
            print(f"✅ {i}. 已添加: {memory[:50]}...")
        except Exception as e:
            print(f"❌ {i}. 添加失败: {e}")
    
    print("\n🎉 记忆添加完成!")
    print("\n💡 现在你可以在 Chatwise 中测试搜索这些记忆:")
    print("   - '你还记得我喜欢什么吗？'")
    print("   - '我的生日是什么时候？'")
    print("   - '我会什么语言？'")
    print("   - '我的朋友李四是做什么的？'")

async def search_memory_demo():
    """演示如何搜索记忆"""
    
    print("\n🔍 记忆搜索演示")
    print("=" * 50)
    
    search_queries = [
        "我喜欢什么饮料",
        "我的生日",
        "我会什么语言",
        "我的朋友李四",
        "我的目标"
    ]
    
    for query in search_queries:
        try:
            print(f"\n🔎 搜索: '{query}'")
            memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1")
            
            if memories["results"]:
                for i, result in enumerate(memories["results"][:3], 1):  # 只显示前3个结果
                    print(f"   {i}. {result['memory'][:100]}...")
            else:
                print("   ❌ 未找到相关记忆")
                
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")

async def get_all_memories_demo():
    """演示如何获取所有记忆"""
    
    print("\n📋 获取所有记忆演示")
    print("=" * 50)
    
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=10)
        
        if memories["results"]:
            print(f"📊 总共找到 {len(memories['results'])} 条记忆:")
            for i, memory in enumerate(memories["results"], 1):
                print(f"   {i}. {memory['memory'][:80]}...")
        else:
            print("❌ 没有找到任何记忆")
            
    except Exception as e:
        print(f"❌ 获取记忆失败: {e}")

def interactive_add_memory():
    """交互式添加记忆"""
    
    print("\n🎯 交互式记忆添加")
    print("=" * 50)
    print("输入你想记住的信息 (输入 'quit' 退出):")
    
    while True:
        try:
            user_input = input("\n💭 你想记住什么? ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break
                
            if not user_input:
                print("⚠️  请输入内容")
                continue
                
            # 添加记忆
            messages = [{"role": "user", "content": user_input}]
            mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
            print("✅ 已添加到记忆中!")
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 添加失败: {e}")

async def main():
    """主函数"""
    
    print("🚀 MCP 记忆系统演示")
    print("=" * 50)
    
    # 检查配置
    try:
        # 测试连接
        test_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=1)
        print("✅ 记忆系统连接正常")
    except Exception as e:
        print(f"❌ 记忆系统连接失败: {e}")
        print("💡 请检查 .env 文件中的 MEM0_API_KEY 是否正确")
        return
    
    # 运行演示
    await add_memory_demo()
    await search_memory_demo()
    await get_all_memories_demo()
    
    # 交互式添加
    print("\n" + "=" * 50)
    interactive_add_memory()

if __name__ == "__main__":
    asyncio.run(main()) 