#!/usr/bin/env python3
"""
启动脚本 - 自动设置环境并运行应用
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """设置环境变量"""
    # 硬编码API密钥，不再需要环境变量
    os.environ['ZHIPUAI_API_KEY'] = '7f19e322592746f4967003fdde505901.LYWsCBh699azgL8J'
    
    # 如果没有设置API密钥，尝试从环境变量文件读取
    if not os.getenv('ZHIPUAI_API_KEY'):
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            print("📋 从 .env 文件加载环境变量...")
            from dotenv import load_dotenv
            load_dotenv(env_file)
    
    return True

def main():
    """主函数"""
    print("🚀 启动智谱AI饮食记录助手...")
    
    # 设置环境
    if not setup_environment():
        sys.exit(1)
    
    # 运行主应用
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所有依赖：pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()