import telebot
import yt_dlp
import os
import threading
from flask import Flask

TOKEN = '8962021834:AAHQDtC7s1tQ9TugW7tCwkVIDY8RljR6t7E'
bot = telebot.TeleBot(TOKEN)

# --- ХИТРОСТЬ: ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ЗАСЫПАНИЯ ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот жив и работает 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()
# ------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Отправь ссылку, и я скачаю видео.")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Пытаюсь скачать... ⏳")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s', 
        'max_filesize': 50000000, 
        'noplaylist': True,       
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            bot.edit_message_text("Качаю... 📥", chat_id=message.chat.id, message_id=msg.message_id)
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("Отправляю... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, timeout=120)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.edit_message_text("❌ Ошибка. Скорее всего соцсеть не пускает или видео слишком большое.", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == '__main__':
    keep_alive() # Запускаем веб-сервер
    print("Бот запущен...")
    bot.polling(none_stop=True)
