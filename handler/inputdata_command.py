import os
import tempfile
import pandas as pd
import httpx
from dotenv import load_dotenv
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
        
        # Gunakan tempfile untuk menyimpan file sementara
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            await processed_file.download_to_drive(tmp_file.name)
            await update.message.reply_text('Data Sedang Diproses... Tunggu Sebentar')

            try:
                # Membaca file Excel dari tmp_file
                df = pd.read_excel(tmp_file.name)
                df.columns = df.columns.str.lower()
                df.columns = df.columns.str.replace(' ', '_')
                df = df.astype(str)
                df = df.replace([pd.NA, 'nan', 'NaN', ''], None)
                list_df = df.to_dict(orient='records')

                transformed_data = []

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

                for data in list_df:
                    transformed = {}

                    for field, source in fields.items():
                        value = data.get(source)
                        if value is not None:
                            value = str(value).strip() if isinstance(value, str) else value
                            transformed[field] = value
                        else:
                            transformed[field] = None  # Pastikan kalau kosong atau None kirimkan None

                    transformed_data.append(transformed)

                # Kirim data ke API
                for data in transformed_data:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{API_URL}?sto={data['sto']}&nama_lemari_ftm_oakses={data['nama_lemari_ftm_oakses']}")
                    
                        response_data = response.json()
                        if response_data.get("data", {}).get("from") is 1:
                            remove_data = await client.delete(f"{API_URL}?sto={data['sto']}&nama_lemari_ftm_oakses={data['nama_lemari_ftm_oakses']}")
                            if remove_data.status_code == 200:
                                await client.post(f"{API_URL}", json=data)
                                reply_message.append(f"✅ Data GPON {data['sto']} - {data['nama_lemari_ftm_oakses']} Berhasil Terupdate")
                            else:
                                reply_message.append(f"❌ Terjadi Kesalahan saat mengupdate data: {remove_data.status_code}")
                        elif response_data.get("data", {}).get("from") is None:
                            await client.post(f"{API_URL}", json=data)
                            reply_message.append(f"✅ Data GPON {data['sto']} - {data['nama_lemari_ftm_oakses']} Berhasil Ditambahkan")

            except Exception as e:
                reply_message.append(f'❌ Terjadi Kesalahan saat mengambil data: {e}')

        tmp_file.close()    
        os.remove(tmp_file_path)
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
