import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handler.base_command import register_handler as base_handler
from handler.cekgpon_command import register_handler as cekgpon_handler
from handler.ceksto_command import register_handler as cekwto_handler
from handler.inputdata_command import register_handler as inputdata_handler
from handler.inputuplink_command import register_handler as inputuplink_handler

load_dotenv()

bot_token = os.getenv(
    'BOT_TOKEN'
)
app = Application.builder().token(bot_token).build()

base_handler(app)   
cekgpon_handler(app)
cekwto_handler(app)
inputdata_handler(app)
inputuplink_handler(app)

if __name__ == "__main__":
    print('Bot running...')
    app.run_polling()