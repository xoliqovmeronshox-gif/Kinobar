"""
SQLite dan PostgreSQL ga ma'lumotlarni ko'chirish
"""
import asyncio
import sqlite3
import asyncpg
import os

async def migrate_data():
    # PostgreSQL connection
    postgres_url = input("PostgreSQL DATABASE_URL ni kiriting: ")
    
    # SQLite connection
    sqlite_conn = sqlite3.connect('bot_database.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    # PostgreSQL connection
    pg_conn = await asyncpg.connect(postgres_url)
    
    try:
        print("🔄 Ma'lumotlarni ko'chirish boshlandi...")
        
        # Movies jadvalini ko'chirish
        movies = sqlite_conn.execute('SELECT * FROM movies').fetchall()
        for movie in movies:
            await pg_conn.execute('''
                INSERT INTO movies (title, file_id, file_type, description, year, genre, code, added_by, added_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT DO NOTHING
            ''', movie['title'], movie['file_id'], movie['file_type'], 
                movie['description'], movie['year'], movie['genre'], 
                movie['code'], movie['added_by'], movie['added_date'])
        
        print(f"✅ {len(movies)} ta kino ko'chirildi")
        
        # Users jadvalini ko'chirish
        users = sqlite_conn.execute('SELECT * FROM users').fetchall()
        for user in users:
            await pg_conn.execute('''
                INSERT INTO users (user_id, username, first_name, join_date, is_banned)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id) DO NOTHING
            ''', user['user_id'], user['username'], user['first_name'], 
                user['join_date'], user['is_banned'])
        
        print(f"✅ {len(users)} ta foydalanuvchi ko'chirildi")
        
        # Ratings jadvalini ko'chirish
        try:
            ratings = sqlite_conn.execute('SELECT * FROM ratings').fetchall()
            for rating in ratings:
                await pg_conn.execute('''
                    INSERT INTO ratings (user_id, movie_id, rating, rated_date)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, movie_id) DO NOTHING
                ''', rating['user_id'], rating['movie_id'], 
                    rating['rating'], rating['rated_date'])
            
            print(f"✅ {len(ratings)} ta reyting ko'chirildi")
        except:
            print("⚠️ Ratings jadvali topilmadi")
        
        # Stats jadvalini ko'chirish
        try:
            stats = sqlite_conn.execute('SELECT * FROM stats').fetchall()
            for stat in stats:
                await pg_conn.execute('''
                    INSERT INTO stats (user_id, movie_id, action_type, action_date)
                    VALUES ($1, $2, $3, $4)
                ''', stat['user_id'], stat['movie_id'], 
                    stat['action_type'], stat['action_date'])
            
            print(f"✅ {len(stats)} ta statistika ko'chirildi")
        except:
            print("⚠️ Stats jadvali topilmadi")
        
        # Admins jadvalini ko'chirish
        try:
            admins = sqlite_conn.execute('SELECT * FROM admins').fetchall()
            for admin in admins:
                await pg_conn.execute('''
                    INSERT INTO admins (user_id, added_by, added_date)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO NOTHING
                ''', admin['user_id'], admin['added_by'], admin['added_date'])
            
            print(f"✅ {len(admins)} ta admin ko'chirildi")
        except:
            print("⚠️ Admins jadvali topilmadi")
        
        print("🎉 Barcha ma'lumotlar muvaffaqiyatli ko'chirildi!")
        
    finally:
        sqlite_conn.close()
        await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())