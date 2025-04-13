import os
from dotenv import load_dotenv
import httpx
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters

load_dotenv()
API_URL = os.getenv('API_URL')
ASK_STO = 1

async def start_ceksto(
    update: Update,
    context: CallbackContext
) -> int:
    await update.message.reply_text(
        'Silahkan masukkan STO yang akan dicari:'
    )
    
    return ASK_STO

async def main_ceksto(
    update: Update,
    context: CallbackContext
) -> None:
    wto_data = update.message.text
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}?sto={wto_data}")
        
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['data']['total'] > 0:
            data_wto = data['data']['data']
            
            message = 'Data Berhasil Ditemukan! \n'
            for i, datas in enumerate(data_wto, start=1):
                message += f"{i}: {datas.get('nama_gpon', '-')} - {datas.get('status_feeder', '-')}\n"
            
        else:
            message = "Data Tidak Ditemukan!"
    else:
        message = "Terjadi Kesalahan saat mengambil data"
        
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

def register_handler(rh):
    rh.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    'ceksto', start_ceksto
                )
            ],
            states={
                ASK_STO: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        main_ceksto
                    )
                ]
            },
            fallbacks=[],
        )
    )