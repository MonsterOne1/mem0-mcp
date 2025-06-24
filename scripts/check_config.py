#!/usr/bin/env python3
"""
检查 MCP 记忆服务器配置
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.12 或更高版本")
        return False

def check_env_file():
    """检查环境变量文件"""
    print("\n🔧 检查环境配置...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ 未找到 .env 文件")
        print("💡 请创建 .env 文件并添加你的 MEM0_API_KEY")
        print("   示例: MEM0_API_KEY=your_api_key_here")
        return False
    
    # 读取 .env 文件
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "MEM0_API_KEY" in content:
            # 检查是否设置了实际的 API key
            lines = content.split('\n')
            for line in lines:
                if line.startswith("MEM0_API_KEY="):
                    key = line.split('=', 1)[1].strip()
                    if key and key != "your_mem0_api_key_here":
                        print("✅ 找到 MEM0_API_KEY 配置")
                        return True
                    else:
                        print("⚠️  MEM0_API_KEY 未设置实际值")
                        print("💡 请在 .env 文件中设置你的实际 API 密钥")
                        return False
            
            print("⚠️  MEM0_API_KEY 格式可能不正确")
            return False
        else:
            print("❌ 未找到 MEM0_API_KEY 配置")
            return False
            
    except Exception as e:
        print(f"❌ 读取 .env 文件失败: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        "mem0",
        "mcp",
        "uvicorn",
        "starlette",
        "aiohttp"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 请安装缺失的依赖:")
        print("   uv pip install -e .")
        return False
    
    return True

def check_server_files():
    """检查服务器文件"""
    print("\n📁 检查服务器文件...")
    
    required_files = [
        "main.py",
        "pyproject.toml",
        "start_assistant.sh"
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """主检查函数"""
    print("🔍 MCP 记忆服务器配置检查")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_env_file(),
        check_dependencies(),
        check_server_files()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 所有检查通过! 你的环境配置正确。")
        print("\n📋 下一步:")
        print("1. 启动服务器: ./start_assistant.sh")
        print("2. 在 Chatwise 中配置 MCP 服务器")
        print("3. 开始使用记忆功能!")
    else:
        print("❌ 配置检查失败，请解决上述问题后重试。")
        print("\n💡 常见解决方案:")
        print("- 安装依赖: uv pip install -e .")
        print("- 创建 .env 文件并设置 API 密钥")
        print("- 确保 Python 版本 >= 3.12")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 