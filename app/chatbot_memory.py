"""
chatbot_memory.py - Simple conversation memory for the chatbot

This module provides conversation history tracking between user sessions.
It helps the chatbot remember previous interactions and provide more context-aware responses.
"""

import time
from collections import defaultdict, deque

# Maximum number of messages to remember per user
MAX_MEMORY_SIZE = 5

# Maximum lifetime of a message in memory (in seconds) - 30 minutes
MESSAGE_LIFETIME = 30 * 60  

class ChatbotMemory:
    """Manages conversation history for the chatbot"""
    
    def __init__(self):
        # Store conversations per user session
        # Format: {session_id: [(timestamp, role, message), ...]}
        self.conversations = defaultdict(lambda: deque(maxlen=MAX_MEMORY_SIZE))
        
    def add_message(self, session_id, role, message):
        """
        Add a message to the conversation history
        
        Args:
            session_id (str): User session identifier
            role (str): Either 'user' or 'bot'
            message (str): The message content
        """
        timestamp = time.time()
        self.conversations[session_id].append((timestamp, role, message))
        
    def get_conversation_history(self, session_id, limit=None):
        """
        Get conversation history for a session
        
        Args:
            session_id (str): User session identifier
            limit (int, optional): Max number of messages to return. Defaults to None.
            
        Returns:
            list: List of (role, message) tuples, most recent last
        """
        now = time.time()
        # Filter out expired messages
        active_messages = [(t, r, m) for t, r, m in self.conversations[session_id] 
                           if now - t < MESSAGE_LIFETIME]
        
        # Update the conversation with only active messages
        self.conversations[session_id] = deque(active_messages, maxlen=MAX_MEMORY_SIZE)
        
        # Return only the role and message, not timestamps
        history = [(role, msg) for _, role, msg in self.conversations[session_id]]
        
        if limit and limit > 0:
            history = history[-limit:]
            
        return history
    
    def get_formatted_history(self, session_id, limit=None):
        """
        Get a formatted conversation history for API prompting
        
        Args:
            session_id (str): User session identifier
            limit (int, optional): Max number of messages to return. Defaults to None.
            
        Returns:
            str: Formatted conversation history
        """
        history = self.get_conversation_history(session_id, limit)
        
        if not history:
            return ""
        
        formatted = "Dưới đây là lịch sử trò chuyện gần đây:\n"
        
        for role, message in history:
            formatted += f"{'Người dùng' if role == 'user' else 'Chatbot'}: {message}\n"
            
        return formatted
        
    def has_recent_conversation(self, session_id):
        """
        Check if there is a recent conversation for this session
        
        Args:
            session_id (str): User session identifier
            
        Returns:
            bool: True if there's a recent conversation
        """
        if not self.conversations[session_id]:
            return False
            
        now = time.time()
        latest_timestamp, _, _ = self.conversations[session_id][-1]
        
        # If the latest message is recent (within last 5 minutes)
        return now - latest_timestamp < 5 * 60
        

# Singleton instance
memory = ChatbotMemory()
