"""
Base agent class and common functionality
"""
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, model: BaseChatModel, tools: List[Any] = None, system_prompt: str = ""):
        self.model = model
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.agent = None
        self.executor = None
        self._setup_agent()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def _setup_agent(self):
        """Setup the agent and executor"""
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create agent
        self.agent = create_tool_calling_agent(self.model, self.tools, prompt)
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def invoke(self, input_data: Dict, config: Dict = None) -> Dict:
        """Invoke the agent with input"""
        if self.executor is None:
            raise ValueError("Agent not properly initialized")
        
        return self.executor.invoke(input_data, config or {})
    
    def get_tools(self) -> List[Any]:
        """Get the tools used by this agent"""
        return self.tools
    
    def get_model(self) -> BaseChatModel:
        """Get the model used by this agent"""
        return self.model