from ast import parse
import logging
import os
from dotenv import load_dotenv
import httpx
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters

load_dotenv()
API_URL = os.getenv('API_URL')
ASK_GPON = 1

logging.basicConfig(level=logging.INFO)

async def start_cekgpon(
    update: Update,
    context: CallbackContext
) -> int:    
    await update.message.reply_text(
        "Silahkan masukkan nama GPON yang akan dicari: "
    )
    
    return ASK_GPON

async def main_cekgpon(
    update: Update,
    context: CallbackContext
) -> int:
    gpon_name = update.message.text
    logging.info(f"main_cekgpon triggered with message: {update.message.text}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}?nama_gpon={gpon_name}")
        
    logging.info(f"API Response: {response.status_code}, {response.text}") 
    
    if response.status_code == 200:
        data = response.json()
        
        if data['success'] and data['data']['total'] > 0:
            gpon_data = data['data']['data'][0]
            message = f"""
✅ *Data GPON Ditemukan!*
📌 *Witel:* {gpon_data["witel"]}
🏢 *STO:* {gpon_data["sto"]}
🔢 *Nama GPON:* {gpon_data["nama_gpon"]}
🛠 *Card:* {gpon_data["card"]}
🔌 *Port:* {gpon_data["port"]}

📡 *Lemari FTM Eakses:* {gpon_data["nama_lemari_ftm_eakses"]}
🎛 *Panel Eakses:* {gpon_data["no_panel_eakses"]} (Port {gpon_data["no_port_panel_eakses"]})

🟢 *Status Feeder:* {gpon_data["status_feeder"]}
🔗 *Nama Feeder:* {gpon_data["nama_segmen_feeder_utama"]}

🏢 *ODC:* {gpon_data["nama_odc"]}
            """
        
        else:
            message = "Data tidak ditemukan"
    else:
        message = "Terjadi kesalahan saat mengambil data"
        
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

def register_handler(rh):
    logging.info("Registering ConversationHandler for cekgpon")

    handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'cekgpon', start_cekgpon
            )
        ],
        states={
            ASK_GPON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_cekgpon)
            ]
        },
        fallbacks=[],
    )

    logging.info(f"Registered handlers: {handler}")
    rh.add_handler(handler)
