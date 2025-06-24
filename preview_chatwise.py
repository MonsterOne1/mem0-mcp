#!/usr/bin/env python3
"""
Chatwise 聊天记录预览工具
在导入前预览会提取的内容
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class ChatwisePreview:
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)
        self.preview_data = []
        
    def load_chat_files(self) -> List[Dict[str, Any]]:
        """加载所有聊天文件"""
        chat_files = []
        
        for file_path in self.export_path.glob("chat-*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    chat_files.append(chat_data)
            except Exception as e:
                print(f"❌ 加载文件失败 {file_path.name}: {e}")
        
        return chat_files
    
    def extract_user_messages(self, chat_data: Dict[str, Any]) -> List[str]:
        """从聊天记录中提取用户消息"""
        user_messages = []
        
        if 'messages' not in chat_data:
            return user_messages
        
        for message in chat_data['messages']:
            if message.get('role') == 'user' and message.get('content'):
                content = message['content'].strip()
                if content and len(content) > 5:  # 过滤太短的消息
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
    
    def preview_chatwise_export(self):
        """预览 Chatwise 导出数据"""
        print("🔍 Chatwise 聊天记录预览")
        print("=" * 50)
        
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
        
        total_messages = 0
        categorized_messages = {
            "个人偏好": [],
            "工作信息": [],
            "个人信息": [],
            "人际关系": [],
            "目标和计划": [],
            "技能和知识": [],
            "重要日期和事件": [],
            "其他信息": []
        }
        
        # 处理每个聊天文件
        for i, chat_data in enumerate(chat_files, 1):
            print(f"\n📝 聊天 {i}: {chat_data.get('title', 'New Chat')}")
            
            # 提取上下文
            context = self.extract_conversation_context(chat_data)
            print(f"   上下文: {context}")
            
            # 提取用户消息
            user_messages = self.extract_user_messages(chat_data)
            print(f"   用户消息: {len(user_messages)} 条")
            
            # 分类消息
            for message in user_messages:
                category = self.categorize_content(message)
                categorized_messages[category].append({
                    'content': message,
                    'context': context,
                    'chat_title': chat_data.get('title', 'New Chat')
                })
                total_messages += 1
        
        # 显示分类统计
        print("\n" + "=" * 50)
        print("📊 分类统计:")
        for category, messages in categorized_messages.items():
            if messages:
                print(f"   {category}: {len(messages)} 条")
        
        print(f"\n📈 总计: {total_messages} 条用户消息")
        
        # 显示示例内容
        print("\n" + "=" * 50)
        print("📋 示例内容预览:")
        
        for category, messages in categorized_messages.items():
            if messages:
                print(f"\n🔹 {category} ({len(messages)} 条):")
                for i, msg in enumerate(messages[:3], 1):  # 只显示前3条
                    print(f"   {i}. {msg['content'][:80]}...")
                    print(f"      来源: {msg['chat_title']}")
                if len(messages) > 3:
                    print(f"   ... 还有 {len(messages) - 3} 条")
        
        # 询问是否继续导入
        print("\n" + "=" * 50)
        response = input("是否继续导入这些内容到记忆系统? (y/n): ").strip().lower()
        
        if response in ['y', 'yes', '是', 'Y']:
            print("\n🚀 开始导入...")
            # 这里可以调用导入功能
            print("请运行: ./import_chatwise.py")
        else:
            print("❌ 取消导入")

def main():
    """主函数"""
    print("🔍 Chatwise 聊天记录预览工具")
    print("=" * 50)
    
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
    
    # 创建预览器并处理
    previewer = ChatwisePreview(export_path)
    previewer.preview_chatwise_export()

if __name__ == "__main__":
    main() 