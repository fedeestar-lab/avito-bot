import requests
from bs4 import BeautifulSoup
import time
import os
import json

# 🔥 ВАШИ ДАННЫЕ
BOT_TOKEN = "8839285917:AAFFmsMOk2d8h4i0noPtcHyT3zUPr8ho5bs"
CHAT_ID = "108873834"

SENT_FILE = "sent_links.json"

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
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_avito():
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
            if href and href in sent_links:
                continue
            title_elem = link.find('h3') or link.find('div', {'itemprop': 'name'})
            if title_elem and ('san san' in title_elem.text.lower() or 'sansan' in title_elem.text.lower()):
                full_href = f"https://www.avito.ru{href}" if href.startswith('/') else href
                print(f"✅ НОВОЕ: {title_elem.text.strip()}")
                sent_links.add(full_href)
                save_sent_links()
                new_count += 1
                send_message(f"🔔 НОВОЕ ОБЪЯВЛЕНИЕ!\n{title_elem.text.strip()}\n{full_href}")
        if new_count == 0:
            print("⏳ Новых объявлений нет")
        else:
            print(f"📤 Отправлено новых: {new_count}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

print("🚀 Бот запущен!")
check_avito()
