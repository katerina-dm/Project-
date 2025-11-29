from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import re

def parse_zakupki(search_query):
    print(f"Поиск: {search_query} ===")
    
    driver = None
    try:
        # Настройки Firefox
        firefox_options = Options()
        firefox_options.add_argument("headless")
        
        driver = webdriver.Firefox(options=firefox_options)
        
        # Формируем URL поиска
        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
        #как из урока по логину и паролю
        
        print(f"Открываем: {url}")
        driver.get(url)
        
        # Ждем загрузки
        time.sleep(8)
        
        # Получаем HTML
        html = driver.page_source
        
        # Парсим 
        return parse_real_results(html)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    finally:
        if driver:
            driver.quit()

def parse_real_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    purchases = []
    
    print("Поиск карточек закупок")
    
    # Основные селекторы для карточек закупок
    cards = soup.find_all('div', class_='search-group searchField')
    
    if not cards:
        print("Не найдено карточек закупок")
        return []
    
    print(f"Найдено карточек: {len(cards)}")
    
    for i, card in enumerate(cards[:20], 1):
        try:
            # Извлекаем  данные с правильными ссылками
            data = extract_real_data_with_links(card)
            if data:
                purchases.append(data)
                print(f"{i}. {data['title'][:70]}")
                print(f"   Ссылка: {data['link']}")
                
        except Exception as e:
            print(f"Ошибка карточки {i}: {e}")
            continue
    
    if purchases:
        print(f"Найдено {len(purchases)} закупок")
        return purchases
    else:
        print("Не удалось")
        return []

def extract_real_data_with_links(card):
    #Извлекает данные с ссылками"""
    try:
        # Название закупки
        title_elem = card.find('div', class_='registry-entry__body-value')
        title = title_elem.text.strip() if title_elem else "Название не указано"
        
        # Заказчик
        customer_elem = card.find('div', class_="registry-entry__body-href")
        customer = customer_elem.text.strip() if customer_elem else "Заказчик не указан"
        
        # Цена
        price_elem = card.find('div', class_='price-block__value')
        price = price_elem.text.strip() if price_elem else "Цена не указана"
        
        # Статус
        status_elem = card.find('div', class_='registry-entry__header-mid__title text-normal')
        status = status_elem.text.strip() if status_elem else "Статус не указан"
        
        # ссылка - ищем ссылку на основную страницу закупки
        link = extract_correct_link(card)
        
        # Тип процедуры
        procedure_type = "223-ФЗ" if "223-ФЗ" in card.text else "44-ФЗ"
        
        return {
            'customer': customer,
            'title': title,
            'price': price,
            'amount': price,
            'link': link,
            'status': status,
            'procedure_type': procedure_type
        }
        
    except Exception as e:
        print(f"Ошибка извлечения данных: {e}")
        return None

def extract_correct_link(card):
    # Извлекает  ссылку на закупку
    # Ищем все ссылки в карточке
    links = card.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        
        # Предпочтительные ссылки на основные страницы закупок
        if '/epz/order/notice/' in href and 'printForm' not in href:
            if not href.startswith('http'):
                return 'https://zakupki.gov.ru' + href
            return href
        
        # Ссылки с номером закупки
        if 'regNumber=' in href:
            reg_match = re.search(r'regNumber=([^&]+)', href)
            if reg_match:
                reg_number = reg_match.group(1)
                return f"https://zakupki.gov.ru/epz/order/notice/ea44/view/common-info.html?regNumber"
    
   
    