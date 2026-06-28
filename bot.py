import telebot
from telebot import types
import time
import re
import random

TOKEN = "توکن_باتت_رو_اینجا_بزار"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            return
        name = member.first_name or "کاربر"
        bot.send_message(message.chat.id, f"🎉 خوش اومدی {name} جان!\n📜 قوانین گروه رو بخون و لذت ببر 😎")

@bot.message_handler(content_types=['new_chat_members'])
def silent_mode(message):
    bot.restrict_chat_member(
        message.chat.id,
        message.new_chat_members[0].id,
        until_date=int(time.time()) + 180,
        can_send_messages=False
    )

@bot.message_handler(func=lambda m: m.forward_from is not None or m.forward_from_chat is not None)
def anti_forward(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "❌ فوروارد پیام ممنوع!")

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'))
def filter_message(message):
    text = message.text
    chat_id = message.chat.id
    if re.search(r'(https?://|t\.me/|www\.)', text, re.IGNORECASE):
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, f"🚫 @{message.from_user.username or message.from_user.first_name} لینک ممنوع!")
        return
    spam_words = ['تلگرام یاب', 'فروش ممبر', 'ساخت گروه', 'تبلیغات', 'کانال', 'join']
    for word in spam_words:
        if word in text.lower():
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"🚫 @{message.from_user.username or message.from_user.first_name} تبلیغ ممنوع!")
            return

user_msg_count = {}
user_last_time = {}

@bot.message_handler(func=lambda m: True)
def anti_spam(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()
    if user_id in user_last_time and now - user_last_time[user_id] < 2:
        user_msg_count[user_id] = user_msg_count.get(user_id, 0) + 1
        if user_msg_count[user_id] > 3:
            bot.restrict_chat_member(chat_id, user_id, until_date=int(now) + 60, can_send_messages=False)
            bot.send_message(chat_id, f"⛔ @{message.from_user.username or message.from_user.first_name} اسپم کردی، ۱ دقیقه سکوت!")
            user_msg_count[user_id] = 0
    else:
        user_msg_count[user_id] = 0
    user_last_time[user_id] = now

waiting_captcha = {}

@bot.message_handler(content_types=['new_chat_members'])
def captcha_new_user(message):
    user_id = message.new_chat_members[0].id
    if user_id == bot.get_me().id:
        return
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
    msg = bot.send_message(message.chat.id, f"🧮 {num1} + {num2} = ? (برای اثبات انسان بودن)")
    waiting_captcha[user_id] = {"answer": num1 + num2, "msg_id": msg.message_id}

@bot.message_handler(func=lambda m: m.from_user.id in waiting_captcha)
def check_captcha(message):
    user_id = message.from_user.id
    try:
        if int(message.text) == waiting_captcha[user_id]["answer"]:
            bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.send_message(message.chat.id, "✅ کپچا درست بود، خوش اومدی!")
        else:
            bot.kick_chat_member(message.chat.id, user_id)
            bot.send_message(message.chat.id, "❌ جواب غلط، بن شدی!")
    except:
        pass
    finally:
        del waiting_captcha[user_id]

print("بات روشن شد ✅")
bot.infinity_polling()
# ========== دستورات متنی ادمین ==========
ADMIN_IDS = [123456789]  # آیدی خودتو بزار

@bot.message_handler(func=lambda m: m.text and m.reply_to_message and m.from_user.id in ADMIN_IDS)
def admin_text_commands(message):
    text = message.text.strip().lower()

    # بن کردن — با "بن" یا "سیک" یا "اخراج"
    if text in ['بن', 'سیک بن', 'بکن بن', 'اخراج', 'kick', 'ban']:
        user_id = message.reply_to_message.from_user.id
        bot.kick_chat_member(message.chat.id, user_id)
        bot.send_message(message.chat.id, f"⛔ @{message.reply_to_message.from_user.username or 'کاربر'} بن شد!")

    # سکوت — با "سکوت" یا "mute" یا "میکروفون"
    elif text in ['سکوت', 'mute', 'میکروفون', 'ساکت']:
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
        bot.send_message(message.chat.id, f"🔇 @{message.reply_to_message.from_user.username or 'کاربر'} سکوت شد!")

    # رفع سکوت — با "آن سکوت" یا "unmute" یا "حرف بزنه"
    elif text in ['آن سکوت', 'unmute', 'حرف بزنه', 'بازکردن', 'صدا']:
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        bot.send_message(message.chat.id, f"🔊 @{message.reply_to_message.from_user.username or 'کاربر'} سکوت برداشته شد!")
