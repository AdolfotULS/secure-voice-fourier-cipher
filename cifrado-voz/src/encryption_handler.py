from pathlib import Path
import shutil
import logging
from typing import Dict, Optional, Union
from voice_processing import VoiceKeySystem
from encryption import Encrypter
from visualization import VoiceVisualizer

class EncryptionHandler:
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
            
        self.data_dir = project_root / 'data'
        self.to_encrypt_dir = self.data_dir / 'to_encrypt'
        self.output_dir = self.data_dir / 'output'
        self.audio_samples_dir = self.data_dir / 'audio_samples'
        
        # Crear directorios necesarios
        for directory in [self.to_encrypt_dir, self.output_dir, self.audio_samples_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        self.voice_system = VoiceKeySystem()
        self.encrypter = Encrypter()
        self.visualizer = VoiceVisualizer(str(self.output_dir))
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('EncryptionHandler')

    def process_file_encryption(self, file_name: Optional[str] = None) -> Dict[str, Union[bool, str, float]]:
        """
        Procesa la encriptación de un archivo específico o el primer archivo encontrado en to_encrypt.
        
        Args:
            file_name (str, optional): Nombre del archivo a encriptar. Si es None, se usa el primer archivo encontrado.
            
        Returns:
            Dict con información sobre el proceso:
                - success: bool indicando si el proceso fue exitoso
                - message: str con mensaje descriptivo
                - encrypted_file: str con la ruta del archivo encriptado (si existe)
                - similarity: float con el valor de similitud de voz (si aplica)
                - visualization: str con la ruta de la visualización (si existe)
        """
        try:
            # 1. Encontrar el archivo a encriptar
            if file_name:
                file_to_encrypt = self.to_encrypt_dir / file_name
                if not file_to_encrypt.exists():
                    return {
                        'success': False,
                        'message': f"Archivo '{file_name}' no encontrado en el directorio to_encrypt"
                    }
            else:
                files = list(self.to_encrypt_dir.glob('*'))
                if not files:
                    return {
                        'success': False,
                        'message': "No se encontraron archivos para encriptar"
                    }
                file_to_encrypt = files[0]

            self.logger.info(f"Procesando archivo: {file_to_encrypt}")

            # 2. Verificar audio de entrada
            input_file = self.audio_samples_dir / "user_input.wav"
            if not input_file.exists():
                return {
                    'success': False,
                    'message': "No se encontró el archivo de audio de entrada"
                }

            # 3. Verificar voz y generar visualización
            result = self.voice_system.verify_voice(input_file)
            vis_path = self.visualizer.create_visualizations(str(input_file))

            if not result['matches']:
                return {
                    'success': False,
                    'message': "Voz no autorizada",
                    'similarity': result['max_similarity'],
                    'visualization': str(vis_path)
                }

            # 4. Encriptar archivo
            if 'encryption_data' not in result or not result['encryption_data']:
                return {
                    'success': False,
                    'message': "Error generando datos de encriptación",
                    'similarity': result['max_similarity']
                }

            key = result['encryption_data']['key_bytes']
            encrypted_file = self.encrypter.encrypt_file(str(file_to_encrypt), key)

            if not encrypted_file:
                return {
                    'success': False,
                    'message': "Error durante la encriptación",
                    'similarity': result['max_similarity']
                }

            # 5. Mover archivo encriptado al directorio de salida
            encrypted_path = self.output_dir / Path(encrypted_file).name
            if encrypted_path.exists():
                encrypted_path.unlink()
            shutil.move(encrypted_file, encrypted_path)

            # 6. Opcionalmente, mover el archivo original a un directorio de procesados
            processed_dir = self.to_encrypt_dir / 'processed'
            processed_dir.mkdir(exist_ok=True)
            shutil.move(str(file_to_encrypt), str(processed_dir / file_to_encrypt.name))

            return {
                'success': True,
                'message': "Archivo encriptado exitosamente",
                'encrypted_file': str(encrypted_path),
                'similarity': result['max_similarity'],
                'visualization': str(vis_path)
            }

        except Exception as e:
            self.logger.error(f"Error en process_file_encryption: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}"
            }

    def get_available_files(self) -> list[str]:
        """
        Obtiene la lista de archivos disponibles para encriptar.
        
        Returns:
            Lista de nombres de archivos en el directorio to_encrypt
        """
        try:
            return [f.name for f in self.to_encrypt_dir.glob('*') if f.is_file()]
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de archivos: {str(e)}")
            return []

    def cleanup_old_files(self, max_age_days: int = 7):
        """
        Limpia archivos antiguos del directorio de salida.
        
        Args:
            max_age_days: Edad máxima de los archivos en días
        """
        try:
            import time
            current_time = time.time()
            
            for file in self.output_dir.glob('*'):
                if file.is_file():
                    file_age = current_time - file.stat().st_mtime
                    if file_age > max_age_days * 24 * 3600:
                        file.unlink()
                        self.logger.info(f"Archivo antiguo eliminado: {file}")
        except Exception as e:
            self.logger.error(f"Error durante la limpieza de archivos: {str(e)}")

def encrypt_file_bot_handler(file_name: Optional[str] = None) -> Dict[str, Union[bool, str, float]]:
    """
    Función wrapper para ser llamada desde el bot de Telegram.
    
    Args:
        file_name: Nombre del archivo a encriptar (opcional)
        
    Returns:
        Diccionario con el resultado del proceso
    """
    handler = EncryptionHandler()
    return handler.process_file_encryption(file_name)