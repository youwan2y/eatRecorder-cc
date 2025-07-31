"""
智谱AI饮食记录助手 - 主应用程序
模块化架构版本
"""
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from zai import ZhipuAiClient
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool

# 导入核心模块
sys.path.append(str(Path(__file__).parent))

from app.core.config import AppConfig
from app.core.models import ZhipuAIChatModel
from app.utils.session_manager import SessionManager
from app.tools.tool_registry import ToolRegistry
from app.agents.smart_agent import SmartAgent

# 导入工具模块
from app.tools.food_tools import (
    record_thing, get_all_records, get_records_by_date, 
    get_total_spending, get_eating_stats, recommend_food
)
from app.tools.file_tools import (
    read_file, write_file, list_directory
)
from app.tools.stats_tools import (
    get_function_stats, generate_function_chart, generate_eating_charts
)

class EatRecorderApp:
    """主应用程序类"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = ZhipuAiClient(api_key=config.api_key)
        self.session_manager = SessionManager(config.max_sessions, config.session_timeout)
        self.tool_registry = ToolRegistry()
        
        # 初始化Agent
        self.smart_agent = None
        self.smart_agent_with_history = None
        
        self._setup_tools()
        self._setup_agents()
    
    def _setup_tools(self):
        """设置和注册所有工具"""
        # 注册食物工具（带特殊schema）
        self.tool_registry.register_tool_with_schema(
            record_thing,
            properties={
                "date": {"type": "string", "description": "日期"},
                "eat": {"type": "string", "description": "食物"},
                "money": {"type": "string", "description": "金额"}
            },
            required=["date", "eat", "money"]
        )
        
        # 注册其他工具
        other_tools = [
            get_all_records, get_records_by_date, get_total_spending, get_eating_stats,
            recommend_food,
            read_file, write_file, list_directory,
            get_function_stats, generate_function_chart, generate_eating_charts
        ]
        
        for tool_func in other_tools:
            self.tool_registry.register_tool(tool_func)
        
        print(f"✅ 已注册 {len(self.tool_registry.get_all_tools())} 个工具")
    
    def _setup_agents(self):
        """设置智能统一Agent"""
        # 创建聊天模型
        chat_model = ZhipuAIChatModel(self.client)
        
        # 获取所有工具
        all_tools = self.tool_registry.get_all_tools()
        
        # 创建智能统一Agent
        self.smart_agent = SmartAgent(chat_model, all_tools)
        
        # 设置带历史记录的Agent
        self.smart_agent_with_history = RunnableWithMessageHistory(
            self.smart_agent.executor,
            self.session_manager.get_session,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        
        print("✅ 智能Agent设置完成")
    
    def process_user_input(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        try:
            # 直接使用智能Agent处理所有输入
            config = {"configurable": {"session_id": "default"}}
            
            print("🤖 使用智能Agent处理...")
            response = self.smart_agent_with_history.invoke(
                {"input": user_input}, config
            )
            
            # 返回响应
            if "output" in response:
                return response['output']
            else:
                return str(response)
                
        except Exception as e:
            import traceback
            print(f"❌ 处理用户输入时发生错误: {str(e)}")
            print(traceback.format_exc())
            return "抱歉，我遇到了一些问题，请再试一次。"
    
    def get_stats(self) -> Dict:
        """获取应用程序统计信息"""
        return {
            'session_count': self.session_manager.get_session_count(),
            'tool_registry_stats': self.tool_registry.get_stats()
        }
    
    def cleanup(self):
        """清理资源"""
        self.session_manager.cleanup_all()

def main():
    """主应用程序入口点"""
    print("🚀 正在初始化智谱AI饮食记录助手...")
    print("📁 模块化架构版本")
    
    try:
        # 加载配置
        config = AppConfig.from_env()
        
        # 初始化应用程序
        app = EatRecorderApp(config)
        
        # 显示欢迎信息
        print("\n" + "="*50)
        print("🎉 欢迎使用智谱AI饮食记录助手！")
        print("💡 功能特点：")
        print("   • 智能意图识别")
        print("   • 饮食记录管理")
        print("   • 消费统计分析")
        print("   • 文件操作支持")
        print("   • 可视化图表生成")
        print("="*50)
        print("📝 输入'退出'或'exit'结束对话")
        print(f"📊 当前活跃会话数: {app.session_manager.get_session_count()}")
        print("-"*50)
        
        while True:
            try:
                user_input = input("你: ")
                
                # 检查退出命令
                if user_input.lower() in ["退出", "exit", "quit"]:
                    print("👋 感谢使用，再见！")
                    break
                
                if not user_input.strip():
                    print("⚠️ 输入不能为空，请重新输入。")
                    continue
                
                # 处理输入并获取响应
                response = app.process_user_input(user_input)
                print(f"助手: {response}")
                print("-"*50)
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断。感谢使用，再见！")
                break
            except EOFError:
                print("\n\n👋 输入结束。感谢使用，再见！")
                break
            except Exception as e:
                import traceback
                print(f"❌ 发生未知错误: {str(e)}")
                print(traceback.format_exc())
                print("助手: 抱歉，我遇到了一些问题，请再试一次。")
                
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("💡 请确保设置了 ZHIPUAI_API_KEY 环境变量")
        print("   或者将API密钥添加到 .env 文件中")
    except Exception as e:
        import traceback
        print(f"❌ 启动失败: {str(e)}")
        print(traceback.format_exc())
    finally:
        if 'app' in locals():
            app.cleanup()

if __name__ == "__main__":
    main()