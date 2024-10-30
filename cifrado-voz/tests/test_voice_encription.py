#!/usr/bin/env python3
from pathlib import Path
import sys
import shutil

# Añadir el directorio src al path de Python
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from encryption_handler import EncryptionHandler

def test_encryption_direct():
    """
    Prueba directa de la funcionalidad de encriptación
    """
    print("\n=== Test de Encriptación Directo ===\n")
    
    # 1. Inicializar el handler
    handler = EncryptionHandler()
    
    # 2. Mostrar archivos disponibles
    print("Archivos disponibles para encriptar:")
    available_files = handler.get_available_files()
    if not available_files:
        print("⚠️  No hay archivos en el directorio to_encrypt")
        
        # Crear archivo de prueba
        test_file = handler.to_encrypt_dir / "test_file.txt"
        print(f"\nCreando archivo de prueba: {test_file}")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Este es un archivo de prueba para encriptación")
            
        available_files = handler.get_available_files()

    # Mostrar archivos
    for i, file in enumerate(available_files, 1):
        print(f"{i}. {file}")

    # 3. Permitir selección de archivo
    while True:
        try:
            selection = input("\nSelecciona el número del archivo a encriptar (o 'q' para salir): ")
            
            if selection.lower() == 'q':
                print("\nSaliendo...")
                break
                
            file_index = int(selection) - 1
            if 0 <= file_index < len(available_files):
                selected_file = available_files[file_index]
                break
            else:
                print("❌ Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")

    # 4. Procesar encriptación
    print(f"\nProcesando archivo: {selected_file}")
    result = handler.process_file_encryption(selected_file)

    # 5. Mostrar resultados
    print("\n=== Resultados ===")
    if result['success']:
        print("✅ Encriptación exitosa!")
        print(f"📁 Archivo encriptado: {result['encrypted_file']}")
        print(f"🎯 Similitud de voz: {result['similarity']:.2%}")
        if 'visualization' in result:
            print(f"📊 Visualización guardada en: {result['visualization']}")
    else:
        print(f"❌ Error: {result['message']}")
        if 'similarity' in result:
            print(f"🎯 Similitud de voz: {result['similarity']:.2%}")

    # 6. Mostrar contenido de los directorios
    print("\n=== Estado de los Directorios ===")
    print("\nDirectorio to_encrypt:")
    for file in handler.to_encrypt_dir.glob('*'):
        if file.is_file():
            print(f"  - {file.name}")

    print("\nDirectorio output:")
    for file in handler.output_dir.glob('*'):
        if file.is_file():
            print(f"  - {file.name}")

def cleanup(handler):
    """Limpia los archivos de prueba"""
    try:
        # Eliminar archivos de prueba
        test_file = handler.to_encrypt_dir / "test_file.txt"
        if test_file.exists():
            test_file.unlink()
            
        # Limpiar directorios de salida
        for file in handler.output_dir.glob('*.enc'):
            file.unlink()
            
    except Exception as e:
        print(f"\nError durante la limpieza: {e}")

if __name__ == "__main__":
    try:
        test_encryption_direct()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
    finally:
        # Opcional: descomentar para limpiar archivos de prueba
        # handler = EncryptionHandler()
        # cleanup(handler)
        print("\nTest completado")