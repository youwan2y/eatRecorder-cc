"""
Configuration management for the application
"""
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class AppConfig:
    """Application configuration"""
    api_key: str
    model_name: str = "glm-4.5-flash"
    max_tokens: int = 1000
    temperature: float = 0.1
    max_sessions: int = 100
    session_timeout: int = 3600
    db_connections: int = 5
    database_path: str = "agent_records.db"
    
    @classmethod
    def from_env(cls):
        """Create configuration with hardcoded API key"""
        # 硬编码API密钥，不使用环境变量
        api_key = "7f19e322592746f4967003fdde505901.LYWsCBh699azgL8J"
        
        return cls(
            api_key=api_key,
            model_name=os.getenv('MODEL_NAME', 'glm-4.5-flash'),
            max_tokens=int(os.getenv('MAX_TOKENS', '1000')),
            temperature=float(os.getenv('TEMPERATURE', '0.1')),
            max_sessions=int(os.getenv('MAX_SESSIONS', '100')),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600')),
            db_connections=int(os.getenv('DB_CONNECTIONS', '5')),
            database_path=os.getenv('DATABASE_PATH', 'agent_records.db')
        )
    
    @classmethod
    def create_default(cls):
        """Create default configuration with hardcoded values"""
        return cls(
            api_key="7f19e322592746f4967003fdde505901.LYWsCBh699azgL8J",
            model_name="glm-4.5-flash",
            max_tokens=1000,
            temperature=0.1,
            max_sessions=100,
            session_timeout=3600,
            db_connections=5,
            database_path="agent_records.db"
        )