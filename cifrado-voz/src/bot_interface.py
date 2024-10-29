import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configurar registro
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = '7738525810:AAHr_vKE_rKdN5ogOManoz_w7itBxnXo40U'

# Definir rutas absolutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, 'data', 'audio_samples')
TEST_FILES_DIR = os.path.join(BASE_DIR, 'data', 'test_files')

# Crear directorios
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEST_FILES_DIR, exist_ok=True)

# Contraseña admin
ADMIN_PASSWORD = "ABCabc123"
ADMIN_ALTERNATIVE_PASSWORD = "admin1"

# Estados para el manejador de conversación
ESPERANDO_PASSWORD = 1
MOSTRAR_MENU = 2
ESPERANDO_ARCHIVO = 3
ADMIN_MENU = 4
ADMIN_AGREGAR_USUARIO = 5
ADMIN_ELIMINAR_USUARIO = 6

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("verificado"):
        await update.message.reply_text("Ya estás verificado. Puedes usar /cifrar o /descifrar.")
        return MOSTRAR_MENU
    else:
        await update.message.reply_text("Bienvenido. Por favor, ingresa la contraseña para acceder.")
        return ESPERANDO_PASSWORD

async def verificar_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == ADMIN_PASSWORD:
        context.user_data["verificado"] = True
        await update.message.reply_text("Contraseña correcta. Acceso concedido.")
        return await mostrar_menu(update, context)
    elif update.message.text == ADMIN_ALTERNATIVE_PASSWORD:
        await update.message.reply_text("Contraseña alternativa aceptada. Acceso al menú de administrador.")
        return await mostrar_admin_menu(update, context)
    else:
        await update.message.reply_text("Contraseña incorrecta. Inténtalo nuevamente.")
        return ESPERANDO_PASSWORD

async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("verificado"):
        keyboard = [['/cifrar', '/descifrar']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Seleccione una opción:", reply_markup=reply_markup)
        return MOSTRAR_MENU
    else:
        await update.message.reply_text("Error: Debes estar verificado para acceder al menú. Usa /start para iniciar.")
        return ESPERANDO_PASSWORD

async def mostrar_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['/agregar_usuario', '/eliminar_usuario'],
        ['/salir']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Menú de Administrador:", reply_markup=reply_markup)
    return ADMIN_MENU

async def agregar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, envía el nombre y apellido del usuario con el formato 'nombre_apellido'.")
    return ADMIN_ESPERANDO_NOMBRE

async def procesar_nombre_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre_apellido = update.message.text
    context.user_data["nombre_apellido"] = nombre_apellido
    await update.message.reply_text("Ahora, por favor envía un mensaje de voz con el usuario.")
    return ADMIN_ESPERANDO_AUDIO

async def procesar_nuevo_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.voice
    if audio:
        audio_file = await audio.get_file()
        nombre_apellido = context.user_data["nombre_apellido"]
        audio_path = os.path.join(AUDIO_DIR, f"{nombre_apellido}.wav")
        await audio_file.download_to_drive(audio_path)
        await update.message.reply_text(f"Usuario '{nombre_apellido}' agregado correctamente.")
        return await mostrar_admin_menu(update, context)
    else:
        await update.message.reply_text("Error: No se ha recibido un mensaje de voz válido.")
        return ADMIN_ESPERANDO_AUDIO

async def eliminar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivos = os.listdir(AUDIO_DIR)
    if archivos:
        lista_usuarios = "\n".join(f"{idx + 1}. {os.path.splitext(archivo)[0]}" for idx, archivo in enumerate(archivos))
        await update.message.reply_text(
            f"Usuarios registrados:\n{lista_usuarios}\n\n"
            "Por favor, ingresa el número del usuario que deseas eliminar."
        )
        return ADMIN_ELIMINAR_USUARIO
    else:
        await update.message.reply_text("No hay usuarios registrados.")
        return ADMIN_MENU

async def procesar_eliminacion_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        usuario_seleccionado = int(update.message.text.strip()) - 1  # Eliminar espacios en blanco y ajustar a índice de lista
        archivos = os.listdir(AUDIO_DIR)
        if 0 <= usuario_seleccionado < len(archivos):
            usuario = os.path.splitext(archivos[usuario_seleccionado])[0]
            usuario_path = os.path.join(AUDIO_DIR, archivos[usuario_seleccionado])
            os.remove(usuario_path)
            await update.message.reply_text(f"Usuario '{usuario}' eliminado correctamente.")
            return await mostrar_admin_menu(update, context)
        else:
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ADMIN_ELIMINAR_USUARIO
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return ADMIN_ELIMINAR_USUARIO
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {e}")
        await update.message.reply_text("Ha ocurrido un error al eliminar el usuario. Inténtalo de nuevo más tarde.")
        return ADMIN_MENU

async def salir_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Saliendo del menú de administrador. Regresando al menú principal.", reply_markup=ReplyKeyboardRemove())
    return await mostrar_menu(update, context)

async def cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("verificado"):
        await update.message.reply_text("Por favor, envía el archivo que deseas cifrar. Puede ser cualquier tipo de archivo.")
        return ESPERANDO_ARCHIVO
    else:
        await update.message.reply_text("Error: No tienes acceso. Usa /start para verificarte.")
        return ConversationHandler.END

async def descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("verificado"):
        archivos = os.listdir(TEST_FILES_DIR)
        if archivos:
            lista_archivos = "\n".join(f"{idx + 1}. {archivo}" for idx, archivo in enumerate(archivos))
            await update.message.reply_text(
                f"Archivos cifrados disponibles:\n{lista_archivos}\n\n"
                "Por favor, ingresa el número del archivo que deseas descifrar."
            )
        else:
            await update.message.reply_text("No hay archivos disponibles para descifrar.")
        return ESPERANDO_ARCHIVO
    else:
        await update.message.reply_text("Error: No tienes acceso. Usa /start para verificarte.")
        return ConversationHandler.END

async def cifrar_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivo = update.message.document or update.message.photo[-1]
    if archivo:
        archivo_file = await archivo.get_file()
        archivo_name = archivo.file_name if update.message.document else "imagen.jpg"
        archivo_path = os.path.join(TEST_FILES_DIR, archivo_name)
        await archivo_file.download_to_drive(archivo_path)
        await update.message.reply_text(f"Archivo recibido y guardado en {archivo_path} para cifrar.")
        return await mostrar_menu(update, context)  # Regresar al menú después de guardar
    else:
        await update.message.reply_text("Error: No se ha recibido un archivo válido.")
    return MOSTRAR_MENU

async def descifrar_archivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        archivo_seleccionado = int(update.message.text) - 1
        archivos = os.listdir(TEST_FILES_DIR)
        if 0 <= archivo_seleccionado < len(archivos):
            archivo = archivos[archivo_seleccionado]
            await update.message.reply_text(f"Archivo seleccionado para descifrar: {archivo}. Descifrado en proceso.")
            # Aquí va la lógica de descifrado
            await update.message.reply_text("Descifrado completo. Regresando al menú.")
            return await mostrar_menu(update, context)  # Regresar al menú después del descifrado
        else:
            await update.message.reply_text("Número inválido. Por favor, selecciona un número de la lista.")
            return ESPERANDO_ARCHIVO
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
    return MOSTRAR_MENU

async def mensaje_no_entendido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lo siento, no entendí ese mensaje. Usa /start para comenzar.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Ha ocurrido un error en el sistema.")

def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Crear manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ESPERANDO_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_password)],
            MOSTRAR_MENU: [
                CommandHandler("cifrar", cifrar),
                CommandHandler("descifrar", descifrar)
            ],
            ESPERANDO_ARCHIVO: [
                MessageHandler(filters.Document.ALL | filters.PHOTO, cifrar_archivo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, descifrar_archivo)
            ],
            ADMIN_MENU: [
                CommandHandler("agregar_usuario", agregar_usuario),
                CommandHandler("eliminar_usuario", eliminar_usuario),
                CommandHandler("salir", salir_admin_menu)
            ],
            ADMIN_AGREGAR_USUARIO: [MessageHandler(filters.VOICE, procesar_nuevo_usuario)],
            ADMIN_ELIMINAR_USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_eliminacion_usuario)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Agregar manejador para mensajes no entendidos y errores
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.ALL, mensaje_no_entendido))
    application.add_error_handler(error_handler)

    try:
        application.run_polling()
    finally:
        # Resetear el estado de verificación cuando el bot se apague
        for user_id, data in application.user_data.items():
            data["verificado"] = False
        logger.info("Bot detenido. Estado de verificación restablecido.")

if __name__ == "__main__":
    run_bot()
