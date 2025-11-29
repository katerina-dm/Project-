# Flask - веб-фреймворк для создания сайтов на Python
# render_template - для отображения HTML страниц
# request - для обработки данных из форм
# flash - для показа сообщений пользователю
# parse_zakupki - наш парсер из отдельного файла



from flask import Flask, render_template, request, flash, redirect, url_for
from zakupki_parser import parse_zakupki

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Главная страница GET-запрос
@app.route('/', methods=['GET'])
def index_get():
    """
    Функция обрабатывает GET-запросы главной страницы.
    Просто отображает пустую страницу с формой поиска.
    """
    return render_template('index.html', purchases=[])

# Обработчик формы POST-запрос
@app.route('/', methods=['POST'])
def index_post():
    """
    Функция обрабатывает POST-запросы главной страницы,
    инициированные отправкой формы поиска.
    """
    search_query = request.form.get('search_query', '').strip()
    if search_query:
        try:
            purchases = parse_zakupki(search_query)
            if not purchases:
                flash("Не удалось найти закупки", category='warning')
            else:
                flash(f'Найдено закупок: {len(purchases)}', category='success')
        except Exception as e:
            flash(f'Ошибка при поиске: {str(e)}', category='danger')
    else:
        flash('Введите поисковый запрос', category='info')
    
    return render_template('index.html', purchases=purchases)

if __name__ == '__main__':
    app.run(debug=True)