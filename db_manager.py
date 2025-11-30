import sqlite3
import os
from datetime import datetime

# Создает менеджер базы данных и указывает путь к файлу data/zakupki.db
class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join('data', 'zakupki.db')
        self._init_database()

    #создание папопк и таблиц
    def _init_database(self):
        os.makedirs('data', exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            #Создает папку data если ее нет
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    customer TEXT NOT NULL,
                    price TEXT,
                    amount TEXT,
                    status TEXT,
                    number TEXT,
                    link TEXT,
                    search_query TEXT,
                    created_at TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_count INTEGER,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            print(" ________")
    
    def save_purchase(self, purchase_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO purchases 
                    (title, customer, price, amount, status, number, link, search_query, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    purchase_data.get('title', ''),
                    purchase_data.get('customer', ''),
                    purchase_data.get('price', ''),
                    purchase_data.get('amount', ''),
                    purchase_data.get('status', ''),
                    purchase_data.get('number', ''),
                    purchase_data.get('link', ''),
                    purchase_data.get('search_query', ''),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
        
#Создает таблицу search_history для истории поисков
    def save_search_history(self, query, results_count):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_history (query, results_count, created_at)
                    VALUES (?, ?, ?)
                """, (query, results_count, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")
            return False
        
#получение данных
    def get_search_history(self, limit=10):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT query, results_count, created_at 
                    FROM search_history 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения истории: {e}")
            return []
        
#сохранение закупки
    def get_saved_purchases(self, search_query=None, limit=50):
        try:
            with sqlite3.connect(self.db_path) as conn: #соединение с базой
                cursor = conn.cursor()
                
                if search_query:
                    cursor.execute("""
                        SELECT * FROM purchases 
                        WHERE search_query LIKE ? 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (f'%{search_query}%', limit))
                else:
                    cursor.execute("""
                        SELECT * FROM purchases 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (limit,))
                
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения закупок: {e}")
            return []

#статус закупки
    def get_stats(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM purchases")
                total_purchases = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM search_history")
                total_searches = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT search_query, COUNT(*) 
                    FROM purchases 
                    GROUP BY search_query 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 5
                """)
                popular_searches = cursor.fetchall()
                
                return {
                    'total_purchases': total_purchases,
                    'total_searches': total_searches,
                    'popular_searches': popular_searches
                }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}

db = DatabaseManager()