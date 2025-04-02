from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

from handler import cekgpon_command

async def start(
    update: Update,
    context: CallbackContext
) -> None:
    keyboard = [
        [InlineKeyboardButton("Bantuan", callback_data='help')]
    ]
    await update.message.reply_text(
        "Halo, saya adalah bot yang dapat melakukan beberapa perintah. Cek di /help untuk melihat command yang tersedia",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help(
    update: Update,
    context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Cek GPON", callback_data='cekgpon')]
    ]
    
    await query.edit_message_text(
        """
Command yang tersedia:
        
/start - Menampilkan pesan selamat datang
/help - Menampilkan daftar command yang tersedia

/cekgpon - Mengecek data GPON
        """
    , reply_markup=InlineKeyboardMarkup(keyboard))
    
# async def button(
#     update: Update,
#     context: CallbackContext
# ) -> None:
#     query = update.callback_query
#     await query.answer()

#     if query.data == 'help':
#         await help(update, context)
#     elif query.data == 'cekgpon':
#         await cekgpon_command.start_cekgpon(update, context)
        
def register_handler(rh):
    rh.add_handler(CommandHandler('start', start))
    # rh.add_handler(CallbackQueryHandler(button))