import os
import tempfile
import pandas as pd
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters

load_dotenv()
API_URL = os.getenv('API_URL_UPLINK')
ASK_INPUT = 1

async def start_inputuplink(
    update: Update,
    context: CallbackContext
) -> None:
    await update.message.reply_text(
        'Silahkan kirim file excel yang akan di proses \n NB: Harap kirim file excel yang sudah diformat dengan ketentuan yang ada'
    )
    
    return ASK_INPUT

async def main_inputuplink(
    update: Update,
    context: CallbackContext
) -> None:
    file = update.message.document
    reply_message = []

    if file.mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
        processed_file = await file.get_file()

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_file_path = tmp_file.name
            
        await processed_file.download_to_drive(temp_file_path)
        await update.message.reply_text('Data Sedang Diproses... Tunggu Sebentar')

        try:
                df = pd.read_excel(temp_file_path)
                df.columns = df.columns.str.lower()
                df.columns = df.columns.str.replace(' ', '_')
                df = df.astype(str)
                df = df.replace([pd.NA, 'nan', 'NaN', ''], None)
                list_df = df.to_dict(orient='records')

                transformed_data = []

                fields = {
                    "witel": "witel",
                    "sto": "sto",
                    "gpon_hostname": "gpon_hostname",
                    "gpon_ip": "gpon_ip",
                    "gpon_merk": "gpon_merk",
                    "gpon_tipe": "gpon_tipe",
                    "gpon_merk_tipe": "gpon_merk_tipe",
                    "gpon_intf": "gpon_intf",
                    "gpon_lacp": "gpon_lacp",
                    "neighbor_hostname": "neighbor_hostname",
                    "neighbor_intf": "neighbor_intf",
                    "neighbor_lacp": "neighbor_lacp",
                    "bw": "bw",
                    "sfp": "sfp",
                    "vlan_sip": "vlan_sip",
                    "vlan_internet": "vlan_internet",
                    "keterangan": "keterangan",
                    "otn_cross_metro": "otn_cross_metro",
                }

                for data in list_df:
                    transformed = {}

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

                    if response.status_code == 200:
                        reply_message.append(f'✅ Data Berhasil Disimpan')
                    else:
                        reply_message.append('❌ Terjadi Kesalahan saat menyimpan data')

        except Exception as e:
                reply_message.append(f'❌ Terjadi Kesalahan saat mengambil data: {e}')
            
        tmp_file.close()
        os.remove(temp_file_path)
    else:
        reply_message.append(
            '❌ Format File Tidak Sesuai! Harap kirim file excel yang sudah diformat dengan ketentuan yang ada'
        )

    await update.message.reply_text('\n'.join(reply_message))
    
    return ConversationHandler.END

def register_handler(rh):
    rh.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    'uplinkgpon', start_inputuplink
                )
            ],
            states={
                ASK_INPUT: [
                    MessageHandler(
                        filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") |
                        filters.Document.MimeType("application/vnd.ms-excel"),
                        main_inputuplink
                    )
                ]
            },
            fallbacks=[],
        )
    )