from os import getenv
from dotenv import load_dotenv
import telebot
import webbrowser

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

print("start")

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}")

@bot.message_handler(commands=["id"])
def user_id(message):
    bot.send_message(message.chat.id, f"Your ID: {message.from_user.id}")

@bot.message_handler(commands=["site", "website"])
def site(message):
    webbrowser.open("https://google.com")

@bot.message_handler(commands=["info"])
def info(message):
    print(message)

bot.polling(non_stop=True)