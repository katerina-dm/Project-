from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import re

def parse_zakupki(search_query):
    print(f"Поиск: {search_query}")
    
    #запуск браузера
    driver = None
    try:
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        
        driver = webdriver.Firefox(options=firefox_options)
        
        #загрузка страницы
        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={encoded_query}"
        
        print(f"Открываем: {url}")
        driver.get(url)
        time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        purchases = []
        
        #поиск карточек
        cards = soup.find_all('div', class_='row no-gutters registry-entry__form mr-0')
        
        print(f"Найдено карточек: {len(cards)}")
        
        for i, card in enumerate(cards, 1):
            try: # извлечение
                title_elem = card.find('div', class_='registry-entry__body-value')
                title = title_elem.text.strip() if title_elem else "Объект закупки не указан"

                if title == "Объект закупки не указан":
                    title_elem = card.find('a', class_='registry-entry__body-value')
                    title = title_elem.text.strip() if title_elem else "Объект закупки не указан"

                customer_elem = card.find('div', class_='registry-entry__body-href')
                customer = customer_elem.text.strip() if customer_elem else "Заказчик не указан"

                price_elem = card.find('div', class_='price-block__value')
                price = price_elem.text.strip() if price_elem else "Цена не указана"
                # поиск ссылки
                link = extract_correct_link(card)

                print(f"Закупка {i}: {title[:80]}...")

                purchases.append({
                    'title': title, # Что закупают
                    'customer': customer,   # Кто 
                    'price': price,  # Цена
                    'amount': price,  # Дублирует в базу 
                    'link': link,  # Ссылка на закупку
                    'status': 'Активна', # Тип процедуры
                    'procedure_type': '44-ФЗ',
                    'number': str(i)  # Добавляем номер как строку
                })
                
            except Exception as e:
                print(f"Ошибка в карточке {i}: {e}")
                continue
        
        print(f"Успешно: {len(purchases)} закупок")
        return purchases
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    finally:
        if driver:
            driver.quit()

#Ищет все ссылки в карточке и проверяет их по приоритету:
#Ссылки на просмотр закупки (/epz/order/notice/view/common-info.html)
#Ссылки с номером закупки (regNumber=...)
#Любые другие ссылки на закупки (кроме печатных форм)

def extract_correct_link(card):
    links = card.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        
        if '/epz/order/notice/view/common-info.html' in href:
            if not href.startswith('http'):
                return 'https://zakupki.gov.ru' + href
            return href
            
        if 'regNumber=' in href:
            match = re.search(r'regNumber=([^&]+)', href)
            if match:
                reg_number = match.group(1)
                return f"https://zakupki.gov.ru/epz/order/notice/view/common-info.html?regNumber={reg_number}"
        
        if '/epz/order/notice/' in href and 'printForm' not in href:
            if not href.startswith('http'):
                return 'https://zakupki.gov.ru' + href
            return href
    
    return "https://zakupki.gov.ru"