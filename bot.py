from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
import re

TOKEN = "8748296863:AAGFRkU-ScWX70mGXpPiptgjG7mXKFVizs8"

# حذف لینک
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat_id = update.message.chat_id
    text = update.message.text or ""

    # چک کردن لینک
    link_pattern = r'(https?://[^\s]+|t\.me/[^\s]+|@\w+)'
    if re.search(link_pattern, text):
        await update.message.delete()
        await context.bot.send_message(chat_id, f"❌ لینک ممنوع!\nکاربر: {update.message.from_user.first_name}")

# خوشامدگویی
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 خوش آمدی {member.first_name} عزیز!\nبه گروه خوش اومدی ❤️")

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 سلام! من بات مدیریت گروه هستم.\nاضافم کن به گروهت و ادمینم کن!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_links))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 بات روشن شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
