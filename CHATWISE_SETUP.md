# Chatwise 配置指南

## 在 Chatwise 中配置 MCP 记忆服务器

Chatwise 是一个支持 MCP (Model Context Protocol) 的 AI 聊天应用，可以轻松集成我们的记忆管理系统。

## 步骤 1: 启动记忆服务器

首先确保你的记忆服务器正在运行：

```bash
# 使用启动脚本
./start_assistant.sh

# 或者手动启动
uv run main.py
```

服务器启动后，你应该看到类似输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

## 步骤 2: 在 Chatwise 中配置 MCP

### 方法 1: 通过 Chatwise 设置界面

1. 打开 Chatwise 应用
2. 进入设置 (Settings)
3. 找到 "MCP Servers" 或 "Model Context Protocol" 部分
4. 点击 "Add Server" 或 "添加服务器"
5. 填写以下信息：
   - **Server Name**: `mem0-mcp` (或任何你喜欢的名称)
   - **Server URL**: `http://localhost:8080/sse`
   - **Transport Type**: `SSE` (Server-Sent Events)
6. 保存配置

### 方法 2: 通过配置文件 (如果支持)

如果 Chatwise 支持配置文件，你可以添加：

```json
{
  "mcpServers": [
    {
      "name": "mem0-mcp",
      "url": "http://localhost:8080/sse",
      "transport": "sse",
      "enabled": true
    }
  ]
}
```

## 步骤 3: 验证连接

1. 重启 Chatwise 应用
2. 开始一个新的对话
3. 尝试使用记忆功能，例如：
   ```
   用户: "记住我喜欢喝咖啡"
   AI: 应该会使用 add_memory 工具存储这个信息
   ```

## 步骤 4: 测试记忆功能

### 测试存储记忆
```
用户: "我的名字是张三，我喜欢摄影和旅行"
```

### 测试搜索记忆
```
用户: "你还记得我喜欢什么吗？"
```

### 测试获取所有记忆
```
用户: "告诉我你记得关于我的所有信息"
```

## 常见问题解决

### 1. 连接失败
- 确保记忆服务器正在运行
- 检查端口 8080 是否被占用
- 尝试使用 `http://127.0.0.1:8080/sse` 替代 `localhost`

### 2. 工具不可用
- 重启 Chatwise 应用
- 检查 MCP 服务器配置是否正确
- 查看服务器日志是否有错误信息

### 3. 记忆不工作
- 确保 `.env` 文件中的 `MEM0_API_KEY` 正确
- 检查网络连接是否正常
- 验证 Mem0 API 密钥是否有效

## 高级配置

### 自定义端口
如果 8080 端口被占用，可以使用其他端口：

```bash
# 启动服务器使用不同端口
uv run main.py --port 8081
```

然后在 Chatwise 中使用：
```
http://localhost:8081/sse
```

### 多用户支持
如果需要支持多个用户，可以修改 `DEFAULT_USER_ID`：

```python
# 在 main.py 中修改
DEFAULT_USER_ID = "chatwise_user_1"
```

## 使用建议

1. **定期备份**: 重要的个人信息建议定期备份
2. **隐私保护**: 不要在记忆中存储敏感信息
3. **自然对话**: 像与朋友聊天一样自然地告诉 AI 你的信息
4. **主动提醒**: 定期询问 AI 记住的信息，确保记忆正常工作

## 故障排除

如果遇到问题，可以：

1. 检查服务器日志
2. 验证 API 密钥
3. 重启服务器和 Chatwise
4. 查看 Chatwise 的 MCP 支持文档

## 联系支持

如果配置过程中遇到问题：
- 检查 [Chatwise 官方文档](https://chatwise.com/docs)
- 查看 MCP 协议文档
- 确认 Chatwise 版本支持 MCP 功能 