# test_encrypt.py
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

def test_encrypt():
    # Configurar directorios usando Path
    data_dir = project_root / 'data'
    to_encrypt_dir = data_dir / "to_encrypt"
    output_dir = data_dir / "output"
    
    # Crear directorios si no existen
    to_encrypt_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar sistemas
    voice_system = VoiceKeySystem()
    encrypter = Encrypter()
    visualizer = VoiceVisualizer(str(output_dir))
    
    try:
        # 1. Encontrar archivo a cifrar
        files = [f for f in to_encrypt_dir.glob('*') if f.is_file()]
        if not files:
            raise FileNotFoundError("No se encontraron archivos en to_encrypt/")
        
        file_to_encrypt = files[0]
        print(f"\nArchivo a procesar: {file_to_encrypt}")
        
        # 2. PROCESO DE CIFRADO
        print("\n=== Proceso de Cifrado ===")
        
        # Verificar voz para cifrado
        input_file = data_dir / "audio_samples" / "user_input.wav"
        print("\nVerificando voz para cifrado...")
        result = voice_system.verify_voice(str(input_file), operation='encrypt')
        
        # Generar visualización
        vis_path = visualizer.create_visualizations(str(input_file))
        print(f"Visualización guardada en: {vis_path}")
        
        if result['matches']:
            print("\n✅ Voz autorizada para cifrado")
            print(f"Similitud: {result['max_similarity']:.2%}")
            
            # Generar clave a partir de encryption_data
            if result['encryption_data']:
                key = result['encryption_data']['key_bytes']
                print("\nClave generada para cifrado:", [b for b in key[:8]], "...")
                
                # Cifrar archivo
                encrypted_file = encrypter.encrypt_file(str(file_to_encrypt), key)
                if encrypted_file:
                    encrypted_path = output_dir / Path(encrypted_file).name
                    
                    # Si el archivo ya existe en el destino, eliminarlo
                    if encrypted_path.exists():
                        encrypted_path.unlink()
                    
                    # Mover el archivo cifrado al directorio de salida
                    os.rename(encrypted_file, encrypted_path)
                    print(f"\nArchivo cifrado guardado en: {encrypted_path}")
                else:
                    print("\nError durante el cifrado del archivo")
            else:
                print("\nError: No se generaron los datos de encriptación")
        else:
            print("\n❌ Voz no autorizada para cifrado")
            
    except Exception as e:
        print(f"\nError durante el test: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("=== Test de Cifrado con Voz ===")
        test_encrypt()
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError general: {str(e)}")