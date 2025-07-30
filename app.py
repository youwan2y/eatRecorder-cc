import os
import json
from datetime import datetime
from zhipuai import ZhipuAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Iterator, Optional, List, Any
from db_utils import DatabaseManager
from file_operations import FileManager
from function_statistics import FunctionCallStatistics
from visualization import DataVisualizer

# 配置你的API密钥
API_KEY = "7f19e322592746f4967003fdde505901.LYWsCBh699azgL8J"

# 初始化ZhipuAI客户端和管理器
client = ZhipuAI(api_key=API_KEY)
db_manager = DatabaseManager()
file_manager = FileManager(db_manager)
stats_manager = FunctionCallStatistics(db_manager)
visualizer = DataVisualizer(stats_manager, db_manager)

# 创建自定义的ZhipuAI聊天模型适配器
class ZhipuAIChatModel(BaseChatModel):
    client: Any = None
    tools: Any = None
    
    def __init__(self, client):
        super().__init__(client=client)
    
    @property
    def _llm_type(self) -> str:
        return "zhipuai"
    
    def bind_tools(self, tools):
        """绑定工具到模型"""
        self.tools = tools
        return self
    
    def _generate(
        self, 
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult:
        # 转换LangChain消息格式为ZhipuAI格式
        zhipu_messages = []
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "user"
                if hasattr(msg, 'type'):
                    if msg.type == "ai":
                        role = "assistant"
                    elif msg.type == "system":
                        role = "system"
                    elif msg.type == "human":
                        role = "user"
                
                zhipu_messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        # 准备工具配置
        tools_config = None
        if self.tools:
            tools_config = []
            for tool in self.tools:
                if hasattr(tool, 'name') and hasattr(tool, 'description'):
                    # 为record_thing工具设置正确的参数schema
                    if tool.name == "record_thing":
                        tool_config = {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "date": {
                                            "type": "string",
                                            "description": "日期"
                                        },
                                        "eat": {
                                            "type": "string",
                                            "description": "食物"
                                        },
                                        "money": {
                                            "type": "string",
                                            "description": "金额"
                                        }
                                    },
                                    "required": ["date", "eat", "money"]
                                }
                            }
                        }
                    else:
                        # 其他工具使用默认配置
                        tool_config = {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        }
                    tools_config.append(tool_config)
        
        # 调用ZhipuAI API
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=zhipu_messages,
                tools=tools_config,
                tool_choice="auto" if tools_config else None,
            )
            
            # 转换响应格式
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message'):
                    message = choice.message
                    content = getattr(message, 'content', '')
                    
                    # 检查是否有工具调用
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        # 处理工具调用
                        tool_calls = []
                        for tool_call in message.tool_calls:
                            # 确保工具调用格式正确
                            function_name = getattr(tool_call.function, 'name', '')
                            function_args = getattr(tool_call.function, 'arguments', '{}')
                            
                            # 解析参数为字典
                            try:
                                import json
                                args_dict = json.loads(function_args)
                            except:
                                args_dict = {"__arg1": function_args}
                            
                            # 创建LangChain期望的工具调用格式
                            tool_call_dict = {
                                "id": getattr(tool_call, 'id', ''),
                                "name": function_name,
                                "args": args_dict
                            }
                            tool_calls.append(tool_call_dict)
                        
                        # 创建带工具调用的AI消息
                        ai_message = AIMessage(content=content)
                        ai_message.tool_calls = tool_calls
                        generation = ChatGeneration(message=ai_message)
                    else:
                        generation = ChatGeneration(message=AIMessage(content=content))
                    
                    return ChatResult(generations=[generation])
            
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content="无法获取响应"))])
        except Exception as e:
            print(f"调用ZhipuAI API时出错: {str(e)}")
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=f"API调用失败: {str(e)}"))])
    
    def _stream(
        self, 
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> Iterator[ChatGeneration]:
        # 简化实现，不支持流式输出
        result = self._generate(messages, stop, run_manager, **kwargs)
        for generation in result.generations:
            yield generation

# 定义工具函数
@tool
def record_thing(date: str, eat: str, money: str) -> dict:
    """记录用户在某日吃了什么花了多少钱"""
    try:
        # 参数校验
        if not date or not eat or not money:
            print(f"记录数据参数不完整: date={date}, eat={eat}, money={money}")
            return {"status": "error", "message": "日期、食物和金额不能为空"}
        
        print(f"准备记录数据: date={date}, eat={eat}, money={money}")
        
        # 记录函数调用
        call_logged = db_manager.log_function_call("record_thing", {"date": date, "eat": eat, "money": money})
        if not call_logged:
            print("函数调用日志记录失败")
        
        # 保存记录到数据库
        saved = db_manager.save_eating_record(date, eat, money)
        if not saved:
            print("饮食记录保存失败")
            return {"status": "error", "message": "数据库记录保存失败"}
        
        print("数据已成功记录到数据库")
        return {"status": "success", "message": f"已记录：{date}吃了{eat}，花费{money}"}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"记录数据失败: {str(e)}")
        print(error_trace)
        return {"status": "error", "message": f"记录数据失败: {str(e)}"}

@tool
def read_file(file_path: str) -> dict:
    """读取指定文件的内容"""
    return file_manager.read_file(file_path)

@tool
def write_file(file_path: str, content: str) -> dict:
    """写入内容到指定文件"""
    return file_manager.write_file(file_path, content)

@tool
def list_directory(directory_path: str = '.') -> dict:
    """列出指定目录的内容"""
    return file_manager.list_directory(directory_path)

@tool
def get_all_records() -> dict:
    """获取所有饮食记录"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_all_records", {})
        
        records = db_manager.get_all_eating_records()
        return {"status": "success", "records": records}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_records_by_date(date: str) -> dict:
    """获取特定日期的饮食记录"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_records_by_date", {"date": date})
        
        records = db_manager.get_eating_records_by_date(date)
        return {"status": "success", "records": records}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_total_spending() -> dict:
    """获取总消费金额"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_total_spending", {})
        
        total = db_manager.get_total_spending()
        return {"status": "success", "total": total}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_function_stats() -> dict:
    """获取函数调用统计信息"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_function_stats", {})
        
        report = stats_manager.generate_function_call_report()
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_eating_stats() -> dict:
    """获取饮食统计信息"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_eating_stats", {})
        
        report = stats_manager.generate_eating_report()
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def generate_function_chart() -> dict:
    """生成函数调用可视化图表"""
    try:
        result = visualizer.generate_function_call_chart()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def generate_eating_charts() -> dict:
    """生成饮食统计可视化图表"""
    try:
        result = visualizer.generate_eating_charts()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 创建工具列表
tools = [
    record_thing,
    read_file,
    write_file,
    list_directory,
    get_all_records,
    get_records_by_date,
    get_total_spending,
    get_function_stats,
    get_eating_stats,
    generate_function_chart,
    generate_eating_charts
]

# 创建聊天模型
chat_model = ZhipuAIChatModel(client)

# 绑定工具到模型
chat_model_with_tools = chat_model.bind_tools(tools)

# 设置系统提示
system_prompt = """
你是一个提供情绪价值的闲聊助手，同时帮助用户记录信息。

你的主要工作流程是：
1. 和用户闲聊，保持友好和热情
2. 当用户提到日期(date)、食物(eat)和金额(money)的完整信息时，调用record_thing函数记录
3. 如果用户只提供了部分信息，引导他们补充完整所有必要信息

你可以使用以下功能：
- record_thing: 记录用户的饮食和消费信息
- read_file: 读取文件内容
- write_file: 写入内容到文件
- list_directory: 列出目录内容
- get_all_records: 查询所有记录
- get_records_by_date: 查询特定日期的记录
- get_total_spending: 获取总消费金额
- get_function_stats: 获取函数调用统计
- get_eating_stats: 获取饮食统计
- generate_function_chart: 生成函数调用可视化图表
- generate_eating_charts: 生成饮食统计可视化图表
"""

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 创建代理
agent = create_tool_calling_agent(chat_model_with_tools, tools, prompt)

# 创建代理执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# 创建内存管理器
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 创建带聊天历史的代理
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 初始化应用
if __name__ == "__main__":
    print("欢迎使用智谱AI助手！输入'退出'结束对话。")
    
    while True:
        try:
            user_input = input("你: ")
            
            if user_input.lower() in ["退出", "exit", "quit"]:
                print("感谢使用，再见！")
                break
            
            if not user_input.strip():
                print("输入不能为空，请重新输入。")
                continue
            
            try:
                # 使用代理处理用户输入
                config = {"configurable": {"session_id": "default"}}
                response = agent_with_chat_history.invoke(
                    {"input": user_input}, config
                )
                
                # 显示助手回复
                if "output" in response:
                    print(f"助手: {response['output']}")
                else:
                    print(f"助手: {response}")
                    
            except Exception as e:
                import traceback
                print(f"与AI交互时发生错误: {str(e)}")
                print(traceback.format_exc())
                print("助手: 抱歉，我遇到了一些问题，请再试一次。")
                
        except KeyboardInterrupt:
            print("\n程序被用户中断。感谢使用，再见！")
            break
        except Exception as e:
            import traceback
            print(f"发生未知错误: {str(e)}")
            print(traceback.format_exc()) 