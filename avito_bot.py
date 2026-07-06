from flask import Flask
import requests
from bs4 import BeautifulSoup
import time
import os
import json
import threading
import sys  # <-- НОВАЯ БИБЛИОТЕКА

# ========== ВАШИ ДАННЫЕ ==========
BOT_TOKEN = "8839285917:AAFdavZFUYO8Dh_0WoEmiAEaytAb8fxWaQc"
CHAT_ID = "108873834"
# =================================

app = Flask(__name__)
SENT_FILE = "sent_links.json"

# Принудительно включаем немедленный вывод логов
sys.stdout.reconfigure(line_buffering=True)

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_links = set(json.load(f))
else:
    sent_links = set()

def save_sent_links():
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_links), f)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.get(url, params=params, timeout=30)
        print(f"✅ Отправлено: {text[:50]}...")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        sys.stdout.flush()
        return False

def check_avito():
    global sent_links
    print("🔍 НАЧАЛО ПРОВЕРКИ (check_avito вызвана)")
    sys.stdout.flush()
    
    url = 'https://www.avito.ru/rossiya?q=san+san+gear'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        print("📡 Отправляю запрос на Авито...")
        sys.stdout.flush()
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📡 Статус ответа: {response.status_code}")
        sys.stdout.flush()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'data-marker': 'item'})
        print(f"🔍 Найдено объявлений: {len(links)}")
        sys.stdout.flush()
        
        new_count = 0
        for link in links:
            href = link.get('href')
            if not href:
                continue
            full_href = f"https://www.avito.ru{href}" if href.startswith('/') else href
            if full_href in sent_links:
                continue
            title_elem = link.find('h3') or link.find('div', {'itemprop': 'name'})
            if title_elem:
                title_text = title_elem.text.strip()
                if 'san san gear' in title_text.lower():
                    print(f"✅ НОВОЕ: {title_text}")
                    sys.stdout.flush()
                    sent_links.add(full_href)
                    save_sent_links()
                    new_count += 1
                    send_message(f"🔔 НОВОЕ ОБЪЯВЛЕНИЕ!\n\n{title_text}\n\n🔗 {full_href}")
        
        if new_count == 0:
            print("⏳ Новых объявлений с 'San San Gear' не найдено")
        else:
            print(f"📤 Отправлено новых: {new_count}")
        sys.stdout.flush()
            
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        sys.stdout.flush()

def run_bot():
    while True:
        try:
            check_avito()
            print("💤 Следующая проверка через 3 часа...")
            sys.stdout.flush()
            time.sleep(10800)
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            sys.stdout.flush()
            time.sleep(300)

@app.route('/')
def home():
    return "✅ Бот для San San gear работает!"

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/test')
def test():
    check_avito()
    return "✅ Проверка выполнена!", 200

if __name__ == '__main__':
    print("🚀 Бот запущен!")
    sys.stdout.flush()
    
    # ПРОВЕРКА СРАЗУ ПРИ СТАРТЕ
    print("🔄 Вызываю check_avito() при старте...")
    sys.stdout.flush()
    check_avito()
    
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    app.run(host='0.0.0.0', port=10000, debug=False)
