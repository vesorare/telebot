from os import getenv
from dotenv import load_dotenv
import telebot
import sqlite3
import requests
import json
from currency_converter import CurrencyConverter

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
WEATHER = getenv("WEATHER_API")
EXCHANGE = getenv("EXCHANGE_API")

bot = telebot.TeleBot(TOKEN)
name = None
password = None
currency = CurrencyConverter()
amount = 0

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
    global password
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


@bot.message_handler(commands=["weather"])
def weather(message):
    bot.send_message(message.chat.id, "Enter the city:")
    bot.register_next_step_handler(message, send_weather)

        
def send_weather(message):
    city = message.text.strip()
    weather_res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER}&units=metric")
    weather_data = weather_res.json()
    bot.reply_to(message, f"Weather in {city}:\n"
    f"Temp: {weather_data["main"]["temp"]}\n"
    f"Descriptions: {weather_data["weather"][0]["description"]}")
        
        
@bot.message_handler(commands=["convert"])
def convert(message):
    bot.send_message(message.chat.id, "Enter currency amount: ")
    bot.register_next_step_handler(message, get_amount)

def get_amount(message):    
    try:
        global amount
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Enter a number:")
        bot.register_next_step_handler(message, get_amount)
        return
    
    if amount > 0:
        markup = telebot.types.InlineKeyboardMarkup()
        btn_USD_EUR = telebot.types.InlineKeyboardButton("USD/EUR", callback_data="USD/EUR")
        btn_EUR_USD = telebot.types.InlineKeyboardButton("EUR/USD", callback_data="EUR/USD")
        btn_USD_RUB = telebot.types.InlineKeyboardButton("USD/RUB", callback_data="USD/RUB")
        btn_RUB_USD = telebot.types.InlineKeyboardButton("RUB/USD", callback_data="RUB/USD")
        btn_KZT_RUB = telebot.types.InlineKeyboardButton("KZT/RUB", callback_data="KZT/RUB")
        btn_RUB_KZT = telebot.types.InlineKeyboardButton("RUB/KZT", callback_data="RUB/KZT")
        btn_KZT_USD = telebot.types.InlineKeyboardButton("KZT/USD", callback_data="KZT/USD")
        btn_USD_KZT = telebot.types.InlineKeyboardButton("USD/KZT", callback_data="USD/KZT")
        btn_another = telebot.types.InlineKeyboardButton("Another pair", callback_data="another_pair")
        markup.row(btn_USD_EUR, btn_EUR_USD)
        markup.row(btn_USD_RUB, btn_RUB_USD)
        markup.row(btn_KZT_RUB, btn_RUB_KZT)
        markup.row(btn_KZT_USD, btn_USD_KZT)
        markup.row(btn_another)
        
        bot.send_message(message.chat.id , "Choose currency pair:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Number must be bigger than 0. Enter number:")
        bot.register_next_step_handler(message, get_amount)

def convert_another_pair(message):
    try:
        values = message.text.strip().upper().split("/")
        exchange_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE}/latest/{values[0]}")
        exchange_data = exchange_res.json()
        bot.send_message(message.chat.id, f"{amount}{values[0]} to {values[1]}: {round(amount * exchange_data['conversion_rates'][values[1]], 2)}")
    except Exception:
        bot.send_message(message.chat.id, f"Something is wrong. Try again.")
        bot.register_next_step_handler(message, convert_another_pair)

        
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
    elif "/" in callback.data:
        values = callback.data.strip().split("/")
        exchange_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE}/latest/{values[0]}")
        exchange_data = exchange_res.json()
        bot.send_message(callback.message.chat.id, f"{amount}{values[0]} to {values[1]}: {round(amount * exchange_data['conversion_rates'][values[1]], 2)}")
    elif callback.data == "another_pair":
        bot.send_message(callback.message.chat.id, "Enter a pair of currencys like in example. Example: USD/EUR")
        bot.register_next_step_handler(callback.message, convert_another_pair)



bot.polling(non_stop=True)