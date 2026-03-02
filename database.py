import aiosqlite
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Kinolar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    description TEXT,
                    year INTEGER,
                    genre TEXT,
                    code TEXT,
                    added_by INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Foydalanuvchilar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned INTEGER DEFAULT 0
                )
            ''')
            
            # Statistika jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_id INTEGER,
                    action_type TEXT,
                    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Adminlar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reytinglar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_id INTEGER,
                    rating INTEGER,
                    rated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, movie_id)
                )
            ''')
            
            # Referallar jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    referred_by INTEGER,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
            ''')
            
            # Konkurs jadvali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS contest (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    prize TEXT,
                    required_referrals INTEGER,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    winner_user_id INTEGER
                )
            ''')
            
            await db.commit()
    
    async def add_movie(self, title, file_id, file_type, description='', year=None, genre='', code=None, added_by=None):
        """Kino qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO movies (title, file_id, file_type, description, year, genre, code, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, file_id, file_type, description, year, genre, code, added_by))
            await db.commit()
            cursor = await db.execute('SELECT last_insert_rowid()')
            movie_id = (await cursor.fetchone())[0]
            return movie_id
    
    async def get_movie_by_code(self, code):
        """Kod bo'yicha kino olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM movies WHERE code = ?', (code,)) as cursor:
                return await cursor.fetchone()
    
    async def search_movies(self, query):
        """Kino qidirish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM movies 
                WHERE title LIKE ? OR description LIKE ? OR genre LIKE ?
                ORDER BY added_date DESC
                LIMIT 50
            ''', (f'%{query}%', f'%{query}%', f'%{query}%')) as cursor:
                return await cursor.fetchall()
    
    async def get_movie_by_id(self, movie_id):
        """ID bo'yicha kino olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)) as cursor:
                return await cursor.fetchone()
    
    async def get_movie_by_code(self, code):
        """Kod bo'yicha kino olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM movies WHERE code = ?', (code,)) as cursor:
                return await cursor.fetchone()
    
    async def get_movie_code(self, movie_id):
        """Kino kodini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT code FROM movie_codes WHERE movie_id = ?', (movie_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    
    async def delete_movie(self, movie_id):
        """Kinoni o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
            await db.commit()
    
    async def get_all_movies(self, limit=100, offset=0):
        """Barcha kinolarni olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM movies 
                ORDER BY added_date DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset)) as cursor:
                return await cursor.fetchall()
    
    async def add_user(self, user_id, username='', first_name=''):
        """Foydalanuvchi qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            await db.commit()
    
    async def get_user(self, user_id):
        """Foydalanuvchi ma'lumotlarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone()
    
    async def ban_user(self, user_id):
        """Foydalanuvchini bloklash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            await db.commit()
    
    async def unban_user(self, user_id):
        """Foydalanuvchini blokdan chiqarish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            await db.commit()
    
    async def get_stats(self):
        """Statistika olish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Jami foydalanuvchilar
            async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # Jami kinolar
            async with db.execute('SELECT COUNT(*) FROM movies') as cursor:
                total_movies = (await cursor.fetchone())[0]
            
            # Bugungi foydalanuvchilar
            async with db.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(join_date) = DATE('now')
            ''') as cursor:
                today_users = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'total_movies': total_movies,
                'today_users': today_users
            }
    
    async def log_action(self, user_id, movie_id, action_type):
        """Harakatni yozib olish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO stats (user_id, movie_id, action_type)
                VALUES (?, ?, ?)
            ''', (user_id, movie_id, action_type))
            await db.commit()
    
    async def add_admin(self, user_id, added_by):
        """Admin qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO admins (user_id, added_by)
                VALUES (?, ?)
            ''', (user_id, added_by))
            await db.commit()
    
    async def remove_admin(self, user_id):
        """Adminni o'chirish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
            await db.commit()
    
    async def is_admin(self, user_id):
        """Admin ekanligini tekshirish"""
        from config import ADMIN_IDS
        # Asosiy adminlar
        if user_id in ADMIN_IDS:
            return True
        # Database'dagi adminlar
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result is not None
    
    async def get_all_admins(self):
        """Barcha adminlarni olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM admins ORDER BY added_date DESC') as cursor:
                return await cursor.fetchall()
    
    async def add_rating(self, user_id, movie_id, rating):
        """Reyting qo'shish yoki yangilash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO ratings (user_id, movie_id, rating)
                VALUES (?, ?, ?)
            ''', (user_id, movie_id, rating))
            await db.commit()
    
    async def get_movie_rating(self, movie_id):
        """Kino reytingini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
                FROM ratings WHERE movie_id = ?
            ''', (movie_id,)) as cursor:
                result = await cursor.fetchone()
                return result if result else (0, 0)
    
    async def get_user_rating(self, user_id, movie_id):
        """Foydalanuvchi reytingini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT rating FROM ratings WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    
    async def get_top_rated_movies(self, limit=10):
        """Eng yuqori reytingli kinolar"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT m.*, AVG(r.rating) as avg_rating, COUNT(r.id) as total_ratings
                FROM movies m
                LEFT JOIN ratings r ON m.id = r.movie_id
                GROUP BY m.id
                HAVING total_ratings > 0
                ORDER BY avg_rating DESC, total_ratings DESC
                LIMIT ?
            ''', (limit,)) as cursor:
                return await cursor.fetchall()
    
    async def get_most_viewed_movies(self, limit=10):
        """Eng ko'p ko'rilgan kinolar"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT m.*, COUNT(s.id) as view_count
                FROM movies m
                LEFT JOIN stats s ON m.id = s.movie_id AND s.action_type = 'code_view'
                GROUP BY m.id
                HAVING view_count > 0
                ORDER BY view_count DESC
                LIMIT ?
            ''', (limit,)) as cursor:
                return await cursor.fetchall()
    
    async def get_random_movies(self, limit=3):
        """Tasodifiy kinolar"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM movies ORDER BY RANDOM() LIMIT ?
            ''', (limit,)) as cursor:
                return await cursor.fetchall()
    
    async def add_referral(self, user_id, referred_by):
        """Referal qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO referrals (user_id, referred_by)
                VALUES (?, ?)
            ''', (user_id, referred_by))
            await db.commit()
    
    async def get_referral_count(self, user_id):
        """Referal sonini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT COUNT(*) FROM referrals WHERE referred_by = ?
            ''', (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    
    async def get_referrals(self, user_id):
        """Referallar ro'yxati"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT u.user_id, u.first_name, u.username, r.joined_date
                FROM referrals r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.referred_by = ?
                ORDER BY r.joined_date DESC
            ''', (user_id,)) as cursor:
                return await cursor.fetchall()
    
    async def create_contest(self, name, prize, required_referrals, end_date):
        """Konkurs yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO contest (name, prize, required_referrals, start_date, end_date)
                VALUES (?, ?, ?, datetime('now'), ?)
            ''', (name, prize, required_referrals, end_date))
            await db.commit()
    
    async def get_active_contest(self):
        """Faol konkursni olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM contest 
                WHERE is_active = 1 AND datetime('now') < datetime(end_date)
                ORDER BY id DESC LIMIT 1
            ''') as cursor:
                return await cursor.fetchone()
    
    async def get_contest_participants(self, required_referrals):
        """Konkurs ishtirokchilarini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT u.user_id, u.first_name, u.username, COUNT(r.id) as referral_count
                FROM users u
                LEFT JOIN referrals r ON u.user_id = r.referred_by
                GROUP BY u.user_id
                HAVING referral_count >= ?
                ORDER BY referral_count DESC
            ''', (required_referrals,)) as cursor:
                return await cursor.fetchall()
    
    async def end_contest(self, contest_id, winner_user_id):
        """Konkursni tugatish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE contest SET is_active = 0, winner_user_id = ?
                WHERE id = ?
            ''', (winner_user_id, contest_id))
            await db.commit()
    
    async def get_all_referrals_admin(self):
        """Barcha referallar (admin uchun)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT u.user_id, u.first_name, u.username, COUNT(r.id) as referral_count
                FROM users u
                LEFT JOIN referrals r ON u.user_id = r.referred_by
                GROUP BY u.user_id
                HAVING referral_count > 0
                ORDER BY referral_count DESC
            ''') as cursor:
                return await cursor.fetchall()
