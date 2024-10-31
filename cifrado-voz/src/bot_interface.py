import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from encryption_handler import EncryptionHandler  # Importar EncryptionHandler

# Configurar registro
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = '7738525810:AAHr_vKE_rKdN5ogOManoz_w7itBxnXo40U' 

# Definir rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join('cifrado-voz/data', 'audio_samples')  
TEST_FILES_DIR = os.path.join('cifrado-voz/data', 'test_files')
OUTPUT_DIR = os.path.join('cifrado-voz/data', 'output')
TO_ENCRYPT_DIR = os.path.join('cifrado-voz/data', 'to_encrypt')

# Crear directorios
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEST_FILES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TO_ENCRYPT_DIR, exist_ok=True)

# Estados para el manejador de conversación
MOSTRAR_MENU = 1
ESPERANDO_AUDIO = 2
ESPERANDO_SELECCION_DESCIFRAR = 3
SELECCION_DESCIFRAR_PARCIAL = 4
ESPERANDO_ARCHIVO = 5
ESPERANDO_SELECCION_ENCRIPTAR = 6  # Nuevo estado para seleccionar archivo para encriptar

# Instancia de EncryptionHandler
encryption_handler = EncryptionHandler()

async def agregar_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, envía el archivo que deseas agregar para encriptar.")
    return ESPERANDO_ARCHIVO

async def recibir_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        # Obtener el archivo enviado
        archivo = update.message.document
        archivo_path = os.path.join(TO_ENCRYPT_DIR, archivo.file_name)
        
        # Descargar el archivo a la carpeta `to_encrypt`
        archivo_file = await archivo.get_file()
        await archivo_file.download_to_drive(archivo_path)
        
        await update.message.reply_text(f"Archivo '{archivo.file_name}' recibido y guardado en 'to_encrypt'.")
        return await mostrar_menu(update, context)
    else:
        # Si no se recibe un archivo válido, pedir al usuario que intente de nuevo
        await update.message.reply_text("No se ha recibido un archivo válido. Por favor, envía un archivo para continuar.")
        return ESPERANDO_ARCHIVO

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await mostrar_menu(update, context)

async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['/cifrar', '/descifrar'],
        ['/grabar_audio', '/eliminar_audio'],
        ['/mostrar_graficos', '/Agregar_archivo']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Seleccione una opción:", reply_markup=reply_markup)
    return MOSTRAR_MENU

async def cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivos_para_encriptar = encryption_handler.get_available_files()
    
    if archivos_para_encriptar:
        lista_archivos = "\n".join(f"{idx + 1}. {archivo}" for idx, archivo in enumerate(archivos_para_encriptar))
        await update.message.reply_text(
            f"Archivos disponibles para encriptar:\n{lista_archivos}\n\n"
            "Por favor, ingresa el número del archivo que deseas encriptar."
        )
        return ESPERANDO_SELECCION_ENCRIPTAR
    else:
        await update.message.reply_text("No hay archivos disponibles para encriptar.")
        return MOSTRAR_MENU

async def procesar_seleccion_encriptar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        seleccion = int(update.message.text.strip()) - 1
        archivos_para_encriptar = encryption_handler.get_available_files()
        
        if 0 <= seleccion < len(archivos_para_encriptar):
            archivo_seleccionado = archivos_para_encriptar[seleccion]
            resultado = encryption_handler.process_file_encryption(archivo_seleccionado)
            
            if resultado['success']:
                await update.message.reply_text(
                    f"Archivo '{archivo_seleccionado}' encriptado exitosamente.\n"
                    f"Similaridad de voz: {resultado.get('similarity', 'N/A')}\n"
                    f"Archivo encriptado: {resultado['encrypted_file']}"
                )
            else:
                await update.message.reply_text(f"Error: {resultado['message']}")
            
            return MOSTRAR_MENU
        else:
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ESPERANDO_SELECCION_ENCRIPTAR
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return ESPERANDO_SELECCION_ENCRIPTAR

async def grabar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, envía el mensaje de audio que deseas guardar.")
    return ESPERANDO_AUDIO

async def recibir_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.voice
    
    if audio:
        file_path = os.path.join(AUDIO_DIR, "user_input.wav")
        
        telegram_audio = await audio.get_file()
        await telegram_audio.download_to_drive(file_path)
        
        await update.message.reply_text("Audio recibido y guardado como 'user_input.wav'.")
        return await mostrar_menu(update, context)
    else:
        await update.message.reply_text("No se ha recibido un mensaje de audio. Por favor, envía un mensaje de audio para continuar.")
        return ESPERANDO_AUDIO

async def eliminar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = os.path.join(AUDIO_DIR, "user_input.wav")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        await update.message.reply_text("El archivo 'user_input.wav' ha sido eliminado.")
    else:
        await update.message.reply_text("El archivo 'user_input.wav' no existe.")
    
    return await mostrar_menu(update, context)

async def descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivos = os.listdir(TEST_FILES_DIR)
    if archivos:
        lista_archivos = "\n".join(f"{idx + 1}. {archivo}" for idx, archivo in enumerate(archivos))
        await update.message.reply_text(
            f"Archivos disponibles para descargar:\n{lista_archivos}\n\n"
            "Por favor, ingresa el número del archivo que deseas recuperar."
        )
        return ESPERANDO_SELECCION_DESCIFRAR
    else:
        await update.message.reply_text("No hay archivos disponibles para descargar.")
        return MOSTRAR_MENU

async def procesar_seleccion_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        seleccion = int(update.message.text.strip()) - 1
        archivos = os.listdir(TEST_FILES_DIR)
        
        if 0 <= seleccion < len(archivos):
            archivo_seleccionado = archivos[seleccion]
            archivo_path = os.path.join(TEST_FILES_DIR, archivo_seleccionado)
            
            await update.message.reply_document(document=open(archivo_path, 'rb'))
            await update.message.reply_text(f"Archivo '{archivo_seleccionado}' recuperado y enviado.")
            return MOSTRAR_MENU
        else:
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ESPERANDO_SELECCION_DESCIFRAR
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return ESPERANDO_SELECCION_DESCIFRAR

async def mostrar_graficos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivos_png = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
    
    if archivos_png:
        for archivo in archivos_png:
            archivo_path = os.path.join(OUTPUT_DIR, archivo)
            with open(archivo_path, 'rb') as img:
                await update.message.reply_photo(photo=img)
        
        await update.message.reply_text("Todos los gráficos disponibles han sido enviados.")
    else:
        await update.message.reply_text("No se encontraron archivos de gráficos (.png) en la carpeta.")
    
    return MOSTRAR_MENU

async def mensaje_no_entendido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lo siento, no entendí ese mensaje. Usa /start para comenzar.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Ha ocurrido un error en el sistema.")

def run_bot():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MOSTRAR_MENU: [
            CommandHandler("Agregar_archivo", agregar_archivo),  # Nuevo comando para agregar archivo
            CommandHandler("cifrar", cifrar),
            CommandHandler("descifrar", descifrar),
            CommandHandler("grabar_audio", grabar_audio),
            CommandHandler("eliminar_audio", eliminar_audio),
            CommandHandler("mostrar_graficos", mostrar_graficos)
        ],
        ESPERANDO_AUDIO: [MessageHandler(filters.VOICE, recibir_audio)],
        ESPERANDO_ARCHIVO: [MessageHandler(filters.Document.ALL, recibir_archivo)],  # Manejo de archivos
        ESPERANDO_SELECCION_DESCIFRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_seleccion_descifrar)],
        SELECCION_DESCIFRAR_PARCIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_seleccion_descifrar)],
        
        # Agrega este estado
        ESPERANDO_SELECCION_ENCRIPTAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_seleccion_encriptar)]
    },
    fallbacks=[CommandHandler("start", start)],
)

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.ALL, mensaje_no_entendido))
    application.add_error_handler(error_handler)

    application.run_polling()
if __name__ == "__main__":
    run_bot()