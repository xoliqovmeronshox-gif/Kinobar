import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, filters
from config import BOT_TOKEN
from database import Database
from handlers import *

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Bot ishga tushganda"""
    db = Database()
    await db.init_db()
    logger.info("Ma'lumotlar bazasi tayyor!")

def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return
    
    # Application yaratish
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    # Admin commands
    from admin_handlers import ban_user_start, unban_user_start, broadcast_start, delete_movie_start, add_admin_start, remove_admin_start
    app.add_handler(CommandHandler("ban", ban_user_start))
    app.add_handler(CommandHandler("unban", unban_user_start))
    app.add_handler(CommandHandler("broadcast", broadcast_start))
    app.add_handler(CommandHandler("delete", delete_movie_start))
    app.add_handler(CommandHandler("addadmin", add_admin_start))
    app.add_handler(CommandHandler("removeadmin", remove_admin_start))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Callback query handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Inline query handler
    app.add_handler(InlineQueryHandler(inline_query))
    
    # Botni ishga tushirish
    logger.info("Bot ishga tushdi!")
    app.run_polling(allowed_updates=["message", "callback_query", "inline_query"])

if __name__ == '__main__':
    main()
