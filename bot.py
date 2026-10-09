import os
import logging
import threading
import telebot
from telebot.types import Message
from groq import Groq
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 8000))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN required")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY required")

ai = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='HTML')
app = Flask(__name__)


def ask_ai(prompt):
    try:
        response = ai.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that responds in Arabic"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"Error: {e}"


@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    bot.reply_to(message, "Welcome! I am HoDa HakiM Bot\n\nAsk me anything")


@bot.message_handler(commands=['help'])
def cmd_help(message: Message):
    bot.reply_to(message, "Type your question and I will answer")


@bot.message_handler(commands=['id'])
def cmd_id(message: Message):
    bot.reply_to(message, f"Your ID: {message.from_user.id}")


@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    bot.send_chat_action(message.chat.id, 'typing')
    response = ask_ai(message.text)
    bot.reply_to(message, response)


@app.route('/')
def home():
    return {"status": "ok", "bot": "HoDa HakiM Bot"}


@app.route('/health')
def health():
    return {"status": "ok"}


def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)


if __name__ == '__main__':
    logger.info("Bot started")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"Flask on port {PORT}")
    bot.infinity_polling(timeout=60)
