import bot_interface
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
from scipy.signal import butter, filtfilt
import librosa
import json
import os
from datetime import datetime
import visualization

class VoiceKeySystem:
    def __init__(self, base_dir="./data"):
        self.sample_rate = 44100
        self.base_dir = base_dir
        self.audio_samples_dir = os.path.join(base_dir, "audio_samples")
        self.users_dir = os.path.join(base_dir, "authorized_users")
        self.output_dir = os.path.join(base_dir, "output")
        self.auth_user_dir = os.path.join(self.users_dir, "usuario1")  # Solo un usuario autorizado
        
        # Crear directorios si no existen
        for directory in [self.audio_samples_dir, self.users_dir, self.output_dir, self.auth_user_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Cargar referencias existentes
        self.references = self.load_references()

    def load_references(self):
        """
        Carga las referencias de voz existentes del usuario autorizado
        """
        references = []
        if os.path.exists(self.auth_user_dir):
            for filename in sorted(os.listdir(self.auth_user_dir)):
                if filename.endswith('.json'):
                    with open(os.path.join(self.auth_user_dir, filename), 'r') as f:
                        references.append(json.load(f))
        return references

    def process_audio(self, audio_file):
        """
        Procesa el archivo de audio y extrae sus características
        """
        try:
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            # Aplicar filtro paso banda para frecuencias de voz (300-3400 Hz)
            b, a = butter(4, [300/self.sample_rate*2, 3400/self.sample_rate*2], btype='band')
            y_filtered = filtfilt(b, a, y)
            
            # Normalizar la señal
            y_normalized = y_filtered / np.max(np.abs(y_filtered))
            
            # Aplicar FFT
            fft_result = fft(y_normalized)
            
            # Obtener magnitudes y fases
            magnitudes = np.abs(fft_result[:len(fft_result)//2])
            phases = np.angle(fft_result[:len(fft_result)//2])
            
            # Obtener los coeficientes más significativos
            num_coefficients = 512
            top_indices = np.argsort(magnitudes)[-num_coefficients:]
            top_magnitudes = magnitudes[top_indices]
            top_phases = phases[top_indices]
            
            return {
                'magnitudes': top_magnitudes.tolist(),
                'phases': top_phases.tolist(),
                'indices': top_indices.tolist(),
                'fft_length': len(fft_result)
            }
            
        except Exception as e:
            print(f"Error procesando audio: {str(e)}")
            return None

    def process_reference_files(self):
        """
        Procesa los archivos de referencia del usuario autorizado
        """
        if not os.path.exists(self.auth_user_dir):
            os.makedirs(self.auth_user_dir)
            
        ref_files = sorted([f for f in os.listdir(self.audio_samples_dir) 
                          if f.startswith('usuario1_ref') and f.endswith('.wav')])
        
        for i, ref_file in enumerate(ref_files, 1):
            print(f"Procesando referencia {i}: {ref_file}")
            filepath = os.path.join(self.audio_samples_dir, ref_file)
            coefficients = self.process_audio(filepath)
            if coefficients:
                self.save_reference(coefficients, i)
                print(f"Referencia {i} guardada exitosamente")
            else:
                print(f"Error procesando referencia {i}")

    def save_reference(self, coefficients, ref_number):
        """
        Guarda los coeficientes como referencia
        """
        filename = f"reference_{ref_number}.json"
        filepath = os.path.join(self.auth_user_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(coefficients, f)

    def prepare_encryption_key(self, coefficients):
        """
        Prepara una clave más segura usando los coeficientes
        """
        # Usar tanto magnitudes como fases para más entropía
        magnitudes = np.array(coefficients['magnitudes'])
        phases = np.array(coefficients['phases'])
        
        # Combinar magnitudes y fases
        combined = np.concatenate([magnitudes, phases])
        
        # Aplicar una función hash simple para distribuir mejor los valores
        combined_hash = np.zeros(16, dtype=np.uint8)
        for i in range(len(combined)):
            # Usar el índice como semilla para variar más los valores
            val = (combined[i] * 1000 + i) % 256
            # XOR con el valor actual para propagar cambios
            combined_hash[i % 16] ^= int(val)
        
        # Asegurar que no hay valores repetidos consecutivos
        for i in range(1, 16):
            if combined_hash[i] == combined_hash[i-1]:
                combined_hash[i] = (combined_hash[i] + 73) % 256  # 73 es primo
        
        return {
            'key_bytes': combined_hash.tobytes(),
            'key_array': combined_hash.tolist(),
            'original_coefficients': coefficients
        }

    def save_encryption_data(self, encryption_data, operation='encrypt'):
        """
        Guarda los datos de cifrado en un formato compatible
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar clave en formato binario
        bin_filename = f"key_{operation}_{timestamp}.bin"
        bin_filepath = os.path.join(self.output_dir, bin_filename)
        with open(bin_filepath, 'wb') as f:
            f.write(encryption_data['key_bytes'])
        
        # Guardar información completa en JSON
        json_filename = f"key_data_{operation}_{timestamp}.json"
        json_filepath = os.path.join(self.output_dir, json_filename)
        
        json_data = {
            'key_array': encryption_data['key_array'],
            'timestamp': timestamp,
            'operation': operation,
            'original_coefficients': encryption_data['original_coefficients']
        }
        
        with open(json_filepath, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        return {
            'binary_file': bin_filepath,
            'json_file': json_filepath
        }

    def verify_voice(self, input_audio_file, similarity_threshold=0.85, operation='encrypt'):
        """
        Verifica si la voz coincide con las referencias y genera la clave si coincide
        """
        if not self.references:
            raise ValueError("No hay referencias almacenadas")
        
        test_coefficients = self.process_audio(input_audio_file)
        if not test_coefficients:
            raise ValueError("No se pudo procesar el audio de entrada")
        
        similarities = []
        for ref in self.references:
            correlation = np.corrcoef(ref['magnitudes'], test_coefficients['magnitudes'])[0,1]
            similarities.append(correlation)
        
        max_similarity = np.max(similarities)
        avg_similarity = np.mean(similarities)
        
        matches = max_similarity > similarity_threshold
        
        output_files = None
        encryption_data = None
        if matches:
            encryption_data = self.prepare_encryption_key(test_coefficients)
            output_files = self.save_encryption_data(encryption_data, operation)
        
        return {
            'matches': matches,
            'max_similarity': max_similarity,
            'avg_similarity': avg_similarity,
            'similarities': similarities,
            'encryption_data': encryption_data,
            'output_files': output_files
        }

def print_results(result):
    """
    Imprime los resultados de la verificación de manera formateada
    """
    print("\nResultados de la verificación:")
    print("-" * 40)
    
    if result['matches']:
        print("✅ Voz autorizada verificada correctamente")
        print(f"Similitud: {result['max_similarity']:.2%}")
        
        if result['output_files']:
            print("\nArchivos generados:")
            print(f"Clave binaria: {result['output_files']['binary_file']}")
            print(f"Datos completos: {result['output_files']['json_file']}")
            
            # Mostrar los primeros bytes de la clave
            key_array = result['encryption_data']['key_array']
            print("\nPrimeros bytes de la clave (en decimal):")
            print(key_array[:16])
    else:
        print("❌ Voz no autorizada")
    
    print("\nSimilitudes con cada referencia:")
    for i, sim in enumerate(result['similarities'], 1):
        print(f"Referencia {i}: {sim:.2%}")

def main():
    system = VoiceKeySystem()
    
    try:
        # Procesar y guardar referencias si no existen
        if not system.references:
            print("Procesando archivos de referencia...")
            system.process_reference_files()
            system.references = system.load_references()
        
        # Verificar voz de entrada
        input_file = os.path.join(system.audio_samples_dir, "user_input.wav")
        if os.path.exists(input_file):
            print("\nVerificando voz de entrada...")
            result = system.verify_voice(input_file, operation='encrypt')
            print_results(result)
        else:
            print(f"Archivo de entrada no encontrado: {input_file}")
            
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        
    if result['matches']:
        visualizer = visualization.VoiceVisualizer()
        analysis_path = visualizer.create_visualizations(input_file)
        print(f"\nVisualización guardada en: {analysis_path}")

if __name__ == "__main__":
    main()