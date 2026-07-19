from flask import Flask
from threading import Thread
import os
import telebot 

app = Flask(__name__)

@app.route("/")
def home():
    return "NEXO Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

Thread(target=run).start()
import telebot
import json
import os
import random
import time

TOKEN = "8687051101:AAE_4z-7S_2sfSQ18wFQwJw05GHu0fIErrM"

ADMIN_ID = 8884750457

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

FILE = "nexo_players.json"


# =====================
# БАЗА ИГРОКОВ
# =====================

if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        players = json.load(f)
else:
    players = {}


def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4, ensure_ascii=False)


def create_player(user):

    uid = str(user.id)

    if uid not in players:

        players[uid] = {
            "name": user.first_name,

            "coins": 0,
            "aura": 0,
            "noxe": 0,

            "title": "Новичок",

            "premium": False,
            "premium_time": 0,

            "games": 0,

            "house": "Нет",
            "car": "Нет",
            "plane": "Нет",

            "bonus_aura": 0,

            "game": None
        }

        save()


# =====================
# АДМИН БОГ
# =====================

def is_admin(user_id):
    return user_id == ADMIN_ID


def admin_setup(user):

    uid = str(user.id)

    if is_admin(user.id):

        players[uid]["coins"] = 100000
        players[uid]["noxe"] = 100000
        players[uid]["title"] = "🔱 БОГ"

        save()



# =====================
# START
# =====================

@bot.message_handler(commands=["start"])
def start(message):

    create_player(message.from_user)

    admin_setup(message.from_user)


    bot.reply_to(message,
"""⭐ NEXO Games

Добро пожаловать!

Команды:

👤 /profile
💰 /balance
🎮 /game
🌌 /aura
🏆 /top

Скоро:
🛒 магазин
👑 ELITE
🔷 Noxe""")


# =====================
# ПРОФИЛЬ
# =====================

@bot.message_handler(commands=["profile"])
def profile(message):

    create_player(message.from_user)

    p = players[str(message.from_user.id)]


    bot.reply_to(message,
f"""👤 NEXO PROFILE

{p['title']} | {p['name']}

💰 Монеты:
{p['coins']}

🌌 Aura:
{p['aura']}

🔷 Noxe:
{p['noxe']}

🎮 Игр:
{p['games']}

👑 Premium:
{"Да" if p['premium'] else "Нет"}

🏠 Дом:
{p['house']}

🚗 Машина:
{p['car']}

✈️ Самолёт:
{p['plane']}
""")


# =====================
# БАЛАНС
# =====================

@bot.message_handler(commands=["balance"])
def balance(message):

    create_player(message.from_user)

    p = players[str(message.from_user.id)]

    bot.reply_to(message,
f"""💰 Баланс:

💰 {p['coins']}
🌌 {p['aura']} Aura
🔷 {p['noxe']} Noxe
""")


print("NEXO часть 1 запущена")# =====================
# ИГРА
# =====================

@bot.message_handler(commands=["game"])
def game(message):

    create_player(message.from_user)

    uid = str(message.from_user.id)

    players[uid]["game"] = random.randint(1,5)
    players[uid]["games"] += 1

    save()

    bot.reply_to(message,
"""🎮 Я загадал число от 1 до 5

Угадай число 👇""")


@bot.message_handler(func=lambda m: m.text.isdigit())
def guess(message):

    uid = str(message.from_user.id)

    if uid not in players:
        return

    if players[uid]["game"] is None:
        return


    if int(message.text) == players[uid]["game"]:

        reward = random.randint(1,100)

        if random.randint(1,100) == 1:
            reward = 10000


        # ELITE x2
        if players[uid]["premium"]:
            reward *= 2


        players[uid]["coins"] += reward
        players[uid]["game"] = None

        save()

        bot.reply_to(message,
        f"🎉 Победа!\n+{reward} 💰")


    else:
        bot.reply_to(message,"❌ Не угадал")


# =====================
# AURA
# =====================

@bot.message_handler(commands=["aura"])
def aura(message):

    create_player(message.from_user)

    uid = str(message.from_user.id)

    now = int(time.time())

    if now - players[uid]["bonus_aura"] < 86400:

        bot.reply_to(message,
        "⏳ Aura можно получить раз в 24 часа")

        return


    amount = random.randint(50,100)

    players[uid]["aura"] += amount
    players[uid]["bonus_aura"] = now

    save()

    bot.reply_to(message,
    f"🌌 Получено +{amount} Aura")


# =====================
# NOXE
# =====================

@bot.message_handler(commands=["noxe"])
def noxe(message):

    create_player(message.from_user)

    uid = str(message.from_user.id)

    if players[uid]["coins"] < 1000:

        bot.reply_to(message,
        "❌ Нужно 1000 монет")

        return


    players[uid]["coins"] -= 1000
    players[uid]["noxe"] += 1

    save()

    bot.reply_to(message,
    "🔷 Ты получил 1 Noxe")


# =====================
# ELITE
# =====================

@bot.message_handler(commands=["elite"])
def elite(message):

    create_player(message.from_user)

    uid = str(message.from_user.id)

    if players[uid]["noxe"] < 5:

        bot.reply_to(message,
        "❌ Нужно 5 Noxe")

        return


    players[uid]["noxe"] -= 5

    players[uid]["premium"] = True
    players[uid]["premium_time"] = int(time.time()) + 2592000
    players[uid]["title"] = "👑 ELITE"


    save()

    bot.reply_to(message,
    "👑 Ты получил ELITE на 30 дней!")


# =====================
# ПЕРЕВОД МОНЕТ
# =====================

@bot.message_handler(commands=["pay"])
def pay(message):

    bot.reply_to(message,
    "Используй:\n/pay @username сумма")


# =====================
# TOP
# =====================

@bot.message_handler(commands=["top"])
def top(message):

    users = sorted(
        players.values(),
        key=lambda x:x["coins"],
        reverse=True
    )


    text="🏆 NEXO TOP\n\n"

    for i,p in enumerate(users[:10],1):

        text += f"{i}. {p['name']} — {p['coins']} 💰\n"


    bot.reply_to(message,text)


# =====================
# МАГАЗИН
# =====================

@bot.message_handler(commands=["shop"])
def shop(message):

    bot.reply_to(message,
"""🛒 NEXO SHOP

🏠 Дом
10000 💰

🚗 Машина
50000 💰

✈️ Самолёт
500000 💰

👑 ELITE
5 🔷 Noxe
""")


# =====================
# ПРОСМОТР ПРОФИЛЯ
# =====================

@bot.message_handler(commands=["user"])
def user_profile(message):

    if not (is_admin(message.from_user.id) or 
            players[str(message.from_user.id)]["premium"]):

        bot.reply_to(message,
        "❌ Только ELITE и БОГ")

        return


    bot.reply_to(message,
    "Функция поиска по username будет добавлена")


print("NEXO полностью запущен!")
bot.infinity_polling(skip_pending=True)

