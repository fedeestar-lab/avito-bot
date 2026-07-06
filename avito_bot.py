from flask import Flask
import requests
import time
import os
import json
import threading
from datetime import datetime

app = Flask(__name__)

# ========== ВАШИ ДАННЫЕ ==========
BOT_TOKEN = "ВАШ_НОВЫЙ_ТОКЕН"
CHAT_ID = "108873834"
SCREENSHOT_API_KEY = "ВАШ_API_КЛЮЧ"  # Получить на screenshotapi.net (бесплатно 100 скриншотов)
# =================================

# Файл для хранения времени последнего скриншота
LAST_SCREEN_FILE = "last_screen.json"

def load_last_screen_time():
    if os.path.exists(LAST_SCREEN_FILE):
        with open(LAST_SCREEN_FILE, "r") as f:
            return json.load(f).get("last_time", 0)
    return 0

def save_last_screen_time(timestamp):
    with open(LAST_SCREEN_FILE, "w") as f:
        json.dump({"last_time": timestamp}, f)

def send_photo(image_url, caption):
    """Отправляет фото в Telegram по ссылке"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': CHAT_ID,
        'photo': image_url,
        'caption': caption
    }
    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            print("✅ Фото отправлено в Telegram!")
        else:
            print(f"❌ Ошибка отправки: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def take_screenshot():
    """Делает скриншот через API"""
    api_url = "https://screenshotapi.net/api/v1/screenshot"
    params = {
        'token': SCREENSHOT_API_KEY,
        'url': 'https://www.avito.ru/rossiya?q=San+San+Gear',
        'output': 'image',
        'width': 1920,
        'height': 1080,
        'wait_for': 5000,
        'fresh': True  # Принудительно обновить страницу
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=60)
        data = response.json()
        
        if data.get('status') == 'success':
            image_url = data['screenshot']
            current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
            caption = f"🔍 Поиск 'San San Gear' на Авито\n🕐 {current_time}\n\nПроверка завершена!"
            send_photo(image_url, caption)
            save_last_screen_time(time.time())
            return True
        else:
            print(f"❌ Ошибка API: {data}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при скриншоте: {e}")
        return False

def check_avito():
    """Тестовая проверка — просто пробуем открыть страницу и отправляем результат"""
    print("🔍 Выполняю тестовую проверку...")
    return take_screenshot()

def send_test_message():
    """Отправляет тестовое сообщение, что бот жив"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': "✅ Бот запущен и работает!\nЯ буду присылать скриншот раз в день."
    }
    try:
        requests.post(url, data=data, timeout=30)
        print("✅ Тестовое сообщение отправлено")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def run_bot():
    """Основной цикл бота"""
    while True:
        try:
            now = time.time()
            last_screen = load_last_screen_time()
            
            # Проверяем, прошло ли уже 24 часа с последнего скриншота
            if now - last_screen >= 86400:  # 24 часа
                print("🕐 Отправляю ежедневный скриншот...")
                take_screenshot()
            else:
                hours_left = int((86400 - (now - last_screen)) / 3600)
                print(f"💤 Следующий скриншот через ~{hours_left} часов")
            
            time.sleep(3600)  # Проверяем каждый час
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(300)

@app.route('/')
def home():
    return "✅ Бот для San San gear работает!"

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/test')
def test():
    """Принудительная проверка — сразу делает скриншот"""
    print("🔄 Принудительная проверка через /test")
    take_screenshot()
    return "✅ Проверка выполнена! Скриншот отправлен.", 200

@app.route('/now')
def now():
    """Сразу проверяет и возвращает результат"""
    result = take_screenshot()
    if result:
        return "✅ Скриншот отправлен в Telegram!", 200
    else:
        return "❌ Ошибка при создании скриншота", 500

if __name__ == '__main__':
    print("🚀 Бот запущен!")
    
    # Отправляем тестовое сообщение
    send_test_message()
    
    # Запускаем основной цикл
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
