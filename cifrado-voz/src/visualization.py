import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft
import librosa
import os
from datetime import datetime
from pathlib import Path  # Añadida esta importación

class VoiceVisualizer:
    def __init__(self, output_dir="./data/output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
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
        output_path = str(Path(self.output_dir) / 'voice_analysis.png')
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
        
        # Crear figura con subplots
        plt.figure(figsize=(15, 10))
        
        # 1. Comparación de formas de onda
        plt.subplot(2, 1, 1)
        times_ref = np.linspace(0, len(y_ref)/sr, len(y_ref))
        times_test = np.linspace(0, len(y_test)/sr, len(y_test))
        plt.plot(times_ref, y_ref, label='Referencia', alpha=0.7)
        plt.plot(times_test, y_test, label='Prueba', alpha=0.7)
        plt.title('Comparación de Formas de Onda')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.legend()
        plt.grid(True)
        
        # 2. Comparación de espectros
        plt.subplot(2, 1, 2)
        fft_ref = np.abs(fft(y_ref))
        fft_test = np.abs(fft(y_test))
        freqs = np.linspace(0, sr, len(fft_ref))
        
        # Solo mostrar hasta 5000 Hz
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
        output_path = str(Path(self.output_dir) / 'voice_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

def main():
    visualizer = VoiceVisualizer()
    
    try:
        # Ruta a los archivos de audio
        base_dir = Path(__file__).parent.parent / "data"
        audio_samples_dir = base_dir / "audio_samples"
        test_file = audio_samples_dir / "user_input.wav"
        ref_file = audio_samples_dir / "usuario1_ref_1.wav"
        
        # Generar visualizaciones
        if test_file.exists():
            print("Generando visualizaciones del audio de entrada...")
            analysis_path = visualizer.create_visualizations(test_file)
            print(f"Visualizaciones guardadas en: {analysis_path}")
            
            if ref_file.exists():
                print("\nGenerando comparación con audio de referencia...")
                comparison_path = visualizer.create_comparison_plot(ref_file, test_file)
                print(f"Comparación guardada en: {comparison_path}")
        else:
            print("Archivo de audio no encontrado")
            
    except Exception as e:
        print(f"Error durante la visualización: {str(e)}")

if __name__ == "__main__":
    main()