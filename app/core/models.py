"""
Custom ZhipuAI chat model adapter for LangChain
"""
from typing import Iterator, Optional, List, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import AIMessage

class ZhipuAIChatModel(BaseChatModel):
    """Custom adapter for ZhipuAI to work with LangChain"""
    
    client: Any = None
    tools: Any = None
    
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
    
    @property
    def _llm_type(self) -> str:
        return "zhipuai"
    
    def bind_tools(self, tools):
        """Bind tools to the model"""
        self.tools = tools
        return self
    
    def _generate(
        self, 
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult:
        # Convert LangChain message format to ZhipuAI format
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
        
        # Prepare tools configuration
        tools_config = None
        if self.tools:
            tools_config = []
            for tool in self.tools:
                if hasattr(tool, 'name') and hasattr(tool, 'description'):
                    # Special handling for record_thing tool
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
                        # Default configuration for other tools
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
        
        # Call ZhipuAI API
        try:
            response = self.client.chat.completions.create(
                model="glm-4.5-flash",
                messages=zhipu_messages,
                tools=tools_config,
                tool_choice="auto" if tools_config else None,
                thinking={"type": "disabled"}
            )
            
            # Convert response format
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message'):
                    message = choice.message
                    content = getattr(message, 'content', '')
                    
                    # Check for tool calls
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        # Process tool calls
                        tool_calls = []
                        for tool_call in message.tool_calls:
                            # Ensure tool call format is correct
                            function_name = getattr(tool_call.function, 'name', '')
                            function_args = getattr(tool_call.function, 'arguments', '{}')
                            
                            # Parse arguments as dict
                            try:
                                import json
                                args_dict = json.loads(function_args)
                            except:
                                args_dict = {"__arg1": function_args}
                            
                            # Create LangChain expected tool call format
                            tool_call_dict = {
                                "id": getattr(tool_call, 'id', ''),
                                "name": function_name,
                                "args": args_dict
                            }
                            tool_calls.append(tool_call_dict)
                        
                        # Create AI message with tool calls
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
        # Simplified implementation, no streaming support
        result = self._generate(messages, stop, run_manager, **kwargs)
        for generation in result.generations:
            yield generation