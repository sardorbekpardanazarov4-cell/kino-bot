import telebot
import json
import os

TOKEN = "8211203712:AAHdM1wShReC3Jq60qX_PR9XesR0xtsxSg0"
ADMIN_ID = 123456789  # O'zingizning Telegram ID
REQUIRED_CHANNELS = [
    "@kkgdlhfoyf",
    "@ikkinchi_kanalcha",
    "@uchinchi_kanalcha",
    "@tortinchi_kanalcha"
]

bot = telebot.TeleBot(TOKEN)

DB_FILE = "movies.json"

# ---------- DATABASE FUNKSIYALARI ----------
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            f.write("{}")
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

movies = load_db()

# ---------- MAJBURIY OBUNA TEKSHIRISH ----------
def check_subscription(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["member", "administrator", "creator"]:
                continue
            else:
                return False
        except:
            return False
    return True

# ---------- ADMIN ADD STATES ----------
admin_states = {}  # {admin_id: {"step":1/2/3, "temp":{}}}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.chat.id
    text = "📌 Kino olish uchun 4 ta kanalga obuna bo‘ling:\n"
    for ch in REQUIRED_CHANNELS:
        text += f"👉 {ch}\n"
    text += "\nObuna tastiqlandi, kino kodini yozing."
    bot.send_message(user_id, text)

# ---------- ADMIN VIDEO QO‘SHISH ----------
ADMIN_ID = 8383448395
@bot.message_handler(commands=['add'])
def start_add(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.reply_to(msg, "❌ Siz admin emassiz!")
        return

    admin_states[msg.from_user.id] = {"step": 1, "temp": {}}
    bot.reply_to(msg, "🎬 Kino qo‘shish boshlandi.\nVideoni yuboring:")

# ---------- ADMIN VIDEO YUBORGANDA FILE_ID OLISH ----------
@bot.message_handler(content_types=['video'])
def handle_video(message):
    uid = message.from_user.id
    if uid not in admin_states or admin_states[uid]["step"] != 1:
        return
    file_id = message.video.file_id
    admin_states[uid]["temp"]["file_id"] = file_id
    admin_states[uid]["step"] = 2
    bot.reply_to(message, "Kino ID sini kiriting (masalan: 101)")

# ---------- ADMIN ID YOZGANDA ----------
@bot.message_handler(func=lambda m: m.from_user.id in admin_states and admin_states[m.from_user.id]["step"] == 2)
def handle_id(message):
    uid = message.from_user.id
    movie_id = message.text.strip()
    admin_states[uid]["temp"]["id"] = movie_id
    admin_states[uid]["step"] = 3
    bot.reply_to(message, "Kino nomini kiriting:")

# ---------- ADMIN NOM YOZGANDA ----------
@bot.message_handler(func=lambda m: m.from_user.id in admin_states and admin_states[m.from_user.id]["step"] == 3)
def handle_title(message):
    uid = message.from_user.id
    title = message.text.strip()
    temp = admin_states[uid]["temp"]
    movie_id = temp["id"]
    file_id = temp["file_id"]

    movies[movie_id] = {"title": title, "file_id": file_id}
    save_db(movies)

    del admin_states[uid]
    bot.reply_to(message, f"✅ Kino saqlandi!\nID: {movie_id}\nNomi: {title}")

# ---------- FOYDALANUVCHI KINO SO‘RAGANDA ----------
@bot.message_handler(func=lambda msg: True)
def send_movie(message):
    user_id = message.chat.id
    movie_id = message.text.strip()

    # Majburiy obuna
    if not check_subscription(user_id):
        chs = "\n".join(REQUIRED_CHANNELS)
        bot.reply_to(message, f"⚠️ Botdan foydalanish uchun quyidagi kanallarga a'zo bo‘ling:\n{chs}")
        return

    # Kino bor-yo‘qligini tekshiramiz
    if movie_id in movies:
        m = movies[movie_id]
        bot.send_message(user_id, f"🎬 {m['title']}")
        bot.send_video(user_id, m["file_id"])
    else:
        bot.reply_to(message, "❗ Bu kod mavjud emas❌.")

print("Bot ishga tushdi...")
bot.infinity_polling()
