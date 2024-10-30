import numpy as np
import librosa
from scipy.signal import butter, filtfilt
from scipy.fft import fft
import python_speech_features
from sklearn.preprocessing import StandardScaler
import json
from pathlib import Path
from datetime import datetime

class VoiceKeySystem:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "data"
        self.audio_samples_dir = self.base_dir / "audio_samples"
        self.users_dir = self.base_dir / "authorized_users"
        self.output_dir = self.base_dir / "output"
        self.auth_user_dir = self.users_dir / "usuario1"
        
        for directory in [self.audio_samples_dir, self.users_dir, self.output_dir, self.auth_user_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.references = self.load_references()

    def load_references(self):
        """Carga las referencias de voz existentes"""
        references = []
        if self.auth_user_dir.exists():
            for filename in sorted(self.auth_user_dir.glob("*.json")):
                try:
                    with open(filename, 'r') as f:
                        ref_data = json.load(f)
                        # Convertir las listas JSON de vuelta a arrays numpy
                        for key in ref_data:
                            if isinstance(ref_data[key], list):
                                ref_data[key] = np.array(ref_data[key])
                        references.append(ref_data)
                except Exception as e:
                    print(f"Error loading reference {filename}: {e}")
        return references

    def extract_voice_features(self, audio_file):
        """Extrae características de la voz"""
        try:
            # Cargar y normalizar el audio
            y, sr = librosa.load(str(audio_file), sr=22050)
            y = librosa.util.normalize(y)
            
            # 1. Extraer MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 2. Obtener espectrograma mel
            mel_spect = librosa.feature.melspectrogram(y=y, sr=sr)
            
            # 3. Características espectrales básicas
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # 4. FFT
            fft_result = np.abs(fft(y))[:len(y)//2]
            
            # Crear diccionario de características con arrays numpy
            features = {
                'mfcc_features': np.mean(mfccs, axis=1),
                'mel_features': np.mean(mel_spect, axis=1),
                'spectral_centroid': np.mean(spectral_centroids),
                'zero_crossing_rate': np.mean(zero_crossing_rate),
                'fft_features': self.compute_fft_profile(fft_result)
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting voice features: {str(e)}")
            return None

    def find_formant_peaks(self, formant_magnitudes, freqs, n_formants=3):
        """Encuentra los primeros n_formants formantes en el espectro"""
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(formant_magnitudes, distance=20)
        peak_freqs = freqs[peaks]
        peak_mags = formant_magnitudes[peaks]
        
        # Ordenar por magnitud y tomar los más prominentes
        sorted_indices = np.argsort(peak_mags)[-n_formants:]
        return peak_freqs[sorted_indices].tolist()

    def compute_fft_profile(self, fft_result, n_bands=24):
        """Computa el perfil FFT en bandas"""
        bands = np.array_split(fft_result, n_bands)
        return np.array([np.mean(band) for band in bands])

    def compare_features(self, features1, features2):
        """Compara dos conjuntos de características de voz"""
        try:
            # Calcular similitud para cada característica
            mfcc_sim = np.corrcoef(features1['mfcc_features'], features2['mfcc_features'])[0,1]
            mel_sim = np.corrcoef(features1['mel_features'], features2['mel_features'])[0,1]
            fft_sim = np.corrcoef(features1['fft_features'], features2['fft_features'])[0,1]
            
            # Comparar características escalares
            spectral_sim = 1 - abs(features1['spectral_centroid'] - features2['spectral_centroid']) / (features1['spectral_centroid'] + 1e-10)
            zcr_sim = 1 - abs(features1['zero_crossing_rate'] - features2['zero_crossing_rate']) / (features1['zero_crossing_rate'] + 1e-10)
            
            # Ponderación de similitudes
            weights = {
                'mfcc': 0.4,
                'mel': 0.3,
                'fft': 0.2,
                'spectral': 0.05,
                'zcr': 0.05
            }
            
            total_similarity = (
                weights['mfcc'] * mfcc_sim +
                weights['mel'] * mel_sim +
                weights['fft'] * fft_sim +
                weights['spectral'] * spectral_sim +
                weights['zcr'] * zcr_sim
            )
            
            return max(0, total_similarity)
            
        except Exception as e:
            print(f"Error comparing features: {e}")
            return 0
    
    def verify_voice(self, input_audio_file, similarity_threshold=0.85):
        """Verifica si la voz coincide con las referencias"""
        if not self.references:
            raise ValueError("No hay referencias almacenadas")
        
        test_features = self.extract_voice_features(input_audio_file)
        if test_features is None:
            raise ValueError("No se pudo procesar el audio de entrada")
        
        similarities = []
        for ref in self.references:
            similarity = self.compare_features(ref, test_features)
            similarities.append(similarity)
        
        max_similarity = max(similarities)
        avg_similarity = np.mean(similarities)
        
        # Verificación más estricta
        matches = (max_similarity > similarity_threshold and 
                  avg_similarity > similarity_threshold * 0.9)
        
        result = {
            'matches': matches,
            'max_similarity': max_similarity,
            'avg_similarity': avg_similarity,
            'similarities': similarities
        }
        
        if matches:
            encryption_data = self.prepare_encryption_key(test_features)
            result['encryption_data'] = encryption_data
            result['output_files'] = self.save_encryption_data(encryption_data)
        
        return result

    def prepare_encryption_key(self, features):
        """Genera una clave de cifrado a partir de las características"""
        # Concatenar todas las características en un solo vector
        feature_vector = np.concatenate([
            features['mfcc_features'],
            features['mel_features'],
            features['fft_features'],
            [features['spectral_centroid']],
            [features['zero_crossing_rate']]
        ])
        
        # Generar clave de 32 bytes
        key = np.zeros(32, dtype=np.uint8)
        
        # Hash personalizado
        for i in range(len(feature_vector)):
            val = int((feature_vector[i] * 1000) % 256)
            key[i % 32] ^= val
            key = np.roll(key, 1 if i % 2 == 0 else -1)
        
        # Asegurar variabilidad
        for i in range(1, 32):
            if key[i] == key[i-1]:
                key[i] = (key[i] + 173) % 256
        
        return {
            'key_bytes': key.tobytes(),
            'key_array': key.tolist(),
            'timestamp': datetime.now().isoformat()
        }

    def load_existing_key(self):
        """Carga la clave existente si existe"""
        try:
            json_filepath = self.output_dir / "voice_key_data.json"
            if json_filepath.exists():
                with open(json_filepath, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading existing key: {str(e)}")
            return None

            
    def clean_output_directory(self, file_pattern):
            """Elimina archivos antiguos que coincidan con el patrón"""
            for file in self.output_dir.glob(file_pattern):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting file {file}: {str(e)}")

    def are_keys_equal(self, key1, key2):
        """Compara dos claves para ver si son iguales"""
        if key1 is None or key2 is None:
            return False
        
        # Comparar arrays de claves
        if 'key_array' in key1 and 'key_array' in key2:
            return key1['key_array'] == key2['key_array']
        
        return False

    def save_encryption_data(self, encryption_data, operation='encrypt'):
        """Guarda los datos de cifrado manteniendo solo una clave a la vez"""
        # Nombres fijos para los archivos
        bin_filepath = self.output_dir / "voice_key.bin"
        json_filepath = self.output_dir / "voice_key_data.json"
        
        # Verificar si ya existe una clave
        existing_data = None
        if json_filepath.exists():
            try:
                with open(json_filepath, 'r') as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"Error reading existing key data: {str(e)}")

        # Comparar si la clave es la misma
        if existing_data and self.are_keys_equal(existing_data, encryption_data):
            print("Using existing key (keys are identical)")
            return {
                'binary_file': str(bin_filepath),
                'json_file': str(json_filepath)
            }

        # Si la clave es diferente o no existe, guardar la nueva
        try:
            # Guardar clave binaria
            with open(bin_filepath, 'wb') as f:
                f.write(encryption_data['key_bytes'])
            
            # Guardar metadatos en JSON
            json_data = {
                'key_array': encryption_data['key_array'],
                'timestamp': encryption_data['timestamp'],
                'operation': operation
            }
            
            with open(json_filepath, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print("New key generated and saved")
            return {
                'binary_file': str(bin_filepath),
                'json_file': str(json_filepath)
            }
        except Exception as e:
            print(f"Error saving encryption data: {str(e)}")
            return None

    def process_reference_files(self):
        """Procesa y guarda las referencias, manteniendo solo una versión por referencia"""
        ref_files = sorted(list(self.audio_samples_dir.glob("usuario1_ref*.wav")))
        
        # Limpiar referencias existentes
        for file in self.auth_user_dir.glob("*.json"):
            file.unlink()
        
        for i, ref_file in enumerate(ref_files, 1):
            print(f"Processing reference {i}: {ref_file.name}")
            features = self.extract_voice_features(ref_file)
            
            if features is not None:
                # Convertir arrays numpy a listas para JSON
                features_json = {
                    key: value.tolist() if isinstance(value, np.ndarray) else value
                    for key, value in features.items()
                }
                
                ref_filename = f"reference_{i}.json"
                ref_filepath = self.auth_user_dir / ref_filename
                
                with open(ref_filepath, 'w') as f:
                    json.dump(features_json, f, indent=2)
                
                print(f"Reference {i} saved successfully")
            else:
                print(f"Error processing reference {i}")

def main():
    """Función principal"""
    system = VoiceKeySystem()
    
    try:
        # Procesar referencias si no existen
        if not system.references:
            print("\nProcessing reference files...")
            system.process_reference_files()
            system.references = system.load_references()
        
        # Verificar voz de entrada
        input_file = system.audio_samples_dir / "user_input.wav"
        if input_file.exists():
            print("\nVerifying input voice...")
            result = system.verify_voice(input_file)
            
            print("\nVerification Results:")
            print("-" * 40)
            
            if result['matches']:
                print("✅ Voice authorized")
                print(f"Similarity: {result['max_similarity']:.2%}")
                
                if result['output_files']:
                    print("\nGenerated Files:")
                    print(f"Binary key: {result['output_files']['binary_file']}")
                    print(f"Full data: {result['output_files']['json_file']}")
            else:
                print("❌ Voice not authorized")
                print(f"Max similarity: {result['max_similarity']:.2%}")
            
            print("\nSimilarity scores:")
            for i, sim in enumerate(result['similarities'], 1):
                print(f"Reference {i}: {sim:.2%}")
        else:
            print(f"Input file not found: {input_file}")
            
    except Exception as e:
        print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    main()