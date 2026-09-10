import telebot
import yt_dlp
import os
import threading
from flask import Flask

TOKEN = '8688120815:AAEgoIz2y3t_cbcKaukXOPBoA9HY4Lo90Cc'
bot = telebot.TeleBot(TOKEN)

# Веб-сервер, чтобы Render не засыпал
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_web).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Бот на связи! Скинь ссылку на видео.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Качаю видео, подожди... ⏳")

    # Самый надежный конфиг yt-dlp для обхода блокировок дата-центров
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'video.mp4',
        'max_filesize': 50000000, # до 50 МБ для Телеграма
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }

    try:
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists('video.mp4'):
            bot.edit_message_text("Отправляю... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, timeout=120)
            os.remove('video.mp4')
        else:
            bot.edit_message_text("❌ Не удалось найти скачанный файл.", chat_id=message.chat.id, message_id=msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка скачивания: видео слишком тяжелое или защита заблокировала запрос.", chat_id=message.chat.id, message_id=msg.message_id)
        print(f"Error: {e}")

if __name__ == '__main__':
    keep_alive()
    print("Бот запущен...")
    bot.polling(none_stop=True)
