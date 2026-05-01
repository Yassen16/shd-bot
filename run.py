import asyncio
import smtplib
import random
import string
import json
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# --- الجزء اللي بيضحك على السيرفر (Flask Server) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Live 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- الثوابت (بياناتك زي ما هي) ---
API_ID = 36043373
API_HASH = "f0c672529a5ad1fa5fb051c395b7c67e"
BOT_TOKEN = "8642516650:AAE6uFW0ccsZoHs3_z4BaqgXDG5zm5v3Zs0"
OWNER_ID = 8615839366 
OWNER_USER = "@reg_q"

bot = Client("shd_pro_v100", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- قاعدة البيانات ---
DB_FILE = "final_shd_db.json"
def load_db():
    if not os.path.exists(DB_FILE):
        return {"codes": {}, "users": {}, "admins": [OWNER_ID], "emails": [], "settings": {"contact": True}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_status(uid):
    db = load_db()
    if uid == OWNER_ID: return "owner"
    if uid in db["admins"]: return "admin"
    if str(uid) in db["users"]:
        if datetime.now() < datetime.fromisoformat(db["users"][str(uid)]["expire_at"]): return "user"
    return "guest"

# --- لوحة التحكم ---
def main_kb(uid):
    s = get_status(uid); db = load_db()
    c_btn = "❌ تعطيل التواصل" if db["settings"]["contact"] else "✅ تفعيل التواصل"
    if s in ["owner", "admin"]:
        return ReplyKeyboardMarkup([
            [KeyboardButton("🚀 بدء الشد"), KeyboardButton("🛑 إيقاف الشد")],
            [KeyboardButton("🎫 إنشاء كود"), KeyboardButton("📧 إضافة جيميل")],
            [KeyboardButton("📊 عرض الأكواد"), KeyboardButton("👥 عرض المستخدمين")],
            [KeyboardButton("❌ تعطيل اشتراك"), KeyboardButton(c_btn)],
            [KeyboardButton("➕ إضافة مشرف"), KeyboardButton("➖ إزالة مشرف")],
            [KeyboardButton("🔄 تحديث"), KeyboardButton("❓ الإرشادات")]
        ], resize_keyboard=True)
    return ReplyKeyboardMarkup([[KeyboardButton("🚀 بدء الشد"), KeyboardButton("🛑 إيقاف الشد")], [KeyboardButton("📧 إضافة جيميل")], [KeyboardButton("💬 تواصل مع المطور")], [KeyboardButton("🔄 تحديث")]], resize_keyboard=True)

user_states = {}
stop_shd = {}

# --- المحرك ---
async def start_engine(client, message, data, sec):
    uid = message.from_user.id; db = load_db()
    await message.reply("🚀 انطلق الشد..")
    while not stop_shd.get(uid, False):
        for target in data["list"]:
            if stop_shd.get(uid, False): break
            if not db["emails"]: break
            sender = random.choice(db["emails"])
            try:
                msg = MIMEText(data["body"]); msg['Subject'] = data["sub"]
                msg['From'] = sender['email']; msg['To'] = target.strip()
                with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as s:
                    s.starttls(); s.login(sender['email'], sender['pass'])
                    s.sendmail(sender['email'], target.strip(), msg.as_string())
                await message.reply(f"✅ تم الإرسال: {target.strip()}")
            except: pass
            await asyncio.sleep(sec)
        if stop_shd.get(uid, False) or not data["list"]: break

@bot.on_message(filters.private)
async def manager(client, message):
    uid = message.from_user.id; text = message.text; status = get_status(uid); db = load_db()
    if not text: return
    
    # تصفير الحالة
    main_btns = ["🚀 بدء الشد", "🛑 إيقاف الشد", "🎫 إنشاء كود", "📧 إضافة جيميل", "📊 عرض الأكواد", "👥 عرض المستخدمين", "❌ تعطيل اشتراك", "🔄 تحديث", "✅ تفعيل التواصل", "❌ تعطيل التواصل", "➕ إضافة مشرف", "➖ إزالة مشرف", "❓ الإرشادات"]
    if text in main_btns or text == "/start":
        user_states.pop(uid, None)
        if text == "🛑 إيقاف الشد": 
            stop_shd[uid] = True
            return await message.reply("🛑 تم الإيقاف.")
        if text in ["/start", "🔄 تحديث"]:
            return await message.reply(f"🔥 أهلاً يا <b>{status}</b>\n👨‍💻 المطور: {OWNER_USER}", reply_markup=main_kb(uid), parse_mode=enums.ParseMode.HTML)

    # تشغيل الشد
    if text == "🚀 بدء الشد":
        if not db["emails"]: return await message.reply("❌ ضيف حسابات أولاً!")
        user_states[uid] = {"step": "L"}
        return await message.reply("📫 أرسل قائمة الإيميلات:")

    elif uid in user_states:
        step = user_states[uid]["step"]
        if step == "L":
            user_states[uid].update({"list": text.split("\n"), "step": "S"})
            await message.reply("✅ الموضوع:")
        elif step == "S":
            user_states[uid].update({"sub": text, "step": "B"})
            await message.reply("✅ الكليشة:")
        elif step == "B":
            user_states[uid].update({"body": text, "step": "T"})
            await message.reply("⏳ الثواني:")
        elif step == "T":
            try:
                sec = int(text); stop_shd[uid] = False; data = user_states[uid].copy()
                user_states.pop(uid); asyncio.create_task(start_engine(client, message, data, sec))
            except: await message.reply("أرقام بس!")

# --- التشغيل النهائي المضمون لـ Render ---
if __name__ == "__main__":
    print("--- Starting Server ---")
    keep_alive() # بيشغل السيرفر الوهمي في الخلفية
    print("--- Bot is Running ---")
    bot.run() # بيشغل البوت
