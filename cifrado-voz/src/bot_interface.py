import sys
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from encryption_handler import EncryptionHandler
from decryption_handler import DecryptionHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = '7738525810:AAHr_vKE_rKdN5ogOManoz_w7itBxnXo40U'

# Definir rutas absolutas considerando que el bot está en la carpeta "src"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio_samples')
TO_ENCRYPT_DIR = os.path.join(DATA_DIR, 'to_encrypt')
PROCESSED_DIR = os.path.join(TO_ENCRYPT_DIR, 'processed')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

# Crear directorios si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TO_ENCRYPT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Función para limpiar archivos
def limpiar_archivos():
    # Eliminar archivos en TO_ENCRYPT_DIR, excluyendo carpetas
    if os.listdir(TO_ENCRYPT_DIR):
        for archivo in os.listdir(TO_ENCRYPT_DIR):
            archivo_path = os.path.join(TO_ENCRYPT_DIR, archivo)
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado en to_encrypt: {archivo}")
    else:
        print("No se encontraron archivos en la carpeta to_encrypt")

    # Eliminar archivo específico en AUDIO_DIR
    audio_file_path = os.path.join(AUDIO_DIR, 'user_input.wav')
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
        print("Archivo eliminado en audio_samples: user_input.wav")
    else:
        print("Archivo user_input.wav no encontrado en audio_samples")

    # Eliminar archivos en PROCESSED_DIR, excluyendo carpetas
    if os.listdir(PROCESSED_DIR):
        for archivo in os.listdir(PROCESSED_DIR):
            archivo_path = os.path.join(PROCESSED_DIR, archivo)
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado en processed: {archivo}")
    else:
        print("No se encontraron archivos en la carpeta processed")

    # Eliminar archivos en OUTPUT_DIR, excluyendo carpetas
    if os.listdir(OUTPUT_DIR):
        for archivo in os.listdir(OUTPUT_DIR):
            archivo_path = os.path.join(OUTPUT_DIR, archivo)
            if os.path.isfile(archivo_path):
                os.remove(archivo_path)
                print(f"Archivo eliminado en output: {archivo}")
    else:
        print("No se encontraron archivos en la carpeta output")

# Ejecutar limpieza de archivos antes de iniciar el bot
limpiar_archivos()
print("Limpieza de archivos completada. Presiona Enter para iniciar el bot.")
input()
# Estados para el manejador de conversación
MOSTRAR_MENU = 1
ESPERANDO_AUDIO = 2
ESPERANDO_SELECCION_DESCIFRAR = 3
ESPERANDO_ARCHIVO = 5
ESPERANDO_SELECCION_ENCRIPTAR = 6

# Instancia de EncryptionHandler y DecryptionHandler
encryption_handler = EncryptionHandler()
decryption_handler = DecryptionHandler()

# Función para solicitar al usuario que envíe un archivo
async def agregar_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enviar un mensaje solicitando el archivo para encriptar
    await update.message.reply_text("Por favor, envía el archivo que deseas agregar para encriptar.")
    # Retornar el estado en el que el bot espera recibir el archivo
    return ESPERANDO_ARCHIVO



# Función para recibir y guardar el archivo enviado por el usuario
async def recibir_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si el mensaje contiene un archivo (documento)
    if update.message.document:
        # Obtener el archivo del mensaje
        archivo = update.message.document
        # Definir la ruta donde se guardará el archivo en el directorio 'to_encrypt'
        archivo_path = os.path.join(TO_ENCRYPT_DIR, archivo.file_name)
        
        # Obtener el archivo completo de Telegram y descargarlo al directorio especificado
        archivo_file = await archivo.get_file()
        await archivo_file.download_to_drive(archivo_path)
        
        # Confirmar al usuario que el archivo fue recibido y guardado
        await update.message.reply_text(f"Archivo '{archivo.file_name}' recibido y guardado en 'to_encrypt'.")
        # Llamar a la función 'mostrar_menu' para continuar la conversación
        return await mostrar_menu(update, context)
    else:
        # Si no se recibe un archivo válido, se envía un mensaje de error y se espera otro archivo
        await update.message.reply_text("No se ha recibido un archivo válido. Por favor, envía un archivo para continuar.")
        return ESPERANDO_ARCHIVO

# Comando de inicio del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await mostrar_menu(update, context)

async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define el teclado con opciones que el usuario puede seleccionar, organizadas en filas
    keyboard = [
        ['/cifrar', '/descifrar'],               # Primera fila de opciones
        ['/grabar_audio', '/eliminar_audio'],    # Segunda fila de opciones
        ['/mostrar_graficos', '/Agregar_archivo'] # Tercera fila de opciones
    ]
    
    # Crea un teclado de respuesta (ReplyKeyboardMarkup) para mostrar las opciones al usuario
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    # Envía un mensaje al usuario con el menú y el teclado personalizado para que seleccione una opción
    await update.message.reply_text("Seleccione una opción:", reply_markup=reply_markup)
    
    # Cambia el estado a MOSTRAR_MENU para que el bot esté listo para recibir la selección del usuario
    return MOSTRAR_MENU

async def cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtener la lista de archivos disponibles para encriptar mediante el handler de encriptación
    archivos_para_encriptar = encryption_handler.get_available_files()
    
    # Si hay archivos disponibles para encriptar
    if archivos_para_encriptar:
        # Crea una lista numerada de los archivos disponibles
        lista_archivos = "\n".join(f"{idx + 1}. {archivo}" for idx, archivo in enumerate(archivos_para_encriptar))
        
        # Envía un mensaje al usuario con los archivos disponibles y solicita que ingrese un número
        await update.message.reply_text(
            f"Archivos disponibles para encriptar:\n{lista_archivos}\n\n"
            "Por favor, ingresa el número del archivo que deseas encriptar."
        )
        # Cambia el estado a ESPERANDO_SELECCION_ENCRIPTAR, esperando que el usuario elija un archivo
        return ESPERANDO_SELECCION_ENCRIPTAR
    else:
        # Si no hay archivos disponibles, informa al usuario y retorna al menú
        await update.message.reply_text("No hay archivos disponibles para encriptar.")
        return MOSTRAR_MENU

async def procesar_seleccion_encriptar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Intenta convertir la selección del usuario en un número (índice)
        seleccion = int(update.message.text.strip()) - 1
        # Obtiene la lista de archivos disponibles nuevamente
        archivos_para_encriptar = encryption_handler.get_available_files()
        
        # Verifica si el índice seleccionado es válido (dentro del rango de archivos disponibles)
        if 0 <= seleccion < len(archivos_para_encriptar):
            archivo_seleccionado = archivos_para_encriptar[seleccion]
            # Llama al handler de encriptación para procesar el archivo seleccionado
            resultado = encryption_handler.process_file_encryption(archivo_seleccionado)
            
            # Si la encriptación fue exitosa
            if resultado['success']:
                # Envía un mensaje confirmando la encriptación exitosa y mostrando la información relevante
                await update.message.reply_text(
                    f"Archivo '{archivo_seleccionado}' encriptado exitosamente.\n"
                    f"Similaridad de voz: {resultado.get('similarity', 'N/A')}\n"
                    f"Archivo encriptado: {resultado['encrypted_file']}"
                )
            else:
                # Si hubo un error en el proceso, informa al usuario
                await update.message.reply_text(f"Error: {resultado['message']}")
            
            # Después de procesar la selección, muestra el menú nuevamente
            return MOSTRAR_MENU
        else:
            # Si el número seleccionado no es válido, informa al usuario y le pide que ingrese un número válido
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ESPERANDO_SELECCION_ENCRIPTAR
    except ValueError:
        # Si el usuario no ingresa un número válido, le pide que ingrese un número
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return ESPERANDO_SELECCION_ENCRIPTAR


async def grabar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Solicita al usuario que envíe un mensaje de audio para guardar
    await update.message.reply_text("Por favor, envía el mensaje de audio que deseas guardar.")
    # Cambia el estado del bot a ESPERANDO_AUDIO, esperando que el usuario envíe un mensaje de audio
    return ESPERANDO_AUDIO

async def recibir_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtiene el mensaje de voz enviado por el usuario
    audio = update.message.voice
    
    # Si el mensaje contiene un archivo de audio
    if audio:
        # Define la ruta donde se guardará el archivo de audio recibido
        file_path = os.path.join(AUDIO_DIR, "user_input.wav")
        
        # Obtiene el archivo de Telegram y lo guarda en la ruta especificada
        telegram_audio = await audio.get_file()
        await telegram_audio.download_to_drive(file_path)
        
        # Informa al usuario que el audio ha sido recibido y guardado
        await update.message.reply_text("Audio recibido y guardado como 'user_input.wav'.")
        # Luego muestra el menú principal al usuario
        return await mostrar_menu(update, context)
    else:
        # Si el mensaje no es un audio, informa al usuario y vuelve a solicitar un mensaje de audio
        await update.message.reply_text("No se ha recibido un mensaje de audio. Por favor, envía un mensaje de audio para continuar.")
        return ESPERANDO_AUDIO

async def eliminar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define la ruta del archivo de audio que se desea eliminar
    file_path = os.path.join(AUDIO_DIR, "user_input.wav")
    
    # Si el archivo existe, se elimina
    if os.path.exists(file_path):
        os.remove(file_path)
        # Informa al usuario que el archivo ha sido eliminado
        await update.message.reply_text("El archivo 'user_input.wav' ha sido eliminado.")
    else:
        # Si el archivo no existe, informa al usuario
        await update.message.reply_text("El archivo 'user_input.wav' no existe.")
    
    # Luego muestra el menú principal al usuario
    return await mostrar_menu(update, context)

async def descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtiene la lista de archivos disponibles para descifrar
    archivos_para_descifrar = decryption_handler.get_encrypted_files()
    
    # Si hay archivos disponibles para descifrar
    if archivos_para_descifrar:
        # Crea una lista numerada de los archivos disponibles
        lista_archivos = "\n".join(f"{idx + 1}. {archivo}" for idx, archivo in enumerate(archivos_para_descifrar))
        
        # Envía un mensaje al usuario con los archivos disponibles y solicita que ingrese un número
        await update.message.reply_text(
            f"Archivos disponibles para descifrar:\n{lista_archivos}\n\n"
            "Por favor, ingresa el número del archivo que deseas descifrar."
        )
        # Cambia el estado a ESPERANDO_SELECCION_DESCIFRAR, esperando que el usuario elija un archivo
        return ESPERANDO_SELECCION_DESCIFRAR
    else:
        # Si no hay archivos disponibles, informa al usuario y retorna al menú
        await update.message.reply_text("No hay archivos encriptados disponibles para descifrar.")
        return MOSTRAR_MENU

async def procesar_descifrado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Intenta convertir la entrada del usuario en un número (índice)
        seleccion = int(update.message.text.strip()) - 1
        # Obtiene la lista de archivos disponibles para descifrar
        archivos_para_descifrar = decryption_handler.get_encrypted_files()
        
        # Verifica si el índice seleccionado es válido (dentro del rango de archivos disponibles)
        if 0 <= seleccion < len(archivos_para_descifrar):
            archivo_seleccionado = archivos_para_descifrar[seleccion]
            # Llama al handler de descifrado para procesar el archivo seleccionado
            resultado = decryption_handler.process_file_decryption(archivo_seleccionado)
            
            # Si el descifrado fue exitoso
            if resultado['success']:
                # Envía el archivo descifrado al usuario
                with open(resultado['decrypted_file'], 'rb') as file:
                    await update.message.reply_document(document=file)
                
                # Envía un mensaje confirmando el éxito del descifrado y mostrando la información relevante
                await update.message.reply_text(
                    f"✅ Archivo '{archivo_seleccionado}' descifrado exitosamente.\n"
                    f"Similitud de voz: {resultado.get('similarity', 'N/A')}\n"
                )
                
                # Si hay una visualización asociada, la envía al usuario como una foto
                if 'visualization' in resultado:
                    with open(resultado['visualization'], 'rb') as img:
                        await update.message.reply_photo(photo=img)
            else:
                # Si hubo un error en el proceso de descifrado, informa al usuario
                await update.message.reply_text(f"❌ Error: {resultado['message']}")
            
            # Después de procesar la selección, muestra el menú nuevamente
            return MOSTRAR_MENU
        else:
            # Si el número seleccionado no es válido, informa al usuario y le pide que ingrese un número válido
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ESPERANDO_SELECCION_DESCIFRAR
    except ValueError:
        # Si el usuario no ingresa un número válido, le pide que ingrese un número
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return ESPERANDO_SELECCION_DESCIFRAR


async def mostrar_graficos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Busca todos los archivos .png en la carpeta de salida (OUTPUT_DIR)
    archivos_png = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
    
    # Si hay archivos .png en la carpeta
    if archivos_png:
        # Itera sobre los archivos encontrados
        for archivo in archivos_png:
            # Construye la ruta completa del archivo
            archivo_path = os.path.join(OUTPUT_DIR, archivo)
            
            # Abre el archivo y lo envía como imagen en el mensaje
            with open(archivo_path, 'rb') as img:
                await update.message.reply_photo(photo=img)
        
        # Informa al usuario que todos los gráficos han sido enviados
        await update.message.reply_text("Todos los gráficos disponibles han sido enviados.")
    else:
        # Si no se encuentran archivos .png, informa al usuario
        await update.message.reply_text("No se encontraron archivos de gráficos (.png) en la carpeta.")
    
    # Devuelve al menú principal
    return MOSTRAR_MENU

async def mensaje_no_entendido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si el mensaje no es reconocido por el bot, informa al usuario
    await update.message.reply_text("Lo siento, no entendí ese mensaje. Usa /start para comenzar.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    # Registra el error que ocurrió en el sistema
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Si el error se produjo en un mensaje, envía un mensaje al usuario indicando que hubo un error
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Ha ocurrido un error en el sistema.")

def run_bot():
    # Inicializa la aplicación del bot usando el token de Telegram
    application = Application.builder().token(TOKEN).build()

    # Define el controlador de conversación para gestionar el flujo y estados del bot
    conv_handler = ConversationHandler(
        # El comando /start inicia la conversación y muestra el menú principal
        entry_points=[CommandHandler("start", start)],
        
        # Define los diferentes estados de la conversación y sus comandos asociados
        states={
            # Estado principal: el usuario puede elegir entre varias acciones (cifrar, descifrar, grabar audio, etc.)
            MOSTRAR_MENU: [
                CommandHandler("cifrar", cifrar),
                CommandHandler("descifrar", descifrar),
                CommandHandler("grabar_audio", grabar_audio),
                CommandHandler("eliminar_audio", eliminar_audio),
                CommandHandler("mostrar_graficos", mostrar_graficos),
                CommandHandler("Agregar_archivo", agregar_archivo),
            ],
            # Estado en el que el bot espera un archivo del usuario
            ESPERANDO_ARCHIVO: [MessageHandler(filters.Document.ALL, recibir_archivo)],
            # Estado en el que el bot espera un texto para la selección de cifrado
            ESPERANDO_SELECCION_ENCRIPTAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_seleccion_encriptar)],
            # Estado en el que el bot espera recibir un mensaje de voz
            ESPERANDO_AUDIO: [MessageHandler(filters.VOICE, recibir_audio)],
            # Estado en el que el bot espera una selección de descifrado del usuario
            ESPERANDO_SELECCION_DESCIFRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_descifrado)],
        },
        
        # Comando para reiniciar la conversación
        fallbacks=[CommandHandler("start", start)],
    )

    # Añade el controlador de conversación a la aplicación
    application.add_handler(conv_handler)
    # Manejador general para cualquier mensaje no entendido o comando incorrecto
    application.add_handler(MessageHandler(filters.ALL, mensaje_no_entendido))
    # Manejador de errores para capturar y gestionar errores en el bot
    application.add_error_handler(error_handler)

    # Inicia el bot en modo polling (escucha continua de mensajes)
    application.run_polling()

if __name__ == "__main__":
    run_bot()