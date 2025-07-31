"""
Session management with cleanup functionality
"""
import time
from threading import Lock
from langchain_core.chat_history import InMemoryChatMessageHistory

class SessionManager:
    """Manages chat sessions with automatic cleanup"""
    
    def __init__(self, max_sessions=100, session_timeout=3600):
        self.sessions = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.lock = Lock()
    
    def get_session(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create a session for the given ID"""
        with self.lock:
            # Clean up expired sessions
            self._cleanup_expired_sessions()
            
            if session_id not in self.sessions:
                if len(self.sessions) >= self.max_sessions:
                    # Remove oldest session
                    oldest_session = min(self.sessions.keys(), 
                                       key=lambda k: self.sessions[k]['last_access'])
                    del self.sessions[oldest_session]
                
                self.sessions[session_id] = {
                    'history': InMemoryChatMessageHistory(),
                    'created_at': time.time(),
                    'last_access': time.time()
                }
            
            self.sessions[session_id]['last_access'] = time.time()
            return self.sessions[session_id]['history']
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, data in self.sessions.items()
            if current_time - data['last_access'] > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """Get current number of active sessions"""
        with self.lock:
            self._cleanup_expired_sessions()
            return len(self.sessions)
    
    def cleanup_all(self):
        """Clean up all sessions"""
        with self.lock:
            self.sessions.clear()