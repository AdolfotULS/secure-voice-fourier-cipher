import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft
import librosa
from pathlib import Path
import os

class VoiceVisualizer:
    def __init__(self, output_dir=None):
        # Obtener la ruta base del proyecto
        self.base_dir = Path(__file__).parent.parent
        
        # Si no se proporciona output_dir, usar la ruta por defecto
        if output_dir is None:
            self.output_dir = self.base_dir / "data" / "output"
        else:
            self.output_dir = Path(output_dir)
        
        # Crear directorio si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
            
    def clean_existing_visualizations(self):
        """
        Elimina visualizaciones existentes
        """
        # Convertir la ruta a Path si es string
        output_dir = Path(self.output_dir)
        for file in output_dir.glob('*.png'):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error eliminando visualización {file}: {str(e)}")

    def create_visualizations(self, audio_file):
        """
        Crea y guarda las visualizaciones para un archivo de audio
        """
        # Eliminar visualizaciones existentes
        self.clean_existing_visualizations()
        
        # Cargar audio
        y, sr = librosa.load(str(audio_file), sr=44100)
        
        # Crear figura con subplots
        plt.figure(figsize=(15, 12))
        
        # 1. Forma de onda
        plt.subplot(3, 1, 1)
        times = np.linspace(0, len(y)/sr, len(y))
        plt.plot(times, y)
        plt.title('Forma de Onda')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid(True)
        
        # 2. Espectrograma
        plt.subplot(3, 1, 2)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        librosa.display.specshow(D, y_axis='log', x_axis='time', sr=sr)
        plt.colorbar(format='%+2.0f dB')
        plt.title('Espectrograma')
        
        # 3. Coeficientes de Fourier
        plt.subplot(3, 1, 3)
        fft_result = fft(y)
        freqs = np.linspace(0, sr, len(fft_result))
        magnitudes = np.abs(fft_result)
        
        # Solo mostrar hasta 5000 Hz para mejor visualización
        mask = freqs <= 5000
        plt.semilogy(freqs[mask], magnitudes[mask])
        plt.title('Espectro de Frecuencias (FFT)')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud (log)')
        plt.grid(True)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar visualización
        output_path = str(Path(self.output_dir) / 'analisis_voz.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

    def create_comparison_plot(self, reference_audio, test_audio):
        """
        Crea una visualización comparativa entre el audio de referencia y el de prueba
        """
        # Cargar ambos audios
        y_ref, sr = librosa.load(str(reference_audio), sr=44100)
        y_test, sr = librosa.load(str(test_audio), sr=44100)
        
        # Igualar las longitudes al mínimo
        min_length = min(len(y_ref), len(y_test))
        y_ref = y_ref[:min_length]
        y_test = y_test[:min_length]
        
        # Crear figura con subplots
        plt.figure(figsize=(15, 10))
        
        # 1. Comparación de formas de onda
        plt.subplot(2, 1, 1)
        times = np.linspace(0, min_length/sr, min_length)
        plt.plot(times, y_ref, label='Referencia', alpha=0.7)
        plt.plot(times, y_test, label='Prueba', alpha=0.7)
        plt.title('Comparación de Formas de Onda')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.legend()
        plt.grid(True)
        
        # 2. Comparación de espectros
        plt.subplot(2, 1, 2)
        
        # Calcular FFT con la misma longitud para ambas señales
        n_fft = 2048  # Tamaño fijo para la FFT
        fft_ref = np.abs(fft(y_ref, n=n_fft))
        fft_test = np.abs(fft(y_test, n=n_fft))
        freqs = np.linspace(0, sr/2, n_fft//2)  # Solo frecuencias positivas
        
        # Usar solo la primera mitad del espectro (frecuencias positivas)
        fft_ref = fft_ref[:n_fft//2]
        fft_test = fft_test[:n_fft//2]
        
        # Aplicar máscara para mostrar solo hasta 5000 Hz
        mask = freqs <= 5000
        plt.semilogy(freqs[mask], fft_ref[mask], label='Referencia', alpha=0.7)
        plt.semilogy(freqs[mask], fft_test[mask], label='Prueba', alpha=0.7)
        plt.title('Comparación de Espectros de Frecuencia')
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud (log)')
        plt.legend()
        plt.grid(True)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar visualización
        output_path = str(Path(self.output_dir) / 'comparacion_audios.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

def main():
    visualizer = VoiceVisualizer()
    
    try:
        # Definir rutas usando Path
        audio_samples_dir = visualizer.base_dir / "data" / "audio_samples"
        test_file = audio_samples_dir / "user_input.wav"
        ref_file = audio_samples_dir / "usuario1_ref_1.wav"
        
        # Generar visualizaciones
        if test_file.exists():
            print("Generando visualizaciones del audio de entrada...")
            analysis_path = visualizer.create_visualizations(test_file)
            print(f"Visualización guardada en: {analysis_path}")
            
            if ref_file.exists():
                print("\nGenerando comparación con audio de referencia...")
                comparison_path = visualizer.create_comparison_plot(ref_file, test_file)
                print(f"Comparación guardada en: {comparison_path}")
            else:
                print(f"Archivo de referencia no encontrado: {ref_file}")
        else:
            print(f"Archivo de audio no encontrado: {test_file}")
            
    except Exception as e:
        print(f"Error durante la visualización: {str(e)}")

if __name__ == "__main__":
    main()