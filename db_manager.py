# sqlite3 - для работы с SQLite базой данных
# os - для работы с файловой системой
# datetime - для работы с датами и временем

import sqlite3
import os
from datetime import datetime

#Создаем класс для управления базой данных
class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join('data', 'zakupki.db') #путь к файлу базы данных: data/zakupki.db
        self._init_database() # cразу при создании инициализируем базу
    
    def _init_database(self): 
        os.makedirs('data', exist_ok=True) # Создаем папку data если ее нет?  не вызывает ошибку если папка уже существует
        
#создаем таблицу
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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
            conn.commit()
            print("База данных создана")
    
    # Сохранение закупки в базу
    # INSERT OR IGNORE - вставляем запись, но игнорируем если такая уже есть
    # purchase_data.get('status', '') - берем статус или пустую строку если нет
# datetime.now().isoformat() - текущая дата-время в формате строки

    def save_purchase(self, purchase_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO purchases 
                    (title, customer, price, amount, status, number, link, search_query, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    purchase_data['title'],
                    purchase_data['customer'],
                    purchase_data['price'],
                    purchase_data['amount'],
                    purchase_data.get('status', ''),
                    purchase_data.get('number', ''),
                    purchase_data['link'],
                    purchase_data['search_query'],
                    datetime.now().isoformat()
                ))
                conn.commit()  #сохраняем изменения в базе
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False