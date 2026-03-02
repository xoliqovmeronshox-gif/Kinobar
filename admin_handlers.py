from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from keyboards import *
from config import ADMIN_IDS

db = Database()

async def is_admin(user_id):
    """Admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ommaviy xabar yuborishni boshlash"""
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    keyboard = [
        ['📢 Hammaga xabar', '👤 Bitta odamga xabar'],
        ['❌ Bekor qilish']
    ]
    
    await update.message.reply_text(
        "📢 Xabar yuborish:\n\nTanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data['state'] = 'waiting_broadcast_type'

async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ommaviy xabar yuborish"""
    message_text = update.message.text
    
    await update.message.reply_text("📤 Xabar yuborilmoqda...")
    
    # Barcha foydalanuvchilarni olish
    conn = await db.get_connection()
    try:
        rows = await conn.fetch('SELECT user_id FROM users WHERE is_banned = 0')
        users = [row['user_id'] for row in rows]
    finally:
        await conn.close()
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Xabar:</b>\n\n{message_text}",
                parse_mode=ParseMode.HTML
            )
            success += 1
        except Exception as e:
            failed += 1
            continue
    
    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"❌ Xatolik: {failed}",
        reply_markup=admin_keyboard()
    )
    
    context.user_data.clear()

async def process_single_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bitta odamga xabar yuborish"""
    message_text = update.message.text
    target_user_id = context.user_data.get('target_user_id')
    
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"📢 <b>Admin xabari:</b>\n\n{message_text}",
            parse_mode=ParseMode.HTML
        )
        
        user = await db.get_user(target_user_id)
        user_name = user['first_name'] if user else "Noma'lum"
        
        await update.message.reply_text(
            f"✅ Xabar yuborildi!\n\n"
            f"👤 {user_name}\n"
            f"🆔 ID: {target_user_id}",
            reply_markup=admin_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Xabar yuborilmadi!\n\n"
            f"Xatolik: {str(e)}",
            reply_markup=admin_keyboard()
        )
    
    context.user_data.clear()

async def delete_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino o'chirishni boshlash"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    await update.message.reply_text(
        "🗑 O'chirmoqchi bo'lgan kino ID sini kiriting:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_delete_id'

async def process_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kinoni o'chirish"""
    try:
        movie_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    movie = await db.get_movie_by_id(movie_id)
    
    if not movie:
        await update.message.reply_text("❌ Bunday ID li kino topilmadi.")
        return
    
    await update.message.reply_text(
        f"🎬 Kino: {movie['title']}\n\n"
        f"❓ Rostdan ham o'chirmoqchimisiz?",
        reply_markup=confirm_delete_keyboard(movie_id)
    )

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE, movie_id: int):
    """O'chirishni tasdiqlash"""
    query = update.callback_query
    
    movie = await db.get_movie_by_id(movie_id)
    if movie:
        await db.delete_movie(movie_id)
        await query.message.edit_text(
            f"✅ '{movie['title']}' kinosi o'chirildi!"
        )
    else:
        await query.message.edit_text("❌ Kino topilmadi.")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar ro'yxati"""
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    conn = await db.get_connection()
    try:
        rows = await conn.fetch('''
            SELECT user_id, username, first_name, is_banned, join_date 
            FROM users 
            ORDER BY join_date DESC 
            LIMIT 20
        ''')
        users = [dict(row) for row in rows]
    finally:
        await conn.close()
    
    if not users:
        await update.message.reply_text("📭 Foydalanuvchilar topilmadi.")
        return
    
    text = "👥 <b>Oxirgi 20 ta foydalanuvchi:</b>\n\n"
    
    for user in users:
        status = "🚫 Bloklangan" if user['is_banned'] else "✅ Faol"
        username = f"@{user['username']}" if user['username'] else "Username yo'q"
        text += f"• {user['first_name']} ({username})\n"
        text += f"  ID: <code>{user['user_id']}</code> | {status}\n\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def ban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini bloklashni boshlash"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    await update.message.reply_text(
        "🚫 Bloklash uchun foydalanuvchi ID sini kiriting:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_ban_id'

async def process_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini bloklash"""
    try:
        ban_user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    if ban_user_id in ADMIN_IDS:
        await update.message.reply_text("❌ Adminni bloklash mumkin emas!")
        return
    
    user = await db.get_user(ban_user_id)
    
    if not user:
        await update.message.reply_text("❌ Bunday foydalanuvchi topilmadi.")
        return
    
    await db.ban_user(ban_user_id)
    
    await update.message.reply_text(
        f"✅ Foydalanuvchi bloklandi!\n\n"
        f"👤 {user['first_name']}\n"
        f"🆔 ID: {ban_user_id}",
        reply_markup=admin_keyboard()
    )
    
    context.user_data.clear()

async def unban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini blokdan chiqarishni boshlash"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    await update.message.reply_text(
        "✅ Blokdan chiqarish uchun foydalanuvchi ID sini kiriting:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_unban_id'

async def process_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini blokdan chiqarish"""
    try:
        unban_user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    user = await db.get_user(unban_user_id)
    
    if not user:
        await update.message.reply_text("❌ Bunday foydalanuvchi topilmadi.")
        return
    
    await db.unban_user(unban_user_id)
    
    await update.message.reply_text(
        f"✅ Foydalanuvchi blokdan chiqarildi!\n\n"
        f"👤 {user['first_name']}\n"
        f"🆔 ID: {unban_user_id}",
        reply_markup=admin_keyboard()
    )
    
    context.user_data.clear()




async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin qo'shishni boshlash"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Faqat asosiy admin bu funksiyadan foydalana oladi.")
        return
    
    await update.message.reply_text(
        "👤 Admin qo'shish uchun foydalanuvchi ID sini kiriting:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_add_admin_id'

async def process_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin qo'shish"""
    try:
        new_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    if new_admin_id in ADMIN_IDS:
        await update.message.reply_text("❌ Bu foydalanuvchi allaqachon asosiy admin!")
        return
    
    await db.add_admin(new_admin_id, update.effective_user.id)
    
    user = await db.get_user(new_admin_id)
    user_name = user['first_name'] if user else "Noma'lum"
    
    await update.message.reply_text(
        f"✅ Admin qo'shildi!\n\n"
        f"👤 {user_name}\n"
        f"🆔 ID: {new_admin_id}\n\n"
        f"Endi u kino qo'shish va boshqa admin funksiyalaridan foydalana oladi.",
        reply_markup=admin_keyboard()
    )
    
    # Yangi adminga xabar yuborish
    try:
        await context.bot.send_message(
            chat_id=new_admin_id,
            text="🎉 Tabriklaymiz! Siz admin qilib tayinlandingiz!\n\n"
                 "Endi /admin komandasi orqali admin paneliga kirishingiz mumkin."
        )
    except:
        pass
    
    context.user_data.clear()

async def remove_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminni o'chirishni boshlash"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Faqat asosiy admin bu funksiyadan foydalana oladi.")
        return
    
    await update.message.reply_text(
        "🗑 O'chirish uchun admin ID sini kiriting:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_remove_admin_id'

async def process_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminni o'chirish"""
    try:
        remove_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    
    if remove_admin_id in ADMIN_IDS:
        await update.message.reply_text("❌ Asosiy adminni o'chirish mumkin emas!")
        return
    
    await db.remove_admin(remove_admin_id)
    
    user = await db.get_user(remove_admin_id)
    user_name = user['first_name'] if user else "Noma'lum"
    
    await update.message.reply_text(
        f"✅ Admin o'chirildi!\n\n"
        f"👤 {user_name}\n"
        f"🆔 ID: {remove_admin_id}",
        reply_markup=admin_keyboard()
    )
    
    context.user_data.clear()

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminlar ro'yxati"""
    user_id = update.effective_user.id
    
    if not await db.is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    # Asosiy adminlar
    text = "👑 <b>Adminlar ro'yxati:</b>\n\n"
    text += "🔹 <b>Asosiy adminlar:</b>\n"
    for admin_id in ADMIN_IDS:
        user = await db.get_user(admin_id)
        if user:
            username = f"@{user['username']}" if user['username'] else "Username yo'q"
            text += f"• {user['first_name']} ({username})\n"
            text += f"  ID: <code>{admin_id}</code>\n\n"
        else:
            text += f"• ID: <code>{admin_id}</code>\n\n"
    
    # Qo'shilgan adminlar
    admins = await db.get_all_admins()
    if admins:
        text += "\n🔹 <b>Qo'shilgan adminlar:</b>\n"
        for admin in admins:
            user = await db.get_user(admin['user_id'])
            if user:
                username = f"@{user['username']}" if user['username'] else "Username yo'q"
                text += f"• {user['first_name']} ({username})\n"
                text += f"  ID: <code>{admin['user_id']}</code>\n\n"
            else:
                text += f"• ID: <code>{admin['user_id']}</code>\n\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
