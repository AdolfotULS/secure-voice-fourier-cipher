import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging for more detailed information
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Define your bot's token
TOKEN = '7738525810:AAHr_vKE_rKdN5ogOManoz_w7itBxnXo40U'

# Define absolute paths for data storage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, 'data', 'audio_samples')
TEST_FILES_DIR = os.path.join(BASE_DIR, 'data', 'test_files')

# Create directories if they don't exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEST_FILES_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send a voice message and then a file you want to process.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()
    voice_path = os.path.join(AUDIO_DIR, f"voice_{update.message.message_id}.wav")

    logger.debug(f"Trying to save voice file to: {voice_path}")

    try:
        await voice_file.download_to_drive(voice_path)

        if os.path.exists(voice_path):
            logger.debug(f"Voice file saved successfully to {voice_path}")
            await update.message.reply_text(f"Audio saved as {voice_path}. Now send the file you want to process.")
        else:
            logger.error(f"Voice file not found after trying to save it to {voice_path}")
            await update.message.reply_text("Error saving audio file.")
    except Exception as e:
        logger.error(f"Error saving voice file: {str(e)}")
        await update.message.reply_text("An error occurred while processing the audio file.")

    context.user_data['voice_path'] = voice_path

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'voice_path' in context.user_data:
        doc_file = await update.message.document.get_file()
        doc_path = os.path.join(TEST_FILES_DIR, update.message.document.file_name)

        logger.debug(f"Trying to save file to: {doc_path}")

        try:
            await doc_file.download_to_drive(doc_path)

            if os.path.exists(doc_path):
                logger.debug(f"File saved successfully to {doc_path}")
                await update.message.reply_text(f"File saved as {doc_path}. You can start over by sending another voice message.")
            else:
                logger.error(f"File not found after trying to save it to {doc_path}")
                await update.message.reply_text("Error saving file.")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            await update.message.reply_text("An error occurred while processing the file.")

        context.user_data.clear()
    else:
        await update.message.reply_text("First send a voice message before sending a file.")

def run_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.run_polling()

if __name__ == '__main__':
    run_bot()