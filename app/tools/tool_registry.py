"""
Tool registry for dynamic tool management
"""
from typing import Dict, List, Any, Optional, Callable
from langchain_core.tools import tool

class ToolRegistry:
    """Registry for managing tools and their schemas"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict] = {}
        self.tool_functions: List[Any] = []
    
    def register_tool(self, tool_func: Callable, schema: Optional[Dict] = None):
        """Register a tool function with optional schema"""
        tool_name = tool_func.name if hasattr(tool_func, 'name') else tool_func.__name__
        
        self.tools[tool_name] = tool_func
        
        # Store the decorated tool function
        if hasattr(tool_func, '__wrapped__'):
            self.tool_functions.append(tool_func)
        else:
            self.tool_functions.append(tool_func)
        
        if schema:
            self.schemas[tool_name] = schema
        else:
            # Generate default schema
            self.schemas[tool_name] = self._generate_default_schema(tool_func, tool_name)
    
    def register_tool_with_schema(self, tool_func: Callable, properties: Dict[str, Dict], required: List[str]):
        """Register a tool with custom schema"""
        tool_name = tool_func.name if hasattr(tool_func, 'name') else tool_func.__name__
        
        schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_func.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
        self.register_tool(tool_func, schema)
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict]:
        """Get tool configuration by name"""
        return self.schemas.get(tool_name)
    
    def get_all_tools(self) -> List[Any]:
        """Get all registered tool functions"""
        return self.tool_functions
    
    def get_all_configs(self) -> List[Dict]:
        """Get all tool configurations"""
        return list(self.schemas.values())
    
    def get_tool_names(self) -> List[str]:
        """Get all registered tool names"""
        return list(self.tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered"""
        return tool_name in self.tools
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            del self.schemas[tool_name]
            
            # Remove from tool functions list
            self.tool_functions = [
                func for func in self.tool_functions
                if (func.name if hasattr(func, 'name') else func.__name__) != tool_name
            ]
    
    def _generate_default_schema(self, tool_func: Callable, tool_name: str) -> Dict:
        """Generate default schema for a tool"""
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_func.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            'total_tools': len(self.tools),
            'tool_names': self.get_tool_names()
        }