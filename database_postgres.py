import asyncpg
import os
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.db_url = DATABASE_URL or os.getenv('DATABASE_URL')
    
    async def get_connection(self):
        """Database connection olish"""
        return await asyncpg.connect(self.db_url)
    
    async def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = await self.get_connection()
        try:
            # Kinolar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    description TEXT,
                    year INTEGER,
                    genre TEXT,
                    code TEXT,
                    added_by BIGINT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Foydalanuvchilar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_banned INTEGER DEFAULT 0
                )
            ''')
            
            # Statistika jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    movie_id INTEGER,
                    action_type TEXT,
                    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Adminlar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY,
                    added_by BIGINT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reytinglar jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    movie_id INTEGER,
                    rating INTEGER,
                    rated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, movie_id)
                )
            ''')
            
        finally:
            await conn.close()
    
    async def add_movie(self, title, file_id, file_type, description='', year=None, genre='', code=None, added_by=None):
        """Kino qo'shish"""
        conn = await self.get_connection()
        try:
            movie_id = await conn.fetchval('''
                INSERT INTO movies (title, file_id, file_type, description, year, genre, code, added_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            ''', title, file_id, file_type, description, year, genre, code, added_by)
            return movie_id
        finally:
            await conn.close()
    
    async def get_movie_by_code(self, code):
        """Kod bo'yicha kino olish"""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow('SELECT * FROM movies WHERE code = $1', code)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def search_movies(self, query):
        """Kino qidirish"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('''
                SELECT * FROM movies 
                WHERE title ILIKE $1 OR description ILIKE $1 OR genre ILIKE $1
                ORDER BY added_date DESC
                LIMIT 50
            ''', f'%{query}%')
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def get_movie_by_id(self, movie_id):
        """ID bo'yicha kino olish"""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow('SELECT * FROM movies WHERE id = $1', movie_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def delete_movie(self, movie_id):
        """Kinoni o'chirish"""
        conn = await self.get_connection()
        try:
            await conn.execute('DELETE FROM movies WHERE id = $1', movie_id)
        finally:
            await conn.close()
    
    async def get_all_movies(self, limit=100, offset=0):
        """Barcha kinolarni olish"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('''
                SELECT * FROM movies 
                ORDER BY added_date DESC 
                LIMIT $1 OFFSET $2
            ''', limit, offset)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def add_user(self, user_id, username='', first_name=''):
        """Foydalanuvchi qo'shish"""
        conn = await self.get_connection()
        try:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id, username, first_name)
        finally:
            await conn.close()
    
    async def get_user(self, user_id):
        """Foydalanuvchi ma'lumotlarini olish"""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def ban_user(self, user_id):
        """Foydalanuvchini bloklash"""
        conn = await self.get_connection()
        try:
            await conn.execute('UPDATE users SET is_banned = 1 WHERE user_id = $1', user_id)
        finally:
            await conn.close()
    
    async def unban_user(self, user_id):
        """Foydalanuvchini blokdan chiqarish"""
        conn = await self.get_connection()
        try:
            await conn.execute('UPDATE users SET is_banned = 0 WHERE user_id = $1', user_id)
        finally:
            await conn.close()
    
    async def get_stats(self):
        """Statistika olish"""
        conn = await self.get_connection()
        try:
            total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
            total_movies = await conn.fetchval('SELECT COUNT(*) FROM movies')
            today_users = await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(join_date) = CURRENT_DATE
            ''')
            
            return {
                'total_users': total_users,
                'total_movies': total_movies,
                'today_users': today_users
            }
        finally:
            await conn.close()
    
    async def log_action(self, user_id, movie_id, action_type):
        """Harakatni yozib olish"""
        conn = await self.get_connection()
        try:
            await conn.execute('''
                INSERT INTO stats (user_id, movie_id, action_type)
                VALUES ($1, $2, $3)
            ''', user_id, movie_id, action_type)
        finally:
            await conn.close()
    
    async def add_admin(self, user_id, added_by):
        """Admin qo'shish"""
        conn = await self.get_connection()
        try:
            await conn.execute('''
                INSERT INTO admins (user_id, added_by)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id, added_by)
        finally:
            await conn.close()
    
    async def remove_admin(self, user_id):
        """Adminni o'chirish"""
        conn = await self.get_connection()
        try:
            await conn.execute('DELETE FROM admins WHERE user_id = $1', user_id)
        finally:
            await conn.close()
    
    async def is_admin(self, user_id):
        """Admin ekanligini tekshirish"""
        from config import ADMIN_IDS
        # Asosiy adminlar
        if user_id in ADMIN_IDS:
            return True
        # Database'dagi adminlar
        conn = await self.get_connection()
        try:
            result = await conn.fetchval('SELECT user_id FROM admins WHERE user_id = $1', user_id)
            return result is not None
        finally:
            await conn.close()
    
    async def get_all_admins(self):
        """Barcha adminlarni olish"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('SELECT * FROM admins ORDER BY added_date DESC')
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def add_rating(self, user_id, movie_id, rating):
        """Reyting qo'shish yoki yangilash"""
        conn = await self.get_connection()
        try:
            await conn.execute('''
                INSERT INTO ratings (user_id, movie_id, rating)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, movie_id) 
                DO UPDATE SET rating = $3, rated_date = CURRENT_TIMESTAMP
            ''', user_id, movie_id, rating)
        finally:
            await conn.close()
    
    async def get_movie_rating(self, movie_id):
        """Kino reytingini olish"""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow('''
                SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
                FROM ratings WHERE movie_id = $1
            ''', movie_id)
            if row and row['avg_rating']:
                return float(row['avg_rating']), int(row['total_ratings'])
            return 0.0, 0
        finally:
            await conn.close()
    
    async def get_user_rating(self, user_id, movie_id):
        """Foydalanuvchi reytingini olish"""
        conn = await self.get_connection()
        try:
            rating = await conn.fetchval('''
                SELECT rating FROM ratings WHERE user_id = $1 AND movie_id = $2
            ''', user_id, movie_id)
            return rating
        finally:
            await conn.close()
    
    async def get_top_rated_movies(self, limit=10):
        """Eng yuqori reytingli kinolar"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('''
                SELECT m.*, AVG(r.rating) as avg_rating, COUNT(r.id) as total_ratings
                FROM movies m
                LEFT JOIN ratings r ON m.id = r.movie_id
                GROUP BY m.id
                HAVING COUNT(r.id) > 0
                ORDER BY AVG(r.rating) DESC, COUNT(r.id) DESC
                LIMIT $1
            ''', limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def get_most_viewed_movies(self, limit=10):
        """Eng ko'p ko'rilgan kinolar"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('''
                SELECT m.*, COUNT(s.id) as view_count
                FROM movies m
                LEFT JOIN stats s ON m.id = s.movie_id AND s.action_type = 'code_view'
                GROUP BY m.id
                HAVING COUNT(s.id) > 0
                ORDER BY COUNT(s.id) DESC
                LIMIT $1
            ''', limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def get_random_movies(self, limit=3):
        """Tasodifiy kinolar"""
        conn = await self.get_connection()
        try:
            rows = await conn.fetch('''
                SELECT * FROM movies ORDER BY RANDOM() LIMIT $1
            ''', limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()