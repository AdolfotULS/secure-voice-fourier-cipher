import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
from scipy.signal import butter, filtfilt
import librosa
import json
import os
from datetime import datetime

class VoiceKeySystem:
    def __init__(self, base_dir="./data"):
        self.sample_rate = 44100
        self.base_dir = base_dir
        self.audio_samples_dir = os.path.join(base_dir, "audio_samples")
        self.users_dir = os.path.join(base_dir, "authorized_users")
        
        # Cargar todos los usuarios y sus referencias
        self.users = self.load_all_users()
    
    def load_all_users(self):
        """
        Carga las referencias de todos los usuarios
        """
        users = {}
        if os.path.exists(self.users_dir):
            for user_dir in os.listdir(self.users_dir):
                user_path = os.path.join(self.users_dir, user_dir)
                if os.path.isdir(user_path):
                    references = []
                    for filename in sorted(os.listdir(user_path)):
                        if filename.endswith('.json'):
                            with open(os.path.join(user_path, filename), 'r') as f:
                                references.append(json.load(f))
                    users[user_dir] = references
        return users

    def process_audio(self, audio_file):
        """
        Procesa el archivo de audio y extrae sus características
        """
        try:
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            b, a = butter(4, [300/self.sample_rate*2, 3400/self.sample_rate*2], btype='band')
            y_filtered = filtfilt(b, a, y)
            
            y_normalized = y_filtered / np.max(np.abs(y_filtered))
            
            fft_result = fft(y_normalized)
            
            magnitudes = np.abs(fft_result[:len(fft_result)//2])
            phases = np.angle(fft_result[:len(fft_result)//2])
            
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

    def save_reference(self, user_id, coefficients, ref_number):
        """
        Guarda los coeficientes como referencia para un usuario específico
        """
        user_dir = os.path.join(self.users_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
        filename = f"reference_{ref_number}.json"
        filepath = os.path.join(user_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(coefficients, f)

    def process_references_for_user(self, user_id):
        """
        Procesa los archivos de referencia para un usuario específico
        """
        ref_files = sorted([f for f in os.listdir(self.audio_samples_dir) 
                          if f.startswith(f'{user_id}_ref') and f.endswith('.wav')])
        
        for i, ref_file in enumerate(ref_files, 1):
            print(f"Procesando referencia {i} para {user_id}: {ref_file}")
            filepath = os.path.join(self.audio_samples_dir, ref_file)
            coefficients = self.process_audio(filepath)
            if coefficients:
                self.save_reference(user_id, coefficients, i)
                print(f"Referencia {i} guardada exitosamente para {user_id}")
            else:
                print(f"Error procesando referencia {i} para {user_id}")

    def verify_voice(self, test_audio_file, similarity_threshold=0.85):
        """
        Verifica si la voz coincide con algún usuario autorizado
        """
        if not self.users:
            raise ValueError("No hay usuarios registrados")
        
        test_coefficients = self.process_audio(test_audio_file)
        if not test_coefficients:
            raise ValueError("No se pudo procesar el audio de prueba")
        
        best_match = {
            'user_id': None,
            'similarity': 0,
            'matches': False
        }
        
        all_results = {}
        
        for user_id, references in self.users.items():
            user_similarities = []
            for ref in references:
                correlation = np.corrcoef(
                    ref['magnitudes'],
                    test_coefficients['magnitudes']
                )[0,1]
                user_similarities.append(correlation)
            
            if user_similarities:
                max_similarity = np.max(user_similarities)
                avg_similarity = np.mean(user_similarities)
                
                all_results[user_id] = {
                    'max_similarity': max_similarity,
                    'avg_similarity': avg_similarity,
                    'individual_similarities': user_similarities
                }
                
                if max_similarity > best_match['similarity']:
                    best_match['similarity'] = max_similarity
                    best_match['user_id'] = user_id
        
        best_match['matches'] = best_match['similarity'] > similarity_threshold
        
        return {
            'best_match': best_match,
            'all_results': all_results,
            'coefficients': test_coefficients if best_match['matches'] else None
        }

def print_results(result):
    """
    Imprime los resultados de la verificación de manera formateada
    """
    print("\nResultados de la verificación:")
    print("-" * 40)
    
    if result['best_match']['matches']:
        print(f"✅ Voz verificada correctamente")
        print(f"Usuario identificado: {result['best_match']['user_id']}")
        print(f"Similitud: {result['best_match']['similarity']:.2%}")
    else:
        print("❌ La voz no coincide con ningún usuario autorizado")
    
    print("\nResultados por usuario:")
    for user_id, data in result['all_results'].items():
        print(f"\n{user_id}:")
        print(f"  Similitud máxima: {data['max_similarity']:.2%}")
        print(f"  Similitud promedio: {data['avg_similarity']:.2%}")
        print("  Similitudes individuales:")
        for i, sim in enumerate(data['individual_similarities'], 1):
            print(f"    Referencia {i}: {sim:.2%}")
    
    if result['coefficients'] is not None:
        coeffs = result['coefficients']
        print("\nCoeficientes disponibles para cifrado:")
        print(f"- Número de coeficientes: {len(coeffs['magnitudes'])}")
        print(f"- Rango de magnitudes: [{min(coeffs['magnitudes']):.2f}, {max(coeffs['magnitudes']):.2f}]")

def main():
    system = VoiceKeySystem()
    
    try:
        # Lista de usuarios a procesar
        users = ['usuario1', 'usuario2']  # Puedes añadir más usuarios aquí
        
        # Procesar referencias para cada usuario si no existen
        for user_id in users:
            if user_id not in system.users or not system.users[user_id]:
                print(f"\nProcesando archivos de referencia para {user_id}...")
                system.process_references_for_user(user_id)
        
        # Recargar referencias
        system.users = system.load_all_users()
        
        # Verificar voz de prueba
        test_file = os.path.join(system.audio_samples_dir, "test_voice.wav")
        if os.path.exists(test_file):
            print("\nVerificando voz de prueba...")
            result = system.verify_voice(test_file)
            print_results(result)
        else:
            print(f"Archivo de prueba no encontrado: {test_file}")
            
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main()