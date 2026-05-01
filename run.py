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

# --- 1. سيرفر Flask عشان ريندير ميفصلش ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Live 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. بياناتك (زي ما هي في صورك) ---
API_ID = 36043373
API_HASH = "f0c672529a5ad1fa5fb051c395b7c67e"
BOT_TOKEN = "8642516650:AAE6uFW0ccsZoHs3_z4BaqgXDG5zm5v3Zs0"
OWNER_ID = 8615839366 
OWNER_USER = "@reg_q"

bot = Client("shd_pro_v100", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 3. قاعدة البيانات ---
DB_FILE = "final_shd_db.json"
def load_db():
    if not os.path.exists(DB_FILE):
        return {"codes": {}, "users": {}, "admins": [OWNER_ID], "emails": [], "settings": {"contact": True}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"codes": {}, "users": {}, "admins": [OWNER_ID], "emails": [], "settings": {"contact": True}}

def get_status(uid):
    db = load_db()
    if uid == OWNER_ID: return "owner"
    if uid in db["admins"]: return "admin"
    return "guest"

# --- 4. لوحة التحكم ---
def main_kb(uid):
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 بدء الشد"), KeyboardButton("🛑 إيقاف الشد")],
        [KeyboardButton("🔄 تحديث")]
    ], resize_keyboard=True)

# --- 5. التعامل مع الرسائل ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    uid = message.from_user.id
    status = get_status(uid)
    await message.reply(
        f"🔥 أهلاً يا <b>{status}</b>\nالبوت شغال الآن بنجاح على Render!",
        reply_markup=main_kb(uid),
        parse_mode=enums.ParseMode.HTML
    )

# --- 6. التشغيل النهائي المضمون لـ Render ---
if __name__ == "__main__":
    print("--- Starting Keep Alive Server ---")
    keep_alive()
    
    print("--- Starting Bot ---")
    # الطريقة دي بتحل مشكلة الـ Loop اللي ظهرت في الصورة رقم 10
    bot.run()
