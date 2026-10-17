import requests
from dotenv import load_dotenv
from os import getenv


load_dotenv()
TOKEN = getenv("BOT_TOKEN")
WEATHER = getenv("WEATHER_API")
EXCHANGE = getenv("EXCHANGE_API")

exchange_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE}/latest/USD")
exchange_data = exchange_res.json()
print(exchange_data)