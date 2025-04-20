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
        "Halo, saya adalah bot yang dapat melakukan beberapa perintah. Tekan 'Bantuan' untuk melihat command yang tersedia",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help(
    update: Update,
    context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        """
Command yang tersedia:
        
/start - Menampilkan pesan selamat datang
/help - Menampilkan daftar command yang tersedia

/cekgpon - Mengecek data GPON
/ceksto - Mengecek data Status Feeder STO
/inputdata - Menginput data GPON via Excel
        """
    )
    
async def button(
    update: Update,
    context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await help(update, context)
        
def register_handler(rh):
    rh.add_handler(CommandHandler('start', start))
    rh.add_handler(CallbackQueryHandler(button))