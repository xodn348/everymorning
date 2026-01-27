import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from db import get_supabase_client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to everymorning! 🌅\n\n"
        "Get daily STEM paper digests delivered to you.\n\n"
        "Commands:\n"
        "/subscribe - Start receiving daily digests\n"
        "/unsubscribe - Stop receiving digests"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    supabase = get_supabase_client()
    
    # Check if already subscribed
    result = supabase.table("subscribers").select("*").eq("telegram_chat_id", chat_id).execute()
    
    if result.data:
        await update.message.reply_text("You're already subscribed! 📬")
        return
    
    # Subscribe
    supabase.table("subscribers").insert({"telegram_chat_id": chat_id}).execute()
    await update.message.reply_text("Subscribed! 🎉 You'll receive daily STEM paper digests.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    supabase = get_supabase_client()
    
    supabase.table("subscribers").update({"is_active": False}).eq("telegram_chat_id", chat_id).execute()
    await update.message.reply_text("Unsubscribed. You won't receive digests anymore. 👋")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN must be set")
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    
    print("Bot started! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
