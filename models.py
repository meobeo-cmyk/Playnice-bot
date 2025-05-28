from datetime import datetime
from app import db

class FilterKeyword(db.Model):
    __tablename__ = 'filter_keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # PROFANITY, HARASSMENT, OFFENSIVE
    context = db.Column(db.Text, nullable=True)  # Ngữ cảnh sử dụng
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=True)

class ViolationLog(db.Model):
    __tablename__ = 'violation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    guild_id = db.Column(db.String(50), nullable=False)
    channel_id = db.Column(db.String(50), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    detected_keywords = db.Column(db.Text, nullable=True)  # JSON string of detected keywords
    ai_confidence = db.Column(db.Float, nullable=True)
    action_taken = db.Column(db.String(100), nullable=False)  # mute, warn, delete
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)