import logging
import os
from datetime import datetime
from config import Config

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Configure logging
    log_filename = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Set discord.py logging level to WARNING to reduce noise
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} giây"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} phút"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} giờ {minutes} phút"
        else:
            return f"{hours} giờ"

def truncate_message(message: str, max_length: int = 100) -> str:
    """Truncate message to specified length"""
    if len(message) <= max_length:
        return message
    return message[:max_length-3] + "..."

def is_mention(text: str) -> bool:
    """Check if text contains user mentions"""
    import re
    return bool(re.search(r'<@[!&]?\d+>', text))

def extract_user_id_from_mention(mention: str) -> int:
    """Extract user ID from Discord mention"""
    import re
    match = re.search(r'<@[!&]?(\d+)>', mention)
    if match:
        return int(match.group(1))
    return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    return sanitized

def get_user_display_name(user) -> str:
    """Get user display name safely"""
    try:
        return user.display_name if hasattr(user, 'display_name') else str(user)
    except:
        return "Unknown User"

def is_valid_discord_invite(url: str) -> bool:
    """Validate if URL is a Discord invite link"""
    import re
    discord_invite_pattern = r'^https?://(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+/?$'
    return bool(re.match(discord_invite_pattern, url.strip()))

def format_violation_type(violation_type: str) -> str:
    """Format violation type for display"""
    type_map = {
        "PROFANITY": "🤬 Ngôn từ thô tục",
        "HARASSMENT": "😠 Quấy rối, gạ gẫm", 
        "OFFENSIVE": "😡 Nội dung xúc phạm",
        "DISCORD_INVITE": "🔗 Link Discord",
        "SPAM": "📢 Spam"
    }
    return type_map.get(violation_type.upper(), f"⚠️ {violation_type}")

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a text progress bar"""
    if total == 0:
        return "█" * length
    
    filled_length = int(length * current // total)
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = round(100 * current / total, 1)
    return f"{bar} {percentage}%"

def get_relative_time(timestamp: datetime) -> str:
    """Get relative time string (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} ngày trước"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} giờ trước"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} phút trước"
    else:
        return "Vừa xong"

def validate_environment():
    """Validate required environment variables"""
    required_vars = ["DISCORD_BOT_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

def safe_int_convert(value, default=0):
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def clean_content(content: str) -> str:
    """Clean message content for logging/storage"""
    # Remove mentions, channels, and roles for privacy
    import re
    cleaned = re.sub(r'<@[!&]?\d+>', '[USER]', content)
    cleaned = re.sub(r'<#\d+>', '[CHANNEL]', cleaned)
    cleaned = re.sub(r'<@&\d+>', '[ROLE]', cleaned)
    return cleaned.strip()
