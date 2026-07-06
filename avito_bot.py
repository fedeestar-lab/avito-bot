from flask import Flask
import requests
from bs4 import BeautifulSoup
import time
import os
import json
import threading

# ========== ВАШИ ДАННЫЕ ==========
BOT_TOKEN = "8839285917:AAFFmsMOk2d8h4i0noPtcHyT3zUPr8ho5bs"
CHAT_ID = "108873834"
# =================================

app = Flask(__name__)
SENT_FILE = "sent_links.json"

# Загружаем уже отправленные ссылки
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_links = set(json.load(f))
else:
    sent_links = set()

def save_sent_links():
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_links), f)

def send_message(text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.get(url, params=params, timeout=30)
        print(f"✅ Отправлено: {text[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def check_avito():
    """Проверяет Авито и отправляет новые объявления"""
    global sent_links
    url = 'https://www.avito.ru/rossiya?q=san+san+gear'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'data-marker': 'item'})
        print(f"🔍 Найдено объявлений: {len(links)}")
        
        new_count = 0
        for link in links:
            href = link.get('href')
            if not href:
                continue
                
            full_href = f"https://www.avito.ru{href}" if href.startswith('/') else href
            
            if full_href in sent_links:
                continue
                
            title_elem = link.find('h3') or link.find('div', {'itemprop': 'name'})
            if title_elem and ('san san' in title_elem.text.lower() or 'sansan' in title_elem.text.lower()):
                title_text = title_elem.text.strip()
                print(f"✅ НОВОЕ: {title_text}")
                sent_links.add(full_href)
                save_sent_links()
                new_count += 1
                send_message(f"🔔 НОВОЕ ОБЪЯВЛЕНИЕ!\n\n{title_text}\n\n🔗 {full_href}")
        
        if new_count == 0:
            print("⏳ Новых объявлений нет")
        else:
            print(f"📤 Отправлено новых: {new_count}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def run_bot():
    """Основной цикл бота — проверка каждые 3 часа"""
    while True:
        try:
            check_avito()
            print(f"💤 Следующая проверка через 3 часа...")
            time.sleep(10800)  # 3 часа
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(300)  # 5 минут

@app.route('/')
def home():
    return "✅ Бот для San San gear работает!"

@app.route('/ping')
def ping():
    """Эндпоинт для cron-job.org, чтобы бот не засыпал"""
    return "pong", 200

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("🚀 Бот запущен!")
    # Запускаем веб-сервер
    app.run(host='0.0.0.0', port=10000)
