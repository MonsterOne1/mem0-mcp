#!/usr/bin/env python3
"""
Chatwise 批量导入工具
高效处理大量聊天记录的导入
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from mem0 import MemoryClient
from dotenv import load_dotenv
import asyncio
import time

load_dotenv()

# 初始化 mem0 客户端
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"

class BatchChatwiseImporter:
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)
        self.memories_added = 0
        self.errors = []
        self.skipped = 0
        
    def load_chat_files(self) -> List[Dict[str, Any]]:
        """加载所有聊天文件"""
        chat_files = []
        
        print("📂 正在加载聊天文件...")
        for file_path in self.export_path.glob("chat-*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    chat_files.append(chat_data)
            except Exception as e:
                print(f"❌ 加载文件失败 {file_path.name}: {e}")
                self.errors.append(f"加载失败 {file_path.name}: {e}")
        
        return chat_files
    
    def extract_user_messages(self, chat_data: Dict[str, Any]) -> List[str]:
        """从聊天记录中提取用户消息"""
        user_messages = []
        
        if 'messages' not in chat_data:
            return user_messages
        
        for message in chat_data['messages']:
            if message.get('role') == 'user' and message.get('content'):
                content = message['content'].strip()
                if content and len(content) > 10:  # 过滤太短的消息
                    user_messages.append(content)
        
        return user_messages
    
    def extract_conversation_context(self, chat_data: Dict[str, Any]) -> str:
        """提取对话上下文"""
        context_parts = []
        
        # 添加聊天标题
        if chat_data.get('title') and chat_data['title'] != 'New Chat':
            context_parts.append(f"对话主题: {chat_data['title']}")
        
        # 添加模型信息
        if chat_data.get('model'):
            context_parts.append(f"使用的模型: {chat_data['model']}")
        
        # 添加时间信息
        if chat_data.get('createdAt'):
            context_parts.append(f"对话时间: {chat_data['createdAt']}")
        
        return " | ".join(context_parts) if context_parts else "Chatwise 对话记录"
    
    def clean_content(self, content: str) -> str:
        """清理内容，移除不必要的格式"""
        # 移除多余的换行和空格
        content = re.sub(r'\n\s*\n', '\n', content)
        content = re.sub(r' +', ' ', content)
        
        # 移除 markdown 格式标记（保留内容）
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        content = re.sub(r'`(.*?)`', r'\1', content)
        
        return content.strip()
    
    def categorize_content(self, content: str) -> str:
        """根据内容分类"""
        content_lower = content.lower()
        
        # 个人信息相关
        if any(word in content_lower for word in ['我', '我的', '自己', '个人']):
            if any(word in content_lower for word in ['喜欢', '爱好', '兴趣', '习惯']):
                return "个人偏好"
            elif any(word in content_lower for word in ['工作', '职业', '公司', '职位']):
                return "工作信息"
            elif any(word in content_lower for word in ['生日', '年龄', '出生']):
                return "个人信息"
            elif any(word in content_lower for word in ['朋友', '家人', '同事', '关系']):
                return "人际关系"
        
        # 目标和计划
        if any(word in content_lower for word in ['目标', '计划', '想要', '希望', '打算']):
            return "目标和计划"
        
        # 技能和知识
        if any(word in content_lower for word in ['技能', '能力', '学习', '知识', '技术']):
            return "技能和知识"
        
        # 重要日期和事件
        if any(word in content_lower for word in ['时间', '日期', '会议', '约会', '截止']):
            return "重要日期和事件"
        
        return "其他信息"
    
    def add_memory(self, content: str, category: str = "", context: str = "") -> bool:
        """添加记忆到系统"""
        try:
            # 构建完整的记忆内容
            memory_parts = []
            if category:
                memory_parts.append(f"[{category}]")
            if context:
                memory_parts.append(f"上下文: {context}")
            memory_parts.append(content)
            
            full_memory = " | ".join(memory_parts)
            
            # 清理内容
            cleaned_memory = self.clean_content(full_memory)
            
            if len(cleaned_memory) < 15:
                self.skipped += 1
                return False
            
            # 添加到记忆系统
            messages = [{"role": "user", "content": cleaned_memory}]
            mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
            
            self.memories_added += 1
            return True
            
        except Exception as e:
            print(f"❌ 添加记忆失败: {e}")
            self.errors.append(f"添加记忆失败: {e}")
            return False
    
    def process_chatwise_export(self):
        """处理 Chatwise 导出数据"""
        print("🚀 开始批量导入 Chatwise 聊天记录...")
        print(f"📁 导出路径: {self.export_path}")
        print("-" * 50)
        
        # 检查路径是否存在
        if not self.export_path.exists():
            print(f"❌ 导出路径不存在: {self.export_path}")
            return
        
        # 加载聊天文件
        chat_files = self.load_chat_files()
        
        if not chat_files:
            print("❌ 没有找到聊天文件")
            return
        
        print(f"📊 找到 {len(chat_files)} 个聊天文件")
        
        # 统计信息
        total_messages = 0
        processed_chats = 0
        
        # 处理每个聊天文件
        for i, chat_data in enumerate(chat_files, 1):
            # 提取上下文
            context = self.extract_conversation_context(chat_data)
            
            # 提取用户消息
            user_messages = self.extract_user_messages(chat_data)
            
            if user_messages:
                processed_chats += 1
                total_messages += len(user_messages)
                
                # 显示进度
                if i % 10 == 0 or i == len(chat_files):
                    print(f"📝 处理进度: {i}/{len(chat_files)} ({i/len(chat_files)*100:.1f}%)")
                
                # 处理用户消息
                for message in user_messages:
                    category = self.categorize_content(message)
                    self.add_memory(message, category, context)
        
        # 输出统计信息
        print("\n" + "=" * 50)
        print("📊 批量导入完成!")
        print(f"✅ 成功添加记忆: {self.memories_added} 条")
        print(f"⏭️  跳过内容: {self.skipped} 条")
        print(f"📝 处理聊天: {processed_chats}/{len(chat_files)} 个")
        print(f"💬 总消息数: {total_messages} 条")
        
        if self.errors:
            print(f"❌ 错误数量: {len(self.errors)}")
            print("\n错误详情:")
            for error in self.errors[:5]:  # 只显示前5个错误
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... 还有 {len(self.errors) - 5} 个错误")
        
        print("\n💡 现在你可以在 Chatwise 中测试记忆功能:")
        print("   - '你还记得我们之前讨论过什么吗？'")
        print("   - '告诉我你记得关于我的所有信息'")

def main():
    """主函数"""
    print("🧠 Chatwise 批量导入工具")
    print("=" * 50)
    
    # 检查配置
    try:
        test_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=1)
        print("✅ 记忆系统连接正常")
    except Exception as e:
        print(f"❌ 记忆系统连接失败: {e}")
        print("💡 请检查 .env 文件中的 MEM0_API_KEY 是否正确")
        return
    
    # 默认导出路径
    default_export_path = "/Users/monster/Library/Mobile Documents/com~apple~CloudDocs/cherry-studio/chatwise-export-2025-06-24-12-05"
    
    # 检查默认路径是否存在
    if Path(default_export_path).exists():
        export_path = default_export_path
        print(f"📁 使用默认导出路径: {export_path}")
    else:
        # 让用户输入路径
        export_path = input("请输入 Chatwise 导出文件夹路径: ").strip()
        if not export_path:
            print("❌ 未提供导出路径")
            return
    
    # 确认导入
    print(f"\n⚠️  即将导入大量聊天记录，这可能需要一些时间...")
    response = input("是否继续? (y/n): ").strip().lower()
    
    if response not in ['y', 'yes', '是', 'Y']:
        print("❌ 取消导入")
        return
    
    # 创建导入器并处理
    start_time = time.time()
    importer = BatchChatwiseImporter(export_path)
    importer.process_chatwise_export()
    
    end_time = time.time()
    print(f"\n⏱️  总耗时: {end_time - start_time:.1f} 秒")

if __name__ == "__main__":
    main() 