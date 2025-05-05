import os
from dotenv import load_dotenv
import httpx
import pandas as pd
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters

load_dotenv()
API_URL = os.getenv('API_URL')
ASK_INPUT = 1

async def start_inputdata(
    update: Update,
    context: CallbackContext
) -> None:
    await update.message.reply_text(
        'Silahkan kirim file excel yang akan di proses \n NB: Harap kirim file excel yang sudah diformat dengan ketentuan yang ada'
    )
    
    return ASK_INPUT

async def main_inputdata(
    update: Update, 
    context: CallbackContext
    ) -> None:
    file = update.message.document
    reply_message = []

    if file.mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
        processed_file = await file.get_file()
        filename = f"downloads/{file.file_name}"
        await processed_file.download_to_drive(filename)
        await update.message.reply_text('Data Sedang Diproses... Tunggu Sebentar')
        
        try:
            df = pd.read_excel(filename)
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ', '_')
            df = df.astype(str)
            df = df.replace([pd.NA, 'nan', 'NaN', ''], None) 
            list_df = df.to_dict(orient='records')

            transformed_data = []

            for data in list_df:
                transformed = {}

                fields = {
                    "witel": "witel",
                    "sto": "sto",
                    "nama_gpon": "nama_gpon",
                    "card": "card",
                    "port": "port",
                    "nama_lemari_ftm_eakses": "nama_lemari_ftm_eakses",
                    "no_panel_eakses": "no_panel_eakses",
                    "no_port_panel_eakses": "no_port_panel",
                    "nama_lemari_ftm_oakses": "nama_lemari_ftm_oakses",
                    "no_panel_oakses": "no_panel_oakses",
                    "no_port_panel_oakses": "no_port_panel.1",
                    "no_core_feeder": "no_core_feeder",
                    "nama_segmen_feeder_utama": "nama_segmen_feeder_utama",
                    "status_feeder": "status_feeder",
                    "kapasitas_kabel_feeder_utama": "kapasitas_kabel_feeder_utama",
                    "nama_odc": "nama_odc",
                }

                for field, source in fields.items():
                    value = data.get(source)
                    if value is not None:
                        value = str(value).strip() if isinstance(value, str) else value
                        transformed[field] = value
                    else:
                        transformed[field] = None

                transformed_data.append(transformed)
            
            for data in transformed_data:
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{API_URL}", json=data)

                if response.status_code == 201:
                    reply_message.append(f'✅ Data Berhasil Disimpan')
                else:
                    reply_message.append('❌ Terjadi Kesalahan saat menyimpan data')
                        
        except Exception as e:
            reply_message.append(f'❌ Terjadi Kesalahan saat mengambil data')
    else:
        reply_message.append(
            '❌ Format File Tidak Sesuai! Harap kirim file excel yang sudah diformat dengan ketentuan yang ada'
        )

    await update.message.reply_text('\n'.join(reply_message))
    os.remove(filename)
    
    return ConversationHandler.END

def register_handler(rh):
    rh.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    'inputdata', start_inputdata
                )
            ],
            states={
                ASK_INPUT: [
                    MessageHandler(
                        filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") |
                        filters.Document.MimeType("application/vnd.ms-excel"),
                        main_inputdata
                    )
                ]
            },
            fallbacks=[],
        )
    )