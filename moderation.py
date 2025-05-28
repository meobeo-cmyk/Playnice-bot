import json
import re
import asyncio
import logging
from typing import Dict, Any, List
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

class ModerationService:
    def __init__(self):
        self.config = Config()
        self.openai_client = None
        
        # Initialize OpenAI if API key is available
        if self.config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.warning("OpenAI API key not found, using keyword-based filtering only")
    
    async def check_message(self, content: str) -> Dict[str, Any]:
        """
        Check if a message violates community guidelines
        Returns a dictionary with violation information
        """
        if not content or len(content.strip()) == 0:
            return {"is_violation": False}
        
        # First, try OpenAI-based analysis if available
        if self.openai_client:
            try:
                ai_result = await self.check_with_ai(content)
                if ai_result["is_violation"]:
                    return ai_result
            except Exception as e:
                logger.warning(f"AI moderation failed, falling back to keyword filtering: {e}")
        
        # Fallback to keyword-based filtering
        return self.check_with_keywords(content)
    
    async def check_with_ai(self, content: str) -> Dict[str, Any]:
        """Use OpenAI to analyze message content for violations"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Bạn là một hệ thống kiểm duyệt nội dung tiếng Việt. 
                        Phân tích tin nhắn và xác định xem có vi phạm các quy định sau không:
                        1. Ngôn từ thô tục, chửi bậy
                        2. Quấy rối, gạ gẫm
                        3. Xúc phạm, lăng mạ
                        4. Nội dung không phù hợp khác
                        
                        Trả về kết quả JSON với format:
                        {
                            "is_violation": boolean,
                            "violation_type": "string (nếu vi phạm)",
                            "confidence": number (0-1),
                            "reason": "string giải thích"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Phân tích tin nhắn này: {content}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the response
            return {
                "is_violation": result.get("is_violation", False),
                "violation_type": result.get("violation_type", "Unknown"),
                "confidence": min(1.0, max(0.0, result.get("confidence", 0.5))),
                "reason": result.get("reason", "Nội dung không phù hợp")
            }
            
        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            raise
    
    def check_with_keywords(self, content: str) -> Dict[str, Any]:
        """Check message using keyword-based filtering"""
        content_lower = content.lower()
        
        # Check for profanity
        for word in self.config.PROFANITY_WORDS:
            if word.lower() in content_lower:
                return {
                    "is_violation": True,
                    "violation_type": "Ngôn từ thô tục",
                    "confidence": 0.9,
                    "reason": f"Chứa từ ngữ thô tục: {word}"
                }
        
        # Check for harassment
        harassment_count = 0
        found_harassment_words = []
        for word in self.config.HARASSMENT_KEYWORDS:
            if word.lower() in content_lower:
                harassment_count += 1
                found_harassment_words.append(word)
        
        if harassment_count >= 2:  # Multiple harassment keywords
            return {
                "is_violation": True,
                "violation_type": "Quấy rối, gạ gẫm",
                "confidence": 0.8,
                "reason": f"Chứa nội dung gạ gẫm: {', '.join(found_harassment_words)}"
            }
        
        # Check for offensive content
        for word in self.config.OFFENSIVE_KEYWORDS:
            if word.lower() in content_lower:
                return {
                    "is_violation": True,
                    "violation_type": "Nội dung xúc phạm",
                    "confidence": 0.8,
                    "reason": f"Chứa nội dung xúc phạm: {word}"
                }
        
        # Check for excessive caps (shouting)
        if len(content) > 10 and content.isupper():
            return {
                "is_violation": True,
                "violation_type": "Spam/Shouting",
                "confidence": 0.6,
                "reason": "Tin nhắn viết hoa toàn bộ (shouting)"
            }
        
        return {"is_violation": False}
    
    def has_discord_invite(self, content: str) -> bool:
        """Check if message contains Discord invite links"""
        content_lower = content.lower()
        
        for pattern in self.config.DISCORD_INVITE_PATTERNS:
            if pattern in content_lower:
                return True
        
        # Also check for discord invite regex patterns
        discord_invite_regex = r"(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+"
        if re.search(discord_invite_regex, content, re.IGNORECASE):
            return True
        
        return False
    
    def is_potential_spam(self, content: str) -> bool:
        """Check if message is potential spam"""
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', content):  # Same character 5+ times
            return True
        
        # Check for excessive emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
        if emoji_count > 10:
            return True
        
        # Check for excessive mentions
        mention_count = len(re.findall(r'<@[!&]?\d+>', content))
        if mention_count > 5:
            return True
        
        return False
    
    def get_violation_severity(self, violation_type: str) -> str:
        """Get severity level of violation"""
        severity_map = {
            "Ngôn từ thô tục": "high",
            "Quấy rối, gạ gẫm": "critical",
            "Nội dung xúc phạm": "high",
            "Discord Invite Link": "medium",
            "Spam/Shouting": "low"
        }
        return severity_map.get(violation_type, "medium")
