#!/usr/bin/env python3
from pathlib import Path
import sys
import shutil

# Añadir el directorio src al path de Python
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from encryption_handler import EncryptionHandler

class DecryptionHandler(EncryptionHandler):
    def __init__(self):
        super().__init__()
        self.decrypted_dir = self.data_dir / 'decrypted'
        self.decrypted_dir.mkdir(parents=True, exist_ok=True)

    def process_file_decryption(self, file_name: str = None) -> dict:
        """
        Procesa la desencriptación de un archivo.
        
        Args:
            file_name: Nombre del archivo a desencriptar
            
        Returns:
            Dict con información sobre el proceso
        """
        try:
            # 1. Encontrar archivo a desencriptar
            if file_name:
                file_to_decrypt = self.output_dir / file_name
                if not file_to_decrypt.exists():
                    return {
                        'success': False,
                        'message': f"Archivo '{file_name}' no encontrado"
                    }
            else:
                encrypted_files = list(self.output_dir.glob('*.enc'))
                if not encrypted_files:
                    return {
                        'success': False,
                        'message': "No se encontraron archivos encriptados"
                    }
                file_to_decrypt = encrypted_files[0]

            self.logger.info(f"Desencriptando archivo: {file_to_decrypt}")

            # 2. Verificar audio
            input_file = self.audio_samples_dir / "user_input.wav"
            if not input_file.exists():
                return {
                    'success': False,
                    'message': "Archivo de audio no encontrado"
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

            # 4. Desencriptar archivo
            if 'encryption_data' not in result or not result['encryption_data']:
                return {
                    'success': False,
                    'message': "Error generando datos de desencriptación",
                    'similarity': result['similarity']
                }

            key = result['encryption_data']['key_bytes']
            
            # Desencriptar y mover a carpeta de desencriptados
            decrypted_file = self.encrypter.decrypt_file(str(file_to_decrypt), key)
            if not decrypted_file:
                return {
                    'success': False,
                    'message': "Error durante la desencriptación"
                }

            # Mover archivo desencriptado a su carpeta
            decrypted_path = self.decrypted_dir / Path(decrypted_file).name
            if decrypted_path.exists():
                decrypted_path.unlink()
            shutil.move(decrypted_file, decrypted_path)

            return {
                'success': True,
                'message': "Archivo desencriptado exitosamente",
                'decrypted_file': str(decrypted_path),
                'similarity': result['max_similarity'],
                'visualization': str(vis_path)
            }

        except Exception as e:
            self.logger.error(f"Error en process_file_decryption: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"Error inesperado: {str(e)}"
            }

    def get_encrypted_files(self) -> list[str]:
        """Obtiene la lista de archivos encriptados disponibles"""
        try:
            return [f.name for f in self.output_dir.glob('*.enc')]
        except Exception as e:
            self.logger.error(f"Error listando archivos encriptados: {str(e)}")
            return []

def test_decryption_direct():
    """
    Prueba directa de la funcionalidad de desencriptación
    """
    print("\n=== Test de Desencriptación Directo ===\n")
    
    # 1. Inicializar el handler
    handler = DecryptionHandler()
    
    # 2. Mostrar archivos disponibles
    print("Archivos encriptados disponibles:")
    available_files = handler.get_encrypted_files()
    
    if not available_files:
        print("⚠️  No hay archivos encriptados disponibles")
        print("Por favor, encripta algún archivo primero.")
        return
    
    # Mostrar archivos
    for i, file in enumerate(available_files, 1):
        print(f"{i}. {file}")

    # 3. Permitir selección de archivo
    while True:
        try:
            selection = input("\nSelecciona el número del archivo a desencriptar (o 'q' para salir): ")
            
            if selection.lower() == 'q':
                print("\nSaliendo...")
                return
                
            file_index = int(selection) - 1
            if 0 <= file_index < len(available_files):
                selected_file = available_files[file_index]
                break
            else:
                print("❌ Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")

    # 4. Procesar desencriptación
    print(f"\nProcesando archivo: {selected_file}")
    result = handler.process_file_decryption(selected_file)

    # 5. Mostrar resultados
    print("\n=== Resultados ===")
    if result['success']:
        print("✅ Desencriptación exitosa!")
        print(f"📁 Archivo desencriptado: {result['decrypted_file']}")
        print(f"🎯 Similitud de voz: {result['similarity']:.2%}")
        if 'visualization' in result:
            print(f"📊 Visualización guardada en: {result['visualization']}")
    else:
        print(f"❌ Error: {result['message']}")
        if 'similarity' in result:
            print(f"🎯 Similitud de voz: {result['similarity']:.2%}")

    # 6. Mostrar contenido de los directorios
    print("\n=== Estado de los Directorios ===")
    print("\nDirectorio output (archivos encriptados):")
    for file in handler.output_dir.glob('*.enc'):
        print(f"  - {file.name}")

    print("\nDirectorio decrypted (archivos desencriptados):")
    for file in handler.decrypted_dir.glob('*'):
        if file.is_file():
            print(f"  - {file.name}")

def cleanup(handler):
    """Limpia los archivos de prueba"""
    try:
        # Limpiar directorio de desencriptados
        for file in handler.decrypted_dir.glob('*'):
            if file.is_file():
                file.unlink()
    except Exception as e:
        print(f"\nError durante la limpieza: {e}")

if __name__ == "__main__":
    try:
        test_decryption_direct()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
    finally:
        # Opcional: descomentar para limpiar archivos de prueba
        # handler = DecryptionHandler()
        # cleanup(handler)
        print("\nTest completado")