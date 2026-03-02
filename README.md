# 🎬 Kino Bot

Professional Telegram movie bot with code-based movie access system.

## ✨ Features

- 🔢 **Code-based Access**: Users enter codes to get movies instantly
- ⭐ **Rating System**: 1-10 star rating system with statistics
- 👑 **Admin Panel**: Full admin management system
- 📊 **Statistics**: View counts, ratings, and user analytics
- 🎲 **Random Suggestions**: "What to watch today?" feature
- 🏆 **TOP Movies**: Best rated movies list
- 📢 **Subscription Check**: Mandatory channel subscription
- 🚫 **User Management**: Ban/unban system
- 📤 **Broadcast**: Send messages to all users

## 🚀 Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ADMIN_ID`: Your Telegram user ID
   - `CHANNEL_ID`: Channel ID for subscription check
4. Run: `python bot.py`

## 📋 Configuration

### Environment Variables (.env)
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
CHANNEL_ID=-1003399011554
DATABASE_PATH=bot_database.db
```

### Admin Commands
- `/admin` - Open admin panel
- `/ban user_id` - Ban user
- `/unban user_id` - Unban user
- `/addadmin user_id` - Add admin
- `/removeadmin user_id` - Remove admin

## 🎯 How It Works

1. **Admin adds movies** with custom codes (e.g., "24", "FILM001")
2. **Users enter codes** to instantly receive movies
3. **Rating system** allows users to rate movies 1-10 stars
4. **Statistics** track views, downloads, and ratings
5. **Random suggestions** help users discover new content

## 🛠 Tech Stack

- **Python 3.8+**
- **python-telegram-bot 21.0**
- **SQLite** database
- **aiosqlite** for async database operations

## 📱 Bot Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- Enter movie code (e.g., "24") - Get movie

### Admin Features
- ➕ Add movies with codes
- 📊 View statistics
- 👥 Manage users
- 📢 Broadcast messages
- 🗑 Delete movies

## 🎬 Movie Management

Movies are stored with:
- Title, description, year, genre
- Custom access codes
- File attachments (video/document)
- Rating statistics
- View counts

## 📊 Statistics

Track:
- Total users and movies
- Daily new users
- Most viewed movies
- Top rated movies
- User activity

## 🔧 Deployment

### Railway.app
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Manual Deployment
1. Set up Python environment
2. Install dependencies
3. Configure environment variables
4. Run `python bot.py`

## 📞 Support

- **Developer**: @codecrashh
- **Channel**: @kinoBar_12

## 📄 License

This project is for educational purposes.