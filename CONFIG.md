# 配置说明

## 环境变量设置

1. 创建 `.env` 文件在项目根目录：

```bash
touch .env
```

2. 在 `.env` 文件中添加以下内容：

```env
# Mem0 API Key
# 从 https://mem0.ai 获取你的API密钥
MEM0_API_KEY=your_mem0_api_key_here

# 可选: 自定义用户ID
# DEFAULT_USER_ID=your_custom_user_id
```

## 获取 Mem0 API Key

1. 访问 [Mem0.ai](https://mem0.ai)
2. 注册或登录账户
3. 在控制台中获取你的API密钥
4. 将API密钥复制到 `.env` 文件中

## 启动服务器

### 方法1: 使用启动脚本（推荐）
```bash
./start_assistant.sh
```

### 方法2: 手动启动
```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -e .

# 启动服务器
uv run main.py
```

## 在Cursor中连接

1. 启动服务器后，在Cursor中打开设置
2. 找到MCP配置部分
3. 添加新的MCP服务器：
   - 名称: `mem0-mcp`
   - 端点: `http://0.0.0.0:8080/sse`
4. 保存并重启Cursor

## 验证连接

启动服务器后，你应该能看到类似以下的输出：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 确保API密钥正确复制
   - 检查API密钥是否有效

2. **端口被占用**
   - 使用不同端口: `uv run main.py --port 8081`

3. **依赖安装失败**
   - 确保Python版本 >= 3.12
   - 重新安装: `uv pip install -e . --force-reinstall`

4. **连接失败**
   - 检查防火墙设置
   - 确保服务器正在运行
   - 验证端点URL是否正确 