# Discord Bot Kiểm Duyệt + Web Dashboard

Hệ thống hoàn chỉnh bao gồm Discord bot kiểm duyệt tự động và web dashboard quản lý - Tích hợp AI thông minh và giao diện trực quan.

## ✨ Tính năng chính

### 🤖 Discord Bot
- **AI Kiểm duyệt thông minh** - OpenAI GPT-4o phát hiện vi phạm chính xác
- **Lọc từ khóa tiếng Việt** - Database từ khóa được tối ưu hóa
- **Xử lý tự động** - Xóa tin nhắn và mute người vi phạm
- **Slash commands** - `/report` và `/clear_violations` cho admin
- **Chặn link Discord** - Tự động xóa link mời không mong muốn

### 📊 Web Dashboard  
- **Dashboard thống kê** - Biểu đồ vi phạm và analytics realtime
- **Quản lý từ khóa** - Thêm/sửa/xóa với ngữ cảnh chi tiết
- **Lịch sử vi phạm** - Tracking đầy đủ với bộ lọc thông minh
- **Cài đặt linh hoạt** - Cấu hình bot từ xa
- **API endpoints** - Đồng bộ cấu hình realtime

## 🚀 Quick Start

### 1. Clone và cài đặt
```bash
git clone <repository-url>
cd discord-bot-moderation
pip install -r requirements.txt
```

### 2. Environment Variables
```env
# Discord Bot (Required)
DISCORD_BOT_TOKEN=your_discord_bot_token

# OpenAI (Optional but recommended)
OPENAI_API_KEY=your_openai_api_key

# Database (Required for dashboard)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Web Dashboard (Required for dashboard)
FLASK_SECRET_KEY=your_secret_key
```

### 3. Chạy từng thành phần

#### Chỉ Discord Bot
```bash
python main.py
```

#### Chỉ Web Dashboard  
```bash
python web_app.py
```

#### Cả Bot và Dashboard (Khuyến nghị)
```bash
# Terminal 1: Discord Bot
python main.py

# Terminal 2: Web Dashboard
python web_app.py
```

## 📁 Cấu trúc dự án

```
discord-bot-moderation/
├── 🤖 Discord Bot Files
│   ├── main.py              # Bot chính
│   ├── config.py            # Cấu hình và từ khóa
│   ├── moderation.py        # AI và keyword filtering
│   ├── database.py          # JSON database cho bot
│   └── utils.py             # Utilities và logging
│
├── 🌐 Web Dashboard Files  
│   ├── app.py              # Flask app setup
│   ├── web_app.py          # Entry point cho dashboard
│   ├── routes.py           # Web routes và API
│   ├── models.py           # PostgreSQL models
│   ├── forms.py            # WTForms
│   └── templates/          # Jinja2 templates
│       ├── base.html
│       ├── dashboard.html
│       ├── keywords.html
│       ├── violations.html
│       └── settings.html
│
├── 📋 Deploy Files
│   ├── requirements.txt    # All dependencies
│   ├── Procfile           # Heroku deployment
│   └── README.md          # This file
│
└── 📊 Data Storage
    ├── violations.json    # Bot violations (JSON)
    ├── logs/             # Daily log files
    └── PostgreSQL DB     # Dashboard data
```

## 🎯 Workflow sử dụng

### 1. Setup ban đầu
1. **Discord Bot**: Tạo application tại Discord Developer Portal
2. **Database**: Setup PostgreSQL (local hoặc cloud)
3. **OpenAI**: Đăng ký API key (optional)
4. **Deploy**: Chọn platform (Heroku, Railway, VPS)

### 2. Quản lý hàng ngày
1. **Web Dashboard**: Truy cập để xem thống kê
2. **Thêm từ khóa**: Cập nhật danh sách lọc
3. **Monitor**: Kiểm tra vi phạm và hiệu quả
4. **Cấu hình**: Điều chỉnh thời gian mute, AI settings

### 3. API Integration
Bot Discord tự động đồng bộ với dashboard qua API:
- `GET /api/keywords` - Lấy từ khóa mới nhất
- `GET /api/settings` - Lấy cấu hình hiện tại

## 🚀 Deploy Options

### Option 1: Heroku (Đơn giản)
```bash
# Tạo 2 apps: 1 cho bot, 1 cho dashboard
heroku create my-discord-bot
heroku create my-bot-dashboard

# Bot app
git subtree push --prefix=bot heroku-bot main
heroku config:set DISCORD_BOT_TOKEN=xxx -a my-discord-bot
heroku config:set OPENAI_API_KEY=xxx -a my-discord-bot

# Dashboard app  
git subtree push --prefix=dashboard heroku-dash main
heroku addons:create heroku-postgresql -a my-bot-dashboard
heroku config:set FLASK_SECRET_KEY=$(openssl rand -base64 32) -a my-bot-dashboard
```

### Option 2: Railway (Khuyến nghị)
1. Connect GitHub repository
2. Create 2 services từ cùng 1 repo
3. Set start commands:
   - Bot: `python main.py`
   - Dashboard: `python web_app.py`
4. Add PostgreSQL database cho dashboard
5. Set environment variables

### Option 3: VPS/Server
```bash
# Sử dụng systemd services
sudo nano /etc/systemd/system/discord-bot.service
sudo nano /etc/systemd/system/bot-dashboard.service

sudo systemctl enable discord-bot
sudo systemctl enable bot-dashboard
sudo systemctl start discord-bot  
sudo systemctl start bot-dashboard
```

## 📊 Monitoring & Maintenance

### Logs và Debugging
```bash
# Bot logs
tail -f logs/bot_$(date +%Y%m%d).log

# Dashboard logs
tail -f dashboard.log

# Database monitoring
psql $DATABASE_URL -c "SELECT COUNT(*) FROM violation_logs;"
```

### Backup Strategy
```bash
# Backup JSON violations
cp violations.json backups/violations_$(date +%Y%m%d).json

# Backup PostgreSQL
pg_dump $DATABASE_URL > backups/dashboard_$(date +%Y%m%d).sql
```

### Performance Tips
- **Bot**: Restart hàng ngày để clear memory
- **Dashboard**: Enable database connection pooling
- **Database**: Index thường xuyên cho query optimization
- **Monitoring**: Setup uptime monitoring cho cả 2 services

## 🔧 Customization

### Thêm loại vi phạm mới
1. **config.py**: Thêm vào `VIOLATION_TYPES`
2. **forms.py**: Cập nhật choices trong forms
3. **templates**: Thêm badge colors mới

### Custom AI prompts
```python
# moderation.py - line 57
system_prompt = """
Bạn là hệ thống kiểm duyệt cho cộng đồng Việt Nam...
[Customize prompt của bạn]
"""
```

### UI Themes
```css
/* templates/base.html */
.sidebar {
    background: linear-gradient(135deg, #your-color1, #your-color2);
}
```

## 🛡️ Security Best Practices

- ✅ **Secrets management**: Sử dụng environment variables
- ✅ **Database**: PostgreSQL với SSL trong production  
- ✅ **HTTPS**: Bắt buộc cho dashboard
- ✅ **Rate limiting**: Implement cho API endpoints
- ✅ **Input validation**: Forms và API validation
- ✅ **Logs**: Không log sensitive information

## 📈 Scaling

### Horizontal Scaling
- **Bot**: Sharding cho multiple guilds
- **Dashboard**: Load balancer + multiple instances
- **Database**: Read replicas cho queries

### Performance Optimization
- **Caching**: Redis cho dashboard statistics
- **CDN**: Static assets
- **Database**: Indexes và query optimization

## 🐛 Troubleshooting

### Bot không kết nối
```
Lỗi: Invalid token / Privileged intents
```
**Giải pháp**: 
1. Kiểm tra DISCORD_BOT_TOKEN
2. Bật Message Content Intent trong Developer Portal

### Dashboard không load
```
Lỗi: Database connection failed
```
**Giải pháp**:
1. Kiểm tra DATABASE_URL format
2. Verify database credentials
3. Check firewall/network connectivity

### AI không hoạt động
```
Warning: Falling back to keyword filtering
```
**Giải pháp**: Set OPENAI_API_KEY (optional nhưng khuyến nghị)

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

## 🤝 Support & Community

- 📧 **Email**: support@example.com
- 💬 **Discord**: [Community Server](https://discord.gg/example)
- 🐛 **Issues**: [GitHub Issues](https://github.com/example/issues)
- 📚 **Wiki**: [Documentation](https://github.com/example/wiki)

## 🔄 Updates & Roadmap

### v2.0 (Coming soon)
- [ ] Real-time dashboard updates với WebSocket
- [ ] Advanced analytics với machine learning
- [ ] Multi-guild management  
- [ ] Mobile-responsive dashboard improvements
- [ ] Webhook integrations

### Contributing
1. Fork repository
2. Create feature branch
3. Submit pull request với detailed description

---

**⭐ Nếu project hữu ích, hãy star GitHub repo để support team phát triển!**

**🌟 Designed cho cộng đồng Discord Việt Nam - Tuân thủ Discord ToS và pháp luật Việt Nam**