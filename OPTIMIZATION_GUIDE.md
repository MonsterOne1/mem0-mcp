# 🚀 MCP Server 优化功能指南

本指南介绍了 MCP Memory Server 的所有优化功能，帮助你更好地管理个人记忆。

## 📋 新增功能概览

### 1. 记忆管理工具
- **update_memory** - 更新已存在的记忆
- **delete_memory** - 删除特定记忆
- **export_memories** - 导出记忆到 JSON
- **import_memories** - 从 JSON 导入记忆

### 2. 高级搜索功能
- **advanced_search_memories** - 支持类别、数量、相关性过滤
- **get_memories_by_category** - 按类别查看记忆

### 3. 分析和统计工具
- **get_memory_stats** - 获取记忆统计信息
- **analyze_memories** - 分析记忆模式和生成摘要

### 4. 自动分类系统
- 新增记忆时自动添加类别标签
- 支持 10 个预定义类别

## 🔧 详细功能说明

### 1. 更新记忆 (update_memory)

更新已存在的记忆内容：

```
用户: "使用 search_memories 搜索我的生日"
AI: 搜索结果显示记忆 ID [mem_xxx] 包含你的生日信息

用户: "使用 update_memory 更新这个记忆，我的生日是 3 月 20 日"
AI: 成功更新记忆 [mem_xxx]
```

### 2. 删除记忆 (delete_memory)

删除不再需要的记忆：

```
用户: "删除 ID 为 mem_xxx 的记忆"
AI: 成功删除记忆 [mem_xxx]，此操作不可撤销
```

### 3. 高级搜索 (advanced_search_memories)

支持多种搜索参数：

```
# 按类别搜索
用户: "搜索所有工作相关的记忆"
参数: category="work"

# 限制结果数量
用户: "搜索最相关的 5 条关于技能的记忆"
参数: query="技能", limit=5

# 按相关性过滤
用户: "搜索相关性大于 0.8 的偏好记忆"
参数: category="preferences", min_score=0.8
```

### 4. 类别管理 (get_memories_by_category)

查看按类别组织的记忆：

```
# 查看所有类别
用户: "显示我的记忆按类别分组"

# 查看特定类别
用户: "显示所有个人信息类别的记忆"
参数: category="personal_info"
```

### 5. 记忆统计 (get_memory_stats)

获取记忆的统计信息：

```
用户: "显示我的记忆统计"
AI: 
📊 Memory Statistics
==============================
Total Memories: 45

📂 Categories Breakdown:
  • Personal Info: 12 (26.7%)
  • Preferences: 10 (22.2%)
  • Skills: 8 (17.8%)
  ...
```

### 6. 记忆分析 (analyze_memories)

生成个人画像和洞察：

```
用户: "分析我的所有记忆"
AI:
🧠 Memory Analysis & Summary
========================================

👤 Personal Profile:
  • 你的名字是张三
  • 你住在上海
  
💪 Skills & Expertise:
  • 你会说中文和英语
  • 你正在学习日语
  
🎯 Goals & Aspirations:
  • 你想在今年内学会弹吉他
  ...
```

### 7. 导出记忆 (export_memories)

导出所有记忆用于备份：

```
用户: "导出我的所有记忆"
AI: 成功导出 45 条记忆：
{
  "user_id": "cursor_mcp",
  "export_date": "2025-06-24T10:30:00",
  "total_memories": 45,
  "memories": [...]
}
```

### 8. 导入记忆 (import_memories)

从备份恢复记忆：

```
用户: "导入这些记忆: {JSON 数据}"
AI: 
导入完成：
✅ 成功导入：30 条记忆
⏭️ 跳过（重复）：10 条记忆
❌ 错误：2 条记忆
```

## 🏷️ 自动分类系统

系统支持 10 个预定义类别：

1. **personal_info** - 个人信息（姓名、生日、地址等）
2. **work** - 工作相关（职业、公司、同事等）
3. **relationships** - 人际关系（家人、朋友、伴侣等）
4. **goals** - 目标计划（愿望、梦想、计划等）
5. **knowledge** - 知识信息（学习、理解、事实等）
6. **skills** - 技能专长（语言、能力、专业等）
7. **dates_events** - 日期事件（会议、约会、日程等）
8. **preferences** - 偏好兴趣（喜欢、讨厌、最爱等）
9. **health** - 健康相关（医疗、运动、饮食等）
10. **hobbies** - 爱好娱乐（游戏、音乐、旅行等）

## 🔄 错误处理和重试机制

所有操作都包含：
- 自动重试（最多 3 次）
- 指数退避（1s, 2s, 4s）
- 详细的错误日志
- 用户友好的错误消息

## 💡 使用建议

1. **定期导出备份**：使用 `export_memories` 定期备份重要记忆
2. **使用类别搜索**：通过 `advanced_search_memories` 快速找到特定类型的信息
3. **查看统计分析**：使用 `get_memory_stats` 和 `analyze_memories` 了解记忆分布
4. **管理过期信息**：使用 `update_memory` 更新或 `delete_memory` 删除过时信息
5. **批量导入**：使用 `import_memories` 快速迁移或恢复记忆

## 🎯 典型使用场景

### 场景 1：定期维护
```
1. 使用 get_memory_stats 查看统计
2. 使用 analyze_memories 发现重复或过时信息
3. 使用 update_memory 或 delete_memory 清理
4. 使用 export_memories 备份
```

### 场景 2：快速查找
```
1. 使用 advanced_search_memories 按类别搜索
2. 使用 get_memories_by_category 浏览特定类别
3. 找到所需信息
```

### 场景 3：迁移数据
```
1. 在旧设备上使用 export_memories
2. 保存 JSON 文件
3. 在新设备上使用 import_memories
```

这些优化功能让记忆管理更加高效和智能！