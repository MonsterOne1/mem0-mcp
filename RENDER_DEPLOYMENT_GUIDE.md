# mem0-mcp Render 部署指南

本指南将帮助你将 mem0-mcp 项目部署到 Render 平台。

## 前置准备

1. **Render 账号**: 访问 [render.com](https://render.com) 注册账号
2. **GitHub 账号**: 确保你有 GitHub 账号并已 fork 或克隆了 mem0-mcp 项目
3. **mem0 API Key**: 从 [mem0.ai](https://mem0.ai) 获取你的 API key

## 部署步骤

### 1. 准备项目文件

首先，将以下文件添加到你的项目根目录：

1. **render.yaml** - Render 部署配置文件
2. **build.sh** - 构建脚本
3. **requirements.txt** - Python 依赖文件
4. **main_render.py** - 适配 Render 的主程序文件

这些文件已经在当前目录创建好了。

### 2. 推送代码到 GitHub

```bash
# 将新文件添加到你的 fork 仓库
cd mem0-mcp
cp /Users/monster/render.yaml .
cp /Users/monster/build.sh .
cp /Users/monster/requirements.txt .
cp /Users/monster/main_render.py .

# 提交并推送
git add render.yaml build.sh requirements.txt main_render.py
git commit -m "Add Render deployment configuration"
git push origin main
```

### 3. 在 Render 上部署

1. 登录到 [Render Dashboard](https://dashboard.render.com)

2. 点击 "New +" 按钮，选择 "Web Service"

3. 连接你的 GitHub 仓库：
   - 如果是第一次使用，需要授权 Render 访问你的 GitHub
   - 选择你的 mem0-mcp fork 仓库

4. 配置服务：
   - **Name**: `mem0-mcp` (或你喜欢的名称)
   - **Region**: 选择离你最近的区域
   - **Branch**: `main`
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `python main_render.py`

5. 设置环境变量：
   - 点击 "Advanced" 展开高级选项
   - 在 "Environment Variables" 部分添加：
     - **Key**: `MEM0_API_KEY`
     - **Value**: 你的 mem0 API key

6. 选择计划：
   - 对于测试，可以选择 "Free" 计划
   - 生产环境建议选择付费计划以获得更好的性能

7. 点击 "Create Web Service" 开始部署

### 4. 等待部署完成

Render 会自动：
- 克隆你的代码
- 运行构建脚本安装依赖
- 启动服务

部署过程通常需要 2-5 分钟。你可以在日志中查看部署进度。

### 5. 获取服务 URL

部署成功后，Render 会提供一个 URL，格式类似：
```
https://mem0-mcp-xxxx.onrender.com
```

你的 SSE 端点将是：
```
https://mem0-mcp-xxxx.onrender.com/sse
```

### 6. 在 Cursor 中配置

1. 打开 Cursor 的 MCP 配置文件 (`~/.cursor/mcp.json`)

2. 添加 mem0-mcp 服务器配置：

```json
{
  "mcpServers": {
    "mem0-mcp": {
      "transport": "sse",
      "endpoint": "https://mem0-mcp-xxxx.onrender.com/sse"
    }
  }
}
```

3. 重启 Cursor 使配置生效

## 注意事项

1. **免费计划限制**：
   - Render 免费计划的服务在 15 分钟无活动后会休眠
   - 首次访问可能需要等待服务唤醒（约 30 秒）
   - 每月有 750 小时的免费运行时间

2. **安全性**：
   - 确保不要将 API key 提交到 GitHub
   - 使用 Render 的环境变量功能安全存储敏感信息

3. **性能优化**：
   - 考虑使用付费计划以获得持续运行的服务
   - 可以配置自定义域名

4. **调试**：
   - 查看 Render Dashboard 中的日志了解服务状态
   - 使用 `curl` 测试端点：
     ```bash
     curl -X POST https://mem0-mcp-xxxx.onrender.com/sse
     ```

## 更新部署

当你更新代码后：

1. 推送更改到 GitHub
2. Render 会自动检测到更改并重新部署
3. 或者在 Render Dashboard 中手动触发部署

## 故障排除

### 常见问题

1. **部署失败**：
   - 检查 build.sh 是否有执行权限
   - 确认 Python 版本是否正确（需要 3.12+）
   - 查看构建日志中的错误信息

2. **服务无法启动**：
   - 确认 MEM0_API_KEY 环境变量已设置
   - 检查 main_render.py 中的端口配置

3. **Cursor 连接失败**：
   - 确认 SSE 端点 URL 正确
   - 检查服务是否正在运行
   - 查看 Render 日志中的错误信息

## 本地测试

在部署前，你可以本地测试：

```bash
# 设置环境变量
export MEM0_API_KEY=your_api_key_here
export PORT=8080

# 安装依赖
pip install -r requirements.txt

# 运行服务
python main_render.py
```

然后访问 `http://localhost:8080/sse` 测试。

## 支持

如有问题，可以：
- 查看 [Render 文档](https://docs.render.com)
- 查看 [mem0 文档](https://docs.mem0.ai)
- 在项目的 GitHub Issues 中提问