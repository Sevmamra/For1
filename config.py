import os
from typing import List, Dict

class Config:
    """
    Bot Configuration Settings
    """
    
    # Telegram Bot Token
    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Authorized Users
    AUTHORIZED_USER_IDS: List[int] = [
        int(user_id) for user_id in os.getenv("AUTHORIZED_USER_IDS", "").split(",") 
        if user_id.strip()
    ]
    
    # Groups Configuration
    GROUPS_CONFIG: Dict[int, str] = {
        int(group.split(":")[0]): group.split(":")[1]
        for group in os.getenv("GROUPS_CONFIG", "").split(",")
        if ":" in group
    }
    
    # Default Group
    DEFAULT_GROUP_ID: int = list(GROUPS_CONFIG.keys())[0] if GROUPS_CONFIG else None
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Session Timeout
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))
    
    # Messages
    WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE")
    TOPIC_CREATED_MSG: str = os.getenv("TOPIC_CREATED_MSG")

    @classmethod
    def validate(cls):
        """Validate required configurations"""
        if not cls.TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not cls.AUTHORIZED_USER_IDS:
            raise ValueError("At least one AUTHORIZED_USER_ID is required")
        if not cls.GROUPS_CONFIG:
            raise ValueError("At least one GROUP_CONFIG is required")
