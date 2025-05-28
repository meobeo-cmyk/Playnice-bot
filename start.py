#!/usr/bin/env python3
"""
Launcher script để chạy cả Discord Bot và Web Dashboard cùng lúc
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_discord_bot():
    """Chạy Discord Bot"""
    print("🤖 Starting Discord Bot...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("🤖 Discord Bot stopped")
    except Exception as e:
        print(f"❌ Discord Bot error: {e}")

def run_web_dashboard():
    """Chạy Web Dashboard"""
    print("🌐 Starting Web Dashboard...")
    try:
        subprocess.run([sys.executable, "web_app.py"], check=True)
    except KeyboardInterrupt:
        print("🌐 Web Dashboard stopped")
    except Exception as e:
        print(f"❌ Web Dashboard error: {e}")

def check_environment():
    """Kiểm tra environment variables cần thiết"""
    required_vars = {
        'DISCORD_BOT_TOKEN': 'Discord Bot Token (required)',
        'DATABASE_URL': 'Database URL (required for dashboard)',
        'FLASK_SECRET_KEY': 'Flask Secret Key (required for dashboard)'
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key (optional, for AI moderation)'
    }
    
    missing_required = []
    missing_optional = []
    
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"  - {var}: {desc}")
    
    for var, desc in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"  - {var}: {desc}")
    
    if missing_required:
        print("❌ Missing required environment variables:")
        for var in missing_required:
            print(var)
        print("\nPlease set these variables and try again.")
        return False
    
    if missing_optional:
        print("⚠️  Optional environment variables not set:")
        for var in missing_optional:
            print(var)
        print()
    
    print("✅ Environment check passed!")
    return True

def main():
    print("=" * 50)
    print("🚀 Discord Bot Moderation System")
    print("=" * 50)
    
    # Kiểm tra environment
    if not check_environment():
        sys.exit(1)
    
    print("\nStarting both Discord Bot and Web Dashboard...")
    print("Press Ctrl+C to stop both services\n")
    
    # Tạo threads cho cả 2 services
    bot_thread = Thread(target=run_discord_bot, daemon=True)
    dashboard_thread = Thread(target=run_web_dashboard, daemon=True)
    
    try:
        # Start cả 2 services
        bot_thread.start()
        time.sleep(2)  # Delay nhỏ để bot start trước
        dashboard_thread.start()
        
        print("✅ Both services started successfully!")
        print("🤖 Discord Bot: Running")
        print("🌐 Web Dashboard: http://localhost:5000")
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()