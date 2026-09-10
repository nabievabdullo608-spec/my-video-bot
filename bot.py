import telebot
import requests
import os
import threading
from flask import Flask

TOKEN = '8688120815:AAEgoIz2y3t_cbcKaukXOPBoA9HY4Lo90Cc'
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для поддержки активности на Render 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_web).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Отправь ссылку на видео (YouTube, TikTok, Instagram), и я отправлю его тебе.")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Обрабатываю ссылку... ⏳")

    # Используем стабильный публичный сервис для получения прямой ссылки
    api_url = "https://co.wuk.sh/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "url": url,
        "vQuality": "720"
    }

    try:
        response = requests.post(api_url, json=data, headers=headers)
        res_json = response.json()

        if res_json.get("status") == "stream" or res_json.get("url"):
            video_url = res_json.get("url")
            bot.edit_message_text("Скачиваю и отправляю... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
            bot.send_video(message.chat.id, video_url)
        elif res_json.get("status") == "redirect":
            video_url = res_json.get("url")
            bot.edit_message_text("Отправляю... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
            bot.send_video(message.chat.id, video_url)
        else:
            bot.edit_message_text("❌ Не удалось получить видео по этой ссылке. Попробуй другую.", chat_id=message.chat.id, message_id=msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Произошла ошибка при обработке запроса.", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == '__main__':
    keep_alive()
    print("Бот запущен...")
    bot.polling(none_stop=True)
