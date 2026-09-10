import telebot
import yt_dlp
import os
import threading
from flask import Flask

TOKEN = '8688120815:AAEgoIz2y3t_cbcKaukXOPBoA9HY4Lo90Cc'
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для удержания бота в сети 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот жив и работает 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_web).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне ссылку на видео, и я скачаю его.")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Скачиваю видео... Подожди немного ⏳")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
        'max_filesize': 50000000, # Лимит Telegram 50 МБ
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("Отправляю в Telegram... 🚀", chat_id=message.chat.id, message_id=msg.message_id)
        
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, timeout=120)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.edit_message_text("❌ Не удалось скачать видео. Возможно, ссылка защищена или файл слишком большой.", chat_id=message.chat.id, message_id=msg.message_id)
        print(f"Error: {e}")

if __name__ == '__main__':
    keep_alive()
    print("Бот запущен...")
    bot.polling(none_stop=True)
