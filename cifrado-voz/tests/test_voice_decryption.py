# test_decrypt.py
import os
from pathlib import Path
import sys

# Añadir el directorio src al path de Python
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root / 'src'))

from voice_processing import VoiceKeySystem
from encryption import Encrypter
from visualization import VoiceVisualizer

def test_decrypt():
    # Configurar directorios usando Path
    data_dir = project_root / 'data'
    output_dir = data_dir / "output"
    
    # Crear directorios si no existen
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar sistemas
    voice_system = VoiceKeySystem()
    encrypter = Encrypter()
    visualizer = VoiceVisualizer(str(output_dir))
    
    try:
        # Buscar archivo cifrado en el directorio de salida
        encrypted_files = list(output_dir.glob('*.enc'))
        if not encrypted_files:
            raise FileNotFoundError("No se encontraron archivos cifrados en output/")
        
        encrypted_file = encrypted_files[0]
        print(f"\nArchivo cifrado a procesar: {encrypted_file}")
        
        # PROCESO DE DESCIFRADO
        print("\n=== Proceso de Descifrado ===")
        
        # Verificar voz para descifrado
        input_file = data_dir / "audio_samples" / "user_input.wav"
        print("\nVerificando voz para descifrado...")
        result = voice_system.verify_voice(str(input_file), operation='decrypt')
        
        # Generar visualización
        vis_path = visualizer.create_visualizations(str(input_file))
        print(f"Visualización guardada en: {vis_path}")
        
        if result['matches']:
            print("\n✅ Voz autorizada para descifrado")
            print(f"Similitud: {result['max_similarity']:.2%}")
            
            # Generar clave a partir de encryption_data
            if result['encryption_data']:
                key = result['encryption_data']['key_bytes']
                print("\nClave generada para descifrado:", [b for b in key[:8]], "...")
                
                # Descifrar archivo
                decrypted_file = encrypter.decrypt_file(str(encrypted_file), key)
                if decrypted_file:
                    decrypted_path = Path(decrypted_file)
                    print(f"\nArchivo descifrado guardado en: {decrypted_path}")
                    
                    # Mostrar archivos
                    print("\nArchivos existentes:")
                    print(f"Cifrado: {encrypted_file}")
                    print(f"Descifrado: {decrypted_path}")
                else:
                    print("\nError durante el descifrado del archivo")
            else:
                print("\nError: No se generaron los datos de descifrado")
        else:
            print("\n❌ Voz no autorizada para descifrado")
            
    except Exception as e:
        print(f"\nError durante el test: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("=== Test de Descifrado con Voz ===")
        test_decrypt()
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError general: {str(e)}")