from os import getenv
from dotenv import load_dotenv
import telebot
import webbrowser
import sqlite3

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
name = None

print("start")

@bot.message_handler(commands=["start"])
def start(message):
    conn = sqlite3.connect("db.sql")
    cur = conn.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS users(id int auto_increment primary key, name varchar(50), pass varchar(50))")
    conn.commit()
    cur.close()
    conn.close()
    
    
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(telebot.types.KeyboardButton("/id"), telebot.types.KeyboardButton("/info"))
    start_photo = open("thinkfast-chuklenuts.gif", "rb")
    bot.send_animation(message.chat.id, start_photo, reply_markup=markup)
    bot.send_message(message.chat.id, "Hello! Lets sign you up! Enter your name: ")
    bot.register_next_step_handler(message, user_name)
    # bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}", reply_markup=markup)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Enter your password: ")
    bot.register_next_step_handler(message, user_pass)
    
def user_pass(message):
    password = message.text.strip()
    
    conn = sqlite3.connect("db.sql")
    cur = conn.cursor()
    
    cur.execute(f"INSERT INTO users(name, pass) VALUES (?, ?)", (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("Users list", callback_data="users"))
    bot.send_message(message.chat.id, "You signed up", reply_markup=markup)

    

    

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
    elif callback.data == "users":
        conn = sqlite3.connect("db.sql")
        cur = conn.cursor()
        
        cur.execute(f"SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        conn.close()        
        
        info = ""
        for user in users:
            info += f"Username: {user[1]} | Password: {user[2]}\n"
        bot.send_message(callback.message.chat.id, info)
        



bot.polling(non_stop=True)