import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handler.base_command import register_handler as base_handler

load_dotenv()

bot_token = os.getenv(
    'BOT_TOKEN'
)
app = Application.builder().token(bot_token).build()

base_handler(app)

if __name__ == "__main__":
    print('Bot running...')
    app.run_polling()