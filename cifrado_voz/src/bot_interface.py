import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configurar el registro de mensajes
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Cambiado a DEBUG para obtener más información
)
logger = logging.getLogger(__name__)

# Define el token de tu bot
TOKEN = '7738525810:AAHr_vKE_rKdN5ogOManoz_w7itBxnXo40U'

# Definir rutas absolutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, 'data', 'audio_samples')
TEST_FILES_DIR = os.path.join(BASE_DIR, 'data', 'test_files')

# Crear las carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEST_FILES_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('¡Hola! Envía un mensaje de voz y luego un archivo que deseas procesar.')

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()
    voice_path = os.path.join(AUDIO_DIR, f"voice_{update.message.message_id}.wav")
    
    logger.debug(f"Intentando guardar archivo de voz en: {voice_path}")
    
    try:
        await voice_file.download_to_drive(voice_path)
        
        if os.path.exists(voice_path):
            logger.debug(f"Archivo de voz guardado exitosamente en {voice_path}")
            await update.message.reply_text(f"Audio guardado como {voice_path}. Envía ahora el archivo que deseas procesar.")
        else:
            logger.error(f"El archivo de voz no se encontró después de intentar guardarlo en {voice_path}")
            await update.message.reply_text("Error al guardar el archivo de audio.")
    
    except Exception as e:
        logger.error(f"Error al guardar el archivo de voz: {str(e)}")
        await update.message.reply_text("Ocurrió un error al procesar el archivo de audio.")
    
    context.user_data['voice_path'] = voice_path

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'voice_path' in context.user_data:
        doc_file = await update.message.document.get_file()
        doc_path = os.path.join(TEST_FILES_DIR, update.message.document.file_name)
        
        logger.debug(f"Intentando guardar archivo en: {doc_path}")
        
        try:
            await doc_file.download_to_drive(doc_path)
            
            if os.path.exists(doc_path):
                logger.debug(f"Archivo guardado exitosamente en {doc_path}")
                await update.message.reply_text(f"Archivo guardado como {doc_path}. Puedes comenzar de nuevo enviando otro mensaje de voz.")
            else:
                logger.error(f"El archivo no se encontró después de intentar guardarlo en {doc_path}")
                await update.message.reply_text("Error al guardar el archivo.")
        
        except Exception as e:
            logger.error(f"Error al guardar el archivo: {str(e)}")
            await update.message.reply_text("Ocurrió un error al procesar el archivo.")
        
        context.user_data.clear()
    else:
        await update.message.reply_text("Primero envía un mensaje de voz antes de enviar un archivo.")

def run_bot():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.run_polling()

if __name__ == '__main__':
    run_bot()