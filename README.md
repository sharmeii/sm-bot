# 🤖 Multi-Account Social Media Automation

Automatically post to YouTube Shorts, LinkedIn, TikTok, Pinterest, and Twitter across multiple accounts with randomized scheduling.

## ✨ Features
- 📅 Multi-account support (2+ accounts per platform)
- 🎲 Randomized posting times (looks organic)
- 🤖 Human-like behavior patterns
- 🔄 Auto-retry on failures
- 📊 PostgreSQL-powered queue

## 🚀 Quick Start

1. **Clone repo:**
```bash
   git clone https://github.com/yourusername/social-media-automation.git
   cd social-media-automation
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
   playwright install chromium
```

3. **Configure:**
```bash
   cp config/config.py.example config.py
   cp config/db_config.py.example db_config.py
   # Edit both files with your settings
```

4. **Setup database:**
   - Create PostgreSQL database: `sm_bot`
   - Run: `setup/setup.sql` in pgAdmin
   - Edit SQL file with your BitBrowser Profile IDs

5. **Start automation:**
```bash
   python core/add_video.py        # Add video
   python core/db_scheduler.py     # Start bot
```

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Daily Usage](docs/DAILY_USAGE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [FAQ](docs/FAQ.md)

## ⚠️ Important

- Never commit `config.py` or `db_config.py` (contains sensitive data)
- Login to each account manually once in BitBrowser
- Keep laptop awake while running

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Pull requests welcome! Please read CONTRIBUTING.md first.