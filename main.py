import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def init_db():
    conn = sqlite3.connect("saraha.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    conn = sqlite3.connect("saraha.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()
    conn.close()

    if args:
        target_id = args[0]
        if str(user.id) == target_id:
            await update.message.reply_text("لا يمكنك إرسال مصارحة لنفسك!")
            return
        context.user_data['target_id'] = target_id
        await update.message.reply_text("أرسل رسالتك الآن (تطبيق المصارحة يحافظ على سرية هويتك 🔒):")
    else:
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user.id}"
        msg = f"أهلاً بك {user.first_name} 👋\n\nرابط المصارحة الخاص بك هو:\n`{link}`\n\nشاركه لتتلقى الآراء بحرية!"
        await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get('target_id')
    if target_id:
        try:
            msg_to_send = f"📥 **رسالة مصارحة جديدة:**\n\n{update.message.text}"
            await context.bot.send_message(chat_id=int(target_id), text=msg_to_send, parse_mode="Markdown")
            await update.message.reply_text("تم إرسال رسالتك بنجاح وسرية تامّة! ✅")
            context.user_data['target_id'] = None
        except Exception:
            await update.message.reply_text("تعذر إرسال الرسالة. قد يكون المستخدم قد قام بحظر البوت.")
    else:
        await update.message.reply_text("لإرسال مصارحة، يجب عليك الدخول عبر رابط مصارحة شخصي.")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
  
