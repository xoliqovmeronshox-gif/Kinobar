from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def main_keyboard():
    """Asosiy klaviatura"""
    keyboard = [
        ['🔢 Kod kiriting', '🎲 Bugun nima ko\'ray?'],
        ['🏆 TOP filmlar', 'ℹ️ Bot haqida'],
        ['📞 Aloqa']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_keyboard():
    """Admin klaviaturasi"""
    keyboard = [
        ['➕ Kino qo\'shish', '🗑 Kino o\'chirish'],
        ['📊 Statistika', '📢 Xabar yuborish'],
        ['👥 Foydalanuvchilar', '🚫 Ban/Unban'],
        ['👑 Adminlar', '➕ Admin qo\'shish'],
        ['🔙 Orqaga']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    """Bekor qilish klaviaturasi"""
    keyboard = [['❌ Bekor qilish']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def movie_inline_keyboard(movie_id):
    """Kino uchun inline klaviatura"""
    keyboard = [
        [InlineKeyboardButton("📥 Yuklab olish", callback_data=f"download_{movie_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_search")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movies_list_keyboard(movies, page=0):
    """Kinolar ro'yxati uchun inline klaviatura"""
    keyboard = []
    
    for movie in movies:
        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {movie['title']}", 
                callback_data=f"movie_{movie['id']}"
            )
        ])
    
    # Sahifalash tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main"))
    if len(movies) >= 10:
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def admin_movie_keyboard(movie_id):
    """Admin uchun kino boshqaruv klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_{movie_id}"),
            InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{movie_id}")
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_delete_keyboard(movie_id):
    """O'chirishni tasdiqlash klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"confirm_delete_{movie_id}"),
            InlineKeyboardButton("❌ Yo'q", callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
