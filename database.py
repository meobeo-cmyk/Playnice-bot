import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class ViolationDatabase:
    def __init__(self):
        self.config = Config()
        self.db_file = self.config.DATABASE_FILE
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            self._create_empty_database()
    
    def _create_empty_database(self):
        """Create an empty database file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({"violations": []}, f, ensure_ascii=False, indent=2)
            logger.info(f"Created new database file: {self.db_file}")
        except Exception as e:
            logger.error(f"Failed to create database file: {e}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from database file"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._create_empty_database()
            return {"violations": []}
        except json.JSONDecodeError as e:
            logger.error(f"Database file corrupted: {e}")
            # Backup corrupted file and create new one
            if os.path.exists(self.db_file):
                backup_name = f"{self.db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.db_file, backup_name)
                logger.info(f"Corrupted database backed up as: {backup_name}")
            self._create_empty_database()
            return {"violations": []}
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return {"violations": []}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save data to database file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def add_violation(self, user_id: int, username: str, violation_type: str, 
                     message_content: str, channel_id: int, guild_id: int):
        """Add a new violation to the database"""
        try:
            data = self._load_data()
            
            violation = {
                "id": len(data["violations"]) + 1,
                "user_id": user_id,
                "username": username,
                "violation_type": violation_type,
                "message_content": message_content[:500],  # Limit message length
                "channel_id": channel_id,
                "guild_id": guild_id,
                "timestamp": datetime.utcnow().isoformat(),
                "handled": True
            }
            
            data["violations"].append(violation)
            self._save_data(data)
            
            logger.info(f"Added violation for user {username} ({user_id}): {violation_type}")
            
        except Exception as e:
            logger.error(f"Failed to add violation: {e}")
    
    def get_violations_last_week(self, guild_id: int = None) -> List[Dict[str, Any]]:
        """Get all violations from the last week for a specific guild"""
        try:
            data = self._load_data()
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            
            filtered_violations = []
            for violation in data["violations"]:
                try:
                    violation_time = datetime.fromisoformat(violation["timestamp"])
                    if violation_time >= one_week_ago:
                        if guild_id is None or violation.get("guild_id") == guild_id:
                            filtered_violations.append(violation)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid violation timestamp: {e}")
                    continue
            
            return filtered_violations
            
        except Exception as e:
            logger.error(f"Failed to get violations: {e}")
            return []
    
    def get_user_violations(self, user_id: int, guild_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get violations for a specific user"""
        try:
            data = self._load_data()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            user_violations = []
            for violation in data["violations"]:
                try:
                    if violation["user_id"] == user_id:
                        violation_time = datetime.fromisoformat(violation["timestamp"])
                        if violation_time >= cutoff_date:
                            if guild_id is None or violation.get("guild_id") == guild_id:
                                user_violations.append(violation)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid violation data: {e}")
                    continue
            
            return user_violations
            
        except Exception as e:
            logger.error(f"Failed to get user violations: {e}")
            return []
    
    def get_violation_stats(self, guild_id: int, days: int = 7) -> Dict[str, Any]:
        """Get violation statistics for a guild"""
        try:
            violations = self.get_violations_last_week(guild_id) if days == 7 else self._get_violations_last_n_days(guild_id, days)
            
            stats = {
                "total_violations": len(violations),
                "violation_types": {},
                "top_violators": {},
                "daily_breakdown": {},
                "average_per_day": 0
            }
            
            for violation in violations:
                # Count by type
                v_type = violation["violation_type"]
                stats["violation_types"][v_type] = stats["violation_types"].get(v_type, 0) + 1
                
                # Count by user
                user_id = violation["user_id"]
                username = violation["username"]
                if user_id not in stats["top_violators"]:
                    stats["top_violators"][user_id] = {"username": username, "count": 0}
                stats["top_violators"][user_id]["count"] += 1
                
                # Daily breakdown
                violation_date = datetime.fromisoformat(violation["timestamp"]).date()
                date_str = violation_date.isoformat()
                stats["daily_breakdown"][date_str] = stats["daily_breakdown"].get(date_str, 0) + 1
            
            # Calculate average per day
            if days > 0:
                stats["average_per_day"] = round(len(violations) / days, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get violation stats: {e}")
            return {"total_violations": 0, "violation_types": {}, "top_violators": {}, "daily_breakdown": {}, "average_per_day": 0}
    
    def _get_violations_last_n_days(self, guild_id: int, days: int) -> List[Dict[str, Any]]:
        """Get violations from the last N days"""
        try:
            data = self._load_data()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            filtered_violations = []
            for violation in data["violations"]:
                try:
                    violation_time = datetime.fromisoformat(violation["timestamp"])
                    if violation_time >= cutoff_date:
                        if violation.get("guild_id") == guild_id:
                            filtered_violations.append(violation)
                except (ValueError, KeyError):
                    continue
            
            return filtered_violations
            
        except Exception as e:
            logger.error(f"Failed to get violations for last {days} days: {e}")
            return []
    
    def clear_violations(self, guild_id: int = None):
        """Clear all violations for a guild or all violations"""
        try:
            data = self._load_data()
            
            if guild_id is None:
                # Clear all violations
                data["violations"] = []
                logger.info("Cleared all violations")
            else:
                # Clear violations for specific guild
                original_count = len(data["violations"])
                data["violations"] = [v for v in data["violations"] if v.get("guild_id") != guild_id]
                cleared_count = original_count - len(data["violations"])
                logger.info(f"Cleared {cleared_count} violations for guild {guild_id}")
            
            self._save_data(data)
            
        except Exception as e:
            logger.error(f"Failed to clear violations: {e}")
    
    def cleanup_old_violations(self, days: int = 30):
        """Remove violations older than specified days"""
        try:
            data = self._load_data()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            original_count = len(data["violations"])
            data["violations"] = [
                v for v in data["violations"]
                if datetime.fromisoformat(v["timestamp"]) >= cutoff_date
            ]
            removed_count = original_count - len(data["violations"])
            
            if removed_count > 0:
                self._save_data(data)
                logger.info(f"Cleaned up {removed_count} old violations (older than {days} days)")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old violations: {e}")
