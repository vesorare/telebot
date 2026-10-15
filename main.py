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
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(telebot.types.KeyboardButton("/id"), telebot.types.KeyboardButton("/info"))
    start_photo = open("thinkfast-chuklenuts.gif", "rb")
    bot.send_animation(message.chat.id, start_photo, reply_markup=markup)
    # bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}", reply_markup=markup)

@bot.message_handler(commands=["id"])
def user_id(message):
    bot.reply_to(message, f"Your ID: {message.from_user.id}")

@bot.message_handler(commands=["site", "website"])
def site(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(">--0--<", url="https://google.com"))
    bot.reply_to(message, "Go to site", reply_markup=markup)

@bot.message_handler(commands=["info"])
def info(message):
    print(message)
    
@bot.message_handler(content_types=["photo"])
def reply_to_photo(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("Delete image", callback_data="delete"), telebot.types.InlineKeyboardButton("Edit message", callback_data="edit"))
    bot.reply_to(message, "Such a beautiful image", reply_markup=markup)

@bot.callback_query_handler()
def callback_message(callback):
    if callback.data == "delete":
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == "edit":
        bot.edit_message_text("Edited text", callback.message.chat.id, callback.message.message_id) 


bot.polling(non_stop=True)