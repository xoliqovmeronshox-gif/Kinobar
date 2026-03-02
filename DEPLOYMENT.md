# 🚀 Deployment Guide

## Railway.app Deployment (Recommended)

### Step 1: Prepare Repository
1. Create a GitHub repository
2. Push all files to the repository
3. Make sure `.env` is in `.gitignore` (already configured)

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python project

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```
BOT_TOKEN=8213210310:AAEfVfHwlf5_MQ3kkzGldmIp1sEHEvjcnUg
ADMIN_ID=7819381670
CHANNEL_ID=-1003399011554
DATABASE_PATH=bot_database.db
```

### Step 4: Deploy
1. Railway will automatically build and deploy
2. Check logs to ensure bot started successfully
3. Test the bot in Telegram

## Manual VPS Deployment

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip git -y

# Clone repository
git clone https://github.com/yourusername/kino-bot.git
cd kino-bot
```

### Step 2: Install Dependencies
```bash
# Install requirements
pip3 install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### Step 4: Run Bot
```bash
# Run directly
python3 bot.py

# Or use screen for background running
screen -S kinobot
python3 bot.py
# Press Ctrl+A then D to detach
```

### Step 5: Setup Systemd Service (Optional)
```bash
# Create service file
sudo nano /etc/systemd/system/kinobot.service
```

Add this content:
```ini
[Unit]
Description=Kino Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/kino-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kinobot
sudo systemctl start kinobot
sudo systemctl status kinobot
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABC-DEF...` |
| `ADMIN_ID` | Your Telegram user ID | `7819381670` |
| `CHANNEL_ID` | Channel ID for subscription check | `-1003399011554` |
| `DATABASE_PATH` | SQLite database file path | `bot_database.db` |

## Troubleshooting

### Bot Not Starting
- Check bot token is correct
- Verify all environment variables are set
- Check Python version (3.8+ required)

### Database Issues
- Ensure write permissions for database file
- Check SQLite is installed

### Telegram API Issues
- Verify bot token with @BotFather
- Check network connectivity
- Ensure bot is not running elsewhere

## Monitoring

### Railway Logs
- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts

### Manual Monitoring
```bash
# Check bot process
ps aux | grep bot.py

# View logs (if using systemd)
sudo journalctl -u kinobot -f

# Check database
sqlite3 bot_database.db ".tables"
```

## Backup

### Database Backup
```bash
# Create backup
cp bot_database.db bot_database_backup_$(date +%Y%m%d).db

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp bot_database.db backups/bot_database_$DATE.db
find backups/ -name "*.db" -mtime +7 -delete
```

## Updates

### Railway Auto-Deploy
- Push changes to GitHub
- Railway automatically redeploys

### Manual Update
```bash
git pull origin main
sudo systemctl restart kinobot
```