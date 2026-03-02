from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from keyboards import *
from config import ADMIN_IDS, CHANNEL_ID
import uuid

db = Database()

async def is_admin(user_id):
    """Admin ekanligini tekshirish"""
    return await db.is_admin(user_id)

async def is_banned(user_id):
    """Foydalanuvchi bloklangan yoki yo'qligini tekshirish"""
    user = await db.get_user(user_id)
    return user and user['is_banned'] == 1

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obuna tekshirish"""
    if not CHANNEL_ID:
        return True
    
    user_id = update.effective_user.id
    
    # Admin obuna tekshirilmaydi
    if await is_admin(user_id):
        return True
    
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/kinoBar_12")],
                [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")]
            ]
            await update.message.reply_text(
                "❌ Botdan foydalanish uchun kanalga obuna bo'ling!\n\n"
                "📢 Kanal: @kinoBar_12\n\n"
                "Obuna bo'lgandan keyin 'Obunani tekshirish' tugmasini bosing.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return False
    except Exception as e:
        # Xatolik bo'lsa, obuna tekshirilmaydi
        return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    
    # Foydalanuvchini bazaga qo'shish
    await db.add_user(user.id, user.username or '', user.first_name or '')
    
    # Bloklangan foydalanuvchilarni tekshirish
    if await is_banned(user.id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    # Obuna tekshirish
    if not await check_subscription(update, context):
        return
    
    welcome_text = f"""
👋 Assalomu alaykum, {user.first_name}!

🎬 Kino botga xush kelibsiz!

🔢 Kino ko'rish uchun kod kiriting.
Masalan: 24

💡 Kod admin tomonidan beriladi.

📞 Murojaat: @codecrashh
📢 Kanal: @kinoBar_12
"""
    
    if await is_admin(user.id):
        await update.message.reply_text(
            welcome_text + "\n\n👑 Siz admin sifatida tizimga kirdingiz!",
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(welcome_text, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam komandasi"""
    help_text = """
📖 Bot qo'llanmasi:

🔢 Kod kiriting:
- "Kod kiriting" tugmasini bosing
- Yoki kodni to'g'ridan-to'g'ri yozing
- Masalan: 24

💡 Kod admin tomonidan beriladi.

👨‍💼 Admin:
/admin - Admin panel
"""
    await update.message.reply_text(help_text)


async def search_movies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino qidirish"""
    if await is_banned(update.effective_user.id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    await update.message.reply_text(
        "🔍 Qidirmoqchi bo'lgan kino nomini yozing:",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_search'

async def list_all_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha kinolarni ko'rsatish"""
    if await is_banned(update.effective_user.id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    movies = await db.get_all_movies(limit=10, offset=0)
    
    if not movies:
        await update.message.reply_text("📭 Hozircha kinolar mavjud emas.")
        return
    
    await update.message.reply_text(
        "📋 Barcha kinolar:",
        reply_markup=movies_list_keyboard(movies, page=0)
    )

async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot haqida"""
    about_text = """
ℹ️ Bot haqida ma'lumot:

🎬 Kino Bot - kod orqali kino ko'rish boti

✨ Qanday ishlaydi:
• Admin sizga kod beradi
• Siz kodni kiritasiz
• Bot kinoni yuboradi

📊 Oddiy va qulay!

📞 Murojaat: @codecrashh
📢 Kanal: @kinoBar_12
"""
    await update.message.reply_text(about_text)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aloqa"""
    contact_text = """
📞 Aloqa:

📧 Murojaat uchun: @codecrashh
📢 Kanal: @kinoBar_12

💡 Takliflar va shikoyatlar uchun admin bilan bog'laning.
"""
    await update.message.reply_text(contact_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Matn xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if await is_banned(user_id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    # Obuna tekshirish
    if not await check_subscription(update, context):
        return
    
    state = context.user_data.get('state')
    
    # Bekor qilish
    if text == '❌ Bekor qilish':
        context.user_data.clear()
        if await is_admin(user_id):
            await update.message.reply_text("✅ Bekor qilindi", reply_markup=admin_keyboard())
        else:
            await update.message.reply_text("✅ Bekor qilindi", reply_markup=main_keyboard())
        return
    
    # Kod orqali kino qidirish (masalan: FILM0001)
    if text.upper().startswith('FILM') and len(text) == 8:
        movie = await db.get_movie_by_code(text)
        if movie:
            # Kinoni to'g'ridan-to'g'ri yuborish
            await update.message.reply_text(f"🎬 <b>{movie['title']}</b>\n\n📝 {movie['description'] or 'Tavsif yo\'q'}\n📅 Yil: {movie['year'] or 'Noma\'lum'}\n🎭 Janr: {movie['genre'] or 'Noma\'lum'}", parse_mode=ParseMode.HTML)
            
            # Statistika
            await db.log_action(user_id, movie['id'], 'view')
            
            # Faylni yuborish
            if movie['file_type'] == 'video':
                await update.message.reply_video(
                    video=movie['file_id'],
                    caption=f"🎬 {movie['title']}\n\n🔢 Kod: {text.upper()}"
                )
            elif movie['file_type'] == 'document':
                await update.message.reply_document(
                    document=movie['file_id'],
                    caption=f"🎬 {movie['title']}\n\n🔢 Kod: {text.upper()}"
                )
            return
        else:
            await update.message.reply_text(f"❌ '{text}' kodi bo'yicha kino topilmadi.\n\n💡 To'g'ri kod kiriting (masalan: FILM0001)")
            return
    
    # Asosiy tugmalar
    if text == '🔢 Kod kiriting':
        await update.message.reply_text(
            "🔢 Kino kodini kiriting:\n\nMasalan: 24",
            reply_markup=cancel_keyboard()
        )
        context.user_data['state'] = 'waiting_code'
        return
    elif text == '🎲 Bugun nima ko\'ray?':
        await random_movies_suggestion(update, context)
        return
    elif text == '🏆 TOP filmlar':
        await top_movies_list(update, context)
        return
    elif text == 'ℹ️ Bot haqida':
        await about_bot(update, context)
        return
    elif text == '📞 Aloqa':
        await contact_handler(update, context)
        return
    
    # Admin tugmalari
    if await is_admin(user_id):
        if text == '➕ Kino qo\'shish':
            await add_movie_start(update, context)
            return
        elif text == '📊 Statistika':
            await show_stats(update, context)
            return
        elif text == '🗑 Kino o\'chirish':
            from admin_handlers import delete_movie_start
            await delete_movie_start(update, context)
            return
        elif text == '📢 Xabar yuborish':
            from admin_handlers import broadcast_start
            await broadcast_start(update, context)
            return
        elif text == '👥 Foydalanuvchilar':
            from admin_handlers import list_users
            await list_users(update, context)
            return
        elif text == '🚫 Ban/Unban':
            await update.message.reply_text(
                "🚫 Ban/Unban menyusi:\n\n"
                "Foydalanuvchini bloklash: /ban user_id\n"
                "Foydalanuvchini blokdan chiqarish: /unban user_id",
                reply_markup=admin_keyboard()
            )
            return
        elif text == '👑 Adminlar':
            from admin_handlers import list_admins
            await list_admins(update, context)
            return
        elif text == '➕ Admin qo\'shish':
            from admin_handlers import add_admin_start
            await add_admin_start(update, context)
            return
        elif text == '🔙 Orqaga':
            await update.message.reply_text("🏠 Asosiy menyu", reply_markup=main_keyboard())
            return
    
    # Holatlar bo'yicha qayta ishlash
    if state == 'waiting_code':
        movie = await db.get_movie_by_code(text)
        if movie:
            await send_movie_by_code(update, context, movie)
        else:
            await update.message.reply_text(
                f"❌ '{text}' kodi bo'yicha kino topilmadi.\n\n💡 Kodni to'g'ri kiriting.",
                reply_markup=main_keyboard()
            )
        context.user_data.clear()
        return
    elif state == 'waiting_movie_file':
        await process_movie_file(update, context)
    elif state == 'waiting_movie_title':
        context.user_data['movie_title'] = text
        await update.message.reply_text("📝 Kino tavsifini yozing (ixtiyoriy):")
        context.user_data['state'] = 'waiting_movie_description'
    elif state == 'waiting_movie_description':
        context.user_data['movie_description'] = text
        await update.message.reply_text("🔢 Kino kodini kiriting (masalan: 24):")
        context.user_data['state'] = 'waiting_movie_code'
    elif state == 'waiting_movie_code':
        context.user_data['movie_code'] = text
        await update.message.reply_text("📅 Kino yilini kiriting (ixtiyoriy):")
        context.user_data['state'] = 'waiting_movie_year'
    elif state == 'waiting_movie_year':
        context.user_data['movie_year'] = text if text.isdigit() else None
        await update.message.reply_text("🎭 Janrini kiriting (ixtiyoriy):")
        context.user_data['state'] = 'waiting_movie_genre'
    elif state == 'waiting_movie_genre':
        await save_movie(update, context, text)
    elif state == 'waiting_broadcast':
        from admin_handlers import process_broadcast
        await process_broadcast(update, context)
    elif state == 'waiting_broadcast_type':
        if text == '📢 Hammaga xabar':
            await update.message.reply_text(
                "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:",
                reply_markup=cancel_keyboard()
            )
            context.user_data['state'] = 'waiting_broadcast'
        elif text == '👤 Bitta odamga xabar':
            await update.message.reply_text(
                "👤 Foydalanuvchi ID sini kiriting:",
                reply_markup=cancel_keyboard()
            )
            context.user_data['state'] = 'waiting_target_user_id'
        return
    elif state == 'waiting_target_user_id':
        try:
            target_id = int(text)
            context.user_data['target_user_id'] = target_id
            await update.message.reply_text(
                "📝 Xabar matnini yozing:",
                reply_markup=cancel_keyboard()
            )
            context.user_data['state'] = 'waiting_single_message'
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri ID. Raqam kiriting.")
        return
    elif state == 'waiting_single_message':
        from admin_handlers import process_single_message
        await process_single_message(update, context)
    elif state == 'waiting_delete_id':
        from admin_handlers import process_delete
        await process_delete(update, context)
    elif state == 'waiting_ban_id':
        from admin_handlers import process_ban
        await process_ban(update, context)
    elif state == 'waiting_unban_id':
        from admin_handlers import process_unban
        await process_unban(update, context)
    elif state == 'waiting_add_admin_id':
        from admin_handlers import process_add_admin
        await process_add_admin(update, context)
    elif state == 'waiting_remove_admin_id':
        from admin_handlers import process_remove_admin
        await process_remove_admin(update, context)
    else:
        # Kod bo'yicha qidiruv
        movie = await db.get_movie_by_code(text)
        if movie:
            await send_movie_by_code(update, context, movie)
        else:
            await update.message.reply_text(
                f"❌ '{text}' kodi bo'yicha kino topilmadi.\n\n💡 Kodni to'g'ri kiriting yoki 'Kod kiriting' tugmasini bosing.",
                reply_markup=main_keyboard()
            )

async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    """Qidiruv natijalarini qayta ishlash"""
    movies = await db.search_movies(query)
    
    if not movies:
        await update.message.reply_text(
            f"❌ '{query}' bo'yicha natija topilmadi.\n\n💡 Boshqa nom bilan qidiring.",
            reply_markup=main_keyboard() if not await is_admin(update.effective_user.id) else admin_keyboard()
        )
        context.user_data.clear()
        return
    
    await update.message.reply_text(
        f"🔍 '{query}' bo'yicha {len(movies)} ta natija topildi:",
        reply_markup=movies_list_keyboard(movies, page=0)
    )
    context.user_data.clear()


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugmalar callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    # Reyting berish
    if data.startswith('rate_'):
        parts = data.split('_')
        movie_id = int(parts[1])
        rating = int(parts[2])
        
        await db.add_rating(user_id, movie_id, rating)
        await query.answer(f"✅ {rating}/10 baho berildi!", show_alert=True)
        
        # Xabarni yangilash
        movie = await db.get_movie_by_id(movie_id)
        if movie:
            avg_rating, total_ratings = await db.get_movie_rating(movie_id)
            user_rating = await db.get_user_rating(user_id, movie_id)
            
            # Reyting tugmalari
            rating_buttons = []
            for i in range(1, 11):
                star = "⭐" if user_rating and i <= user_rating else "☆"
                rating_buttons.append(
                    InlineKeyboardButton(f"{star}{i}", callback_data=f"rate_{movie_id}_{i}")
                )
            
            keyboard = [
                rating_buttons[0:5],
                rating_buttons[5:10],
                [InlineKeyboardButton("📥 Yuklab olish", callback_data=f"download_{movie_id}")]
            ]
            
            rating_text = f"⭐ {avg_rating:.1f}/10 ({total_ratings} baho)"
            your_rating = f"\n👤 Sizning bahongiz: {user_rating}/10"
            
            new_caption = f"""🎬 <b>{movie['title']}</b>

📝 {movie['description'] or 'Tavsif mavjud emas'}
📅 Yil: {movie['year'] or 'Noma\'lum'}
🎭 Janr: {movie['genre'] or 'Noma\'lum'}
🔢 Kod: {movie['code']}

{rating_text}{your_rating}"""
            
            try:
                await query.message.edit_caption(
                    caption=new_caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
        return
    
    # Obunani tekshirish
    if data == "check_sub":
        if not CHANNEL_ID:
            await query.message.edit_text("✅ Obuna tekshiruvi o'chirilgan.")
            return
        
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                await query.message.edit_text(
                    "✅ Obuna tasdiqlandi!\n\n"
                    "Endi botdan foydalanishingiz mumkin.\n"
                    "/start ni bosing."
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/kinoBar_12")],
                    [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")]
                ]
                await query.message.edit_text(
                    "❌ Siz hali kanalga obuna bo'lmadingiz!\n\n"
                    "📢 Kanal: @kinoBar_12\n\n"
                    "Obuna bo'lgandan keyin qayta tekshiring.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e:
            await query.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        return
    
    if await is_banned(user_id):
        await query.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    # Kino ko'rish
    if data.startswith('movie_'):
        movie_id = int(data.split('_')[1])
        movie = await db.get_movie_by_id(movie_id)
        
        if not movie:
            await query.message.edit_text("❌ Kino topilmadi.")
            return
        
        # Statistika
        await db.log_action(user_id, movie_id, 'view')
        
        movie_info = f"""
🎬 <b>{movie['title']}</b>

📝 Tavsif: {movie['description'] or 'Mavjud emas'}
📅 Yil: {movie['year'] or 'Noma\'lum'}
🎭 Janr: {movie['genre'] or 'Noma\'lum'}
"""
        
        await query.message.edit_text(
            movie_info,
            parse_mode=ParseMode.HTML,
            reply_markup=movie_inline_keyboard(movie_id)
        )
    
    # Kino yuklab olish
    elif data.startswith('download_'):
        movie_id = int(data.split('_')[1])
        movie = await db.get_movie_by_id(movie_id)
        
        if not movie:
            await query.answer("❌ Kino topilmadi.", show_alert=True)
            return
        
        # Statistika
        await db.log_action(user_id, movie_id, 'download')
        
        await query.answer("📥 Yuklab olinmoqda...", show_alert=False)
        
        # Faylni qayta yuborish (yuklab olish uchun)
        try:
            caption = f"🎬 {movie['title']}\n\n📥 Yuklab olindi!"
            
            if movie['file_type'] == 'video':
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=movie['file_id'],
                    caption=caption
                )
            elif movie['file_type'] == 'document':
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=movie['file_id'],
                    caption=caption
                )
        except Exception as e:
            await query.answer(f"❌ Xatolik: {str(e)}", show_alert=True)
        return
    
    # Sahifalash
    elif data.startswith('page_'):
        page = int(data.split('_')[1])
        movies = await db.get_all_movies(limit=10, offset=page*10)
        
        if movies:
            await query.message.edit_text(
                f"📋 Kinolar (sahifa {page + 1}):",
                reply_markup=movies_list_keyboard(movies, page=page)
            )
    
    # O'chirishni tasdiqlash
    elif data.startswith('confirm_delete_'):
        movie_id = int(data.split('_')[2])
        from admin_handlers import confirm_delete
        await confirm_delete(update, context, movie_id)
    elif data == 'cancel_delete':
        await query.message.edit_text("❌ O'chirish bekor qilindi.")
    
    # Orqaga
    elif data == 'back_to_search':
        await query.message.edit_text("🔍 Yangi qidiruv uchun kino nomini yozing:")
    elif data == 'back_to_main':
        await query.message.delete()

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline qidiruv"""
    query = update.inline_query.query
    user_id = update.effective_user.id
    
    if await is_banned(user_id):
        return
    
    if not query:
        return
    
    movies = await db.search_movies(query)
    
    results = []
    for movie in movies[:50]:  # Maksimal 50 ta natija
        movie_info = f"""
🎬 {movie['title']}

📝 {movie['description'] or 'Tavsif mavjud emas'}
📅 Yil: {movie['year'] or 'Noma\'lum'}
🎭 Janr: {movie['genre'] or 'Noma\'lum'}

📥 Yuklab olish uchun botga o'ting: @{context.bot.username}
"""
        
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=movie['title'],
                description=f"{movie['genre'] or ''} • {movie['year'] or ''}",
                input_message_content=InputTextMessageContent(
                    message_text=movie_info,
                    parse_mode=ParseMode.HTML
                ),
                thumb_url="https://via.placeholder.com/150"
            )
        )
    
    await update.inline_query.answer(results, cache_time=300)

# Admin handlers
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    await update.message.reply_text(
        "👑 Admin panel",
        reply_markup=admin_keyboard()
    )

async def add_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino qo'shishni boshlash"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    await update.message.reply_text(
        "📤 Kino faylini yuboring (video yoki document):",
        reply_markup=cancel_keyboard()
    )
    context.user_data['state'] = 'waiting_movie_file'

async def process_movie_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino faylini qayta ishlash"""
    message = update.message
    
    if message.video:
        context.user_data['file_id'] = message.video.file_id
        context.user_data['file_type'] = 'video'
    elif message.document:
        context.user_data['file_id'] = message.document.file_id
        context.user_data['file_type'] = 'document'
    else:
        await message.reply_text("❌ Iltimos, video yoki document fayl yuboring.")
        return
    
    await message.reply_text("📝 Kino nomini kiriting:")
    context.user_data['state'] = 'waiting_movie_title'

async def save_movie(update: Update, context: ContextTypes.DEFAULT_TYPE, genre: str):
    """Kinoni saqlash"""
    user_data = context.user_data
    
    movie_id = await db.add_movie(
        title=user_data.get('movie_title'),
        file_id=user_data.get('file_id'),
        file_type=user_data.get('file_type'),
        description=user_data.get('movie_description', ''),
        year=user_data.get('movie_year'),
        genre=genre,
        code=user_data.get('movie_code'),
        added_by=update.effective_user.id
    )
    
    await update.message.reply_text(
        f"✅ Kino muvaffaqiyatli qo'shildi!\n\n"
        f"🆔 ID: {movie_id}\n"
        f"🎬 Nom: {user_data.get('movie_title')}\n"
        f"🔢 Kod: <code>{user_data.get('movie_code')}</code>\n\n"
        f"💡 Foydalanuvchilar bu kodni yozib kinoni ko'rishlari mumkin!",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_keyboard()
    )
    
    context.user_data.clear()

async def send_movie_by_code(update: Update, context: ContextTypes.DEFAULT_TYPE, movie):
    """Kod bo'yicha kinoni yuborish"""
    user_id = update.effective_user.id
    
    # Statistika
    await db.log_action(user_id, movie['id'], 'code_view')
    
    # Reyting olish
    avg_rating, total_ratings = await db.get_movie_rating(movie['id'])
    user_rating = await db.get_user_rating(user_id, movie['id'])
    
    # Reyting tugmalari
    rating_buttons = []
    for i in range(1, 11):
        star = "⭐" if user_rating and i <= user_rating else "☆"
        rating_buttons.append(
            InlineKeyboardButton(f"{star}{i}", callback_data=f"rate_{movie['id']}_{i}")
        )
    
    # 5 tadan 2 qator
    keyboard = [
        rating_buttons[0:5],
        rating_buttons[5:10],
        [InlineKeyboardButton("📥 Yuklab olish", callback_data=f"download_{movie['id']}")]
    ]
    
    # Kino ma'lumotlari
    rating_text = f"⭐ {avg_rating:.1f}/10 ({total_ratings} baho)" if total_ratings > 0 else "⭐ Hali baholanmagan"
    your_rating = f"\n👤 Sizning bahongiz: {user_rating}/10" if user_rating else ""
    
    caption = f"""🎬 <b>{movie['title']}</b>

📝 {movie['description'] or 'Tavsif mavjud emas'}
📅 Yil: {movie['year'] or 'Noma\'lum'}
🎭 Janr: {movie['genre'] or 'Noma\'lum'}
🔢 Kod: {movie['code']}

{rating_text}{your_rating}"""
    
    # Faylni yuborish
    try:
        if movie['file_type'] == 'video':
            await context.bot.send_video(
                chat_id=update.message.chat_id,
                video=movie['file_id'],
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif movie['file_type'] == 'document':
            await context.bot.send_document(
                chat_id=update.message.chat_id,
                document=movie['file_id'],
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistikani ko'rsatish"""
    user_id = update.effective_user.id
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return
    
    stats = await db.get_stats()
    
    # Eng ko'p ko'rilgan kinolar
    top_viewed = await db.get_most_viewed_movies(5)
    viewed_text = "\n\n📊 <b>Eng ko'p ko'rilgan kinolar:</b>\n"
    for i, movie in enumerate(top_viewed, 1):
        viewed_text += f"{i}. {movie['title']} - {movie['view_count']} marta\n"
    
    # Eng yuqori reytingli kinolar
    top_rated = await db.get_top_rated_movies(5)
    rated_text = "\n\n⭐ <b>Eng yuqori reytingli kinolar:</b>\n"
    for i, movie in enumerate(top_rated, 1):
        rated_text += f"{i}. {movie['title']} - {movie['avg_rating']:.1f}/10 ({movie['total_ratings']} baho)\n"
    
    stats_text = f"""
📊 <b>Bot statistikasi:</b>

👥 Jami foydalanuvchilar: {stats['total_users']}
🎬 Jami kinolar: {stats['total_movies']}
📈 Bugungi yangi foydalanuvchilar: {stats['today_users']}
{viewed_text}{rated_text}
"""
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Video fayllarni qayta ishlash"""
    state = context.user_data.get('state')
    
    if state == 'waiting_movie_file':
        await process_movie_file(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Document fayllarni qayta ishlash"""
    state = context.user_data.get('state')
    
    if state == 'waiting_movie_file':
        await process_movie_file(update, context)

async def random_movies_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tasodifiy filmlar taklifi"""
    if await is_banned(update.effective_user.id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    # Obuna tekshirish
    if not await check_subscription(update, context):
        return
    
    movies = await db.get_random_movies(3)
    
    if not movies:
        await update.message.reply_text("❌ Hozircha kinolar mavjud emas.")
        return
    
    text = "🎲 <b>Bugun sizga taklif qilamiz:</b>\n\n"
    
    for i, movie in enumerate(movies, 1):
        # Reyting olish
        avg_rating, total_ratings = await db.get_movie_rating(movie['id'])
        rating_text = f"⭐ {avg_rating:.1f}/10" if total_ratings > 0 else "⭐ Baholanmagan"
        
        text += f"{i}. <b>{movie['title']}</b>\n"
        text += f"   🔢 Kod: <code>{movie['code']}</code>\n"
        text += f"   📅 {movie['year'] or 'Noma\'lum'} • {rating_text}\n"
        text += f"   🎭 {movie['genre'] or 'Janr ko\'rsatilmagan'}\n\n"
    
    text += "💡 Kodni yozing va kinoni ko'ring!"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def top_movies_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TOP filmlar ro'yxati"""
    if await is_banned(update.effective_user.id):
        await update.message.reply_text("❌ Siz botdan foydalanish huquqidan mahrum qilindingiz.")
        return
    
    # Obuna tekshirish
    if not await check_subscription(update, context):
        return
    
    top_movies = await db.get_top_rated_movies(10)
    
    if not top_movies:
        await update.message.reply_text("❌ Hozircha reytingli kinolar yo'q.")
        return
    
    text = "🏆 <b>TOP reytingli filmlar:</b>\n\n"
    
    for i, movie in enumerate(top_movies, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        text += f"{medal} <b>{movie['title']}</b>\n"
        text += f"   🔢 Kod: <code>{movie['code']}</code>\n"
        text += f"   ⭐ {movie['avg_rating']:.1f}/10 ({movie['total_ratings']} baho)\n"
        text += f"   📅 {movie['year'] or 'Noma\'lum'} • 🎭 {movie['genre'] or 'Janr yo\'q'}\n\n"
    
    text += "💡 Kodni yozing va eng yaxshi filmlarni ko'ring!"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)