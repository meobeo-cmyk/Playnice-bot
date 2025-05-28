import os
from typing import List

class Config:
    """Configuration class for the moderation bot"""
    
    # Discord Bot Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Moderation Settings
    MUTE_DURATION_MINUTES = 10
    INVITE_MUTE_DURATION_MINUTES = 5
    
    # Violation Types
    VIOLATION_TYPES = {
        "PROFANITY": "Ngôn từ thô tục",
        "HARASSMENT": "Quấy rối, gạ gẫm",
        "OFFENSIVE": "Nội dung xúc phạm",
        "DISCORD_INVITE": "Link Discord không được phép",
        "SPAM": "Spam"
    }
    
    # Vietnamese profanity words (basic list)
    PROFANITY_WORDS = [
        "đụ", "địt", "lồn", "cặc", "đéo", "vãi", "chó", "khốn",
        "súc vật", "thằng khốn", "con chó", "đồ khốn", "mẹ kiếp",
        "đồ ngu", "ngu si", "đần độn", "óc chó", "não cá vàng"
    ]
    
    # Harassment/grooming keywords
    HARASSMENT_KEYWORDS = [
        "gạ", "quen", "làm quen", "kết bạn", "hẹn hò", "yêu đương",
        "gặp mặt", "ra ngoài", "đi chơi", "sexy", "xinh đẹp",
        "dễ thương", "cute", "baby", "tình yêu", "crush"
    ]
    
    # Offensive keywords
    OFFENSIVE_KEYWORDS = [
        "chết đi", "chết tiệt", "đi chết", "mày", "tao", "bố mày",
        "mẹ mày", "gia đình mày", "đồ rác", "thằng rác", "con rác",
        "thần kinh", "bệnh hoạn", "điên", "khùng"
    ]
    
    # Discord invite patterns
    DISCORD_INVITE_PATTERNS = [
        "discord.gg/",
        "discord.com/invite/",
        "discordapp.com/invite/"
    ]
    
    # Database file
    DATABASE_FILE = "violations.json"
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_all_bad_words(cls) -> List[str]:
        """Get all bad words combined"""
        return cls.PROFANITY_WORDS + cls.HARASSMENT_KEYWORDS + cls.OFFENSIVE_KEYWORDS
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.DISCORD_BOT_TOKEN:
            print("❌ DISCORD_BOT_TOKEN không được tìm thấy!")
            return False
        
        if not cls.OPENAI_API_KEY:
            print("⚠️ OPENAI_API_KEY không được tìm thấy - sẽ sử dụng keyword filtering")
        
        return True
