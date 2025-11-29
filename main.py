# Flask - веб-фреймворк для создания сайтов на Python
# render_template - для отображения HTML страниц
# request - для обработки данных из форм
# flash - для показа сообщений пользователю
# parse_zakupki - наш парсер из отдельного файла
# app.secret_key - секретный ключ для безопасности сессий


from flask import Flask, render_template, request, flash 
from zakupki_parser import parse_zakupki

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'



#@app.route('/') - при переходе на главную страницу
#methods=['GET', 'POST'] - страница принимает два типа запросов:
#GET - когда пользователь просто открывает страницу
#POST - когда пользователь отправляет форму поиска
#purchases = [] - создаем пустой список для хранения результатов поиска

@app.route('/', methods=['GET', 'POST'])
def index():
    purchases = []

# Если пользователь отправил форму (нажал "Найти закупки")
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip() # - получаем текст из поля ввода
        if search_query:
            try:
                purchases = parse_zakupki(search_query) #Вызываем наш парсер parse_zakupki
                if not purchases: #Обработка результатов
                    flash("Не удалось найти закупки")
                    print("Показываем сообщение: не удалось найти закупки")
                else:
                    flash(f'Найдено закупок: {len(purchases)}', 'success')
                    print(f"Показываем сообщение: найдено {len(purchases)} закупок")
            except Exception as e: #Обработка ошибок
                flash(f'Ошибка при поиске: {str(e)}', 'error')
                print(f"Ошибка: {e}")
        else:
            flash('Введите поисковый запрос', 'error')
            print("Пустой запрос")
    
    return render_template('index.html', purchases=purchases) #Передаем в шаблон переменную purchases с результатами поиска

if __name__ == '__main__':
    app.run(debug=True) #режим отладки (автоперезагрузка при изменениях)