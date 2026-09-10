import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = '8688120815:AAEgoIz2y3t_cbcKaukXOPBoA9HY4Lo90Cc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- ХИТРОСТЬ: ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ЗАСЫПАНИЯ ---
@app.route('/')
def home():
    return "Бот жив и работает 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_web).start()
# ------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Отправь ссылку (YouTube, TikTok, Instagram), и я скачаю видео через секретный API.")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Магия вне Хогвартса... Ищу видео ⏳")

    # Настройки для обращения к стороннему API
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {"url": url}

    try:
        # Стучимся в публичный сервис, который скачивает всё сам без куки
        response = requests.post("https://api.cobalt.tools/api/json", json=data, headers=headers)
        
        if response.status_code == 200:
            res_json = response.json()
            video_url = res_json.get("url")
            
            if video_url:
                bot.edit_message_text("Отправляю видео... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
                # Телеграм сам скачает видео по этой ссылке!
                bot.send_video(message.chat.id, video_url)
            else:
                bot.edit_message_text("❌ API не смог вытащить прямую ссылку на видео.", chat_id=message.chat.id, message_id=msg.message_id)
        else:
            bot.edit_message_text("❌ Сервис временно перегружен или недоступен. Попробуй позже.", chat_id=message.chat.id, message_id=msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Произошла ошибка соединения с сервером.", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == '__main__':
    keep_alive() # Запускаем веб-сервер
    print("Бот запущен...")
    bot.polling(none_stop=True)
