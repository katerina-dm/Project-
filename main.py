# Flask - веб-фреймворк для создания сайтов на Python
# parse_zakupki - наш парсер из отдельного файла


from flask import Flask, render_template, request, flash, redirect, url_for
from zakupki_parser import parse_zakupki
from db_manager import db  # Импортируем нашу базу данных

app = Flask(__name__)
app.secret_key = 'your-secret-key-here' #секретный ключ для безопасности

@app.route('/', methods=['GET'])
def index_get():
    """Главная страница"""
    history = db.get_search_history(5)  # последние 5 поисков
    stats = db.get_stats()    # статистика
    return render_template('index.html', purchases=[], history=history, stats=stats)

@app.route('/', methods=['POST'])
def index_post():
    """Обработка поиска и сохранение"""
    search_query = request.form.get('search_query', '').strip()
    purchases = []
    
    if search_query:
        try:
            # Ищем закупки
            purchases = parse_zakupki(search_query)
            
            if purchases:
                # Сохраняем каждую закупку
                saved_count = 0
                for purchase in purchases:
                    # Добавляем поисковый запрос к данным
                    purchase['search_query'] = search_query
                    if db.save_purchase(purchase):
                        saved_count += 1
                
                # Сохраняем историю поиска
                db.save_search_history(search_query, saved_count)
                
                flash(f'Найдено: {len(purchases)} закупок | Сохранено: {saved_count}', 'success')
            else:
                flash('Не найдено закупок по вашему запросу', 'warning')
                
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'danger')
    else:
        flash(' Введите поисковый запрос', 'info')
    
    history = db.get_search_history(5)
    stats = db.get_stats()
    return render_template('index.html', purchases=purchases, history=history, stats=stats)

@app.route('/saved')
def saved_purchases():
    """Просмотр сохраненных закупок"""
    search_filter = request.args.get('search', '')
    purchases = db.get_saved_purchases(search_filter)
    stats = db.get_stats()
    return render_template('saved.html', purchases=purchases, stats=stats, search_filter=search_filter)
   

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)