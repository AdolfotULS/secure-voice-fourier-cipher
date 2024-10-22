import matplotlib.pyplot as plt
import numpy as np

def plot_waveform(audio_data, sample_rate):
    """
    Crea y muestra una visualizacion de la forma de onda del audio
    """
    time = np.arange(0, len(audio_data)) / sample_rate
    plt.figure(figsize=(12, 4))
    plt.plot(time, audio_data)
    plt.title('Forma de Onda del Audio')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.show()

def plot_fourier_transform(fft_result, sample_rate, num_coefficients=10):
    """
    Crea y muestra una visualizacion de la Transformada de Fourier del audio
    y marca los coeficientes mas significativos
    """
    frequencies = np.fft.fftfreq(len(fft_result), 1/sample_rate)
    magnitude = np.abs(fft_result)
    
    # Encontrar los indices de los coeficientes mas significativos
    top_indices = np.argsort(magnitude)[::-1][:num_coefficients]
    
    plt.figure(figsize=(12, 8))
    
    # Grafico de magnitud
    plt.subplot(2, 1, 1)
    plt.plot(frequencies[:len(frequencies)//2], magnitude[:len(frequencies)//2])
    plt.title('Espectro de Magnitud de la Transformada de Fourier')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Magnitud')
    plt.xscale('log')
    plt.grid(True)
    
    # Marcar los coeficientes mas significativos
    for idx in top_indices:
        if idx < len(frequencies)//2:  # Solo marcar en la mitad positiva del espectro
            plt.plot(frequencies[idx], magnitude[idx], 'ro')
            plt.annotate(f'{frequencies[idx]:.2f} Hz', 
                         (frequencies[idx], magnitude[idx]),
                         textcoords="offset points",
                         xytext=(0,10),
                         ha='center')
    
    # Grafico de fase
    plt.subplot(2, 1, 2)
    phase = np.angle(fft_result)
    plt.plot(frequencies[:len(frequencies)//2], phase[:len(frequencies)//2])
    plt.title('Fase de la Transformada de Fourier')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Fase (radianes)')
    plt.xscale('log')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir los coeficientes mas significativos
    print("Coeficientes mas significativos:")
    for idx in top_indices:
        if idx < len(frequencies)//2:
            print(f"Frecuencia: {frequencies[idx]:.2f} Hz, Magnitud: {magnitude[idx]:.2f}")

def plot_spectrogram(audio_data, sample_rate):
    """
    Crea y muestra un espectrograma del audio
    """
    plt.figure(figsize=(12, 8))
    plt.specgram(audio_data, Fs=sample_rate, cmap='viridis')
    plt.title('Espectrograma')
    plt.xlabel('Tiempo')
    plt.ylabel('Frecuencia')
    plt.colorbar(label='Intensidad (dB)')
    plt.show()

# Ejemplo de uso (puede eliminarse en la version final)
if __name__ == "__main__":
    # Simular datos de audio para probar las funciones de visualizacion
    sample_rate = 44100
    duration = 1  # segundos
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Crear una senal compuesta de varias frecuencias
    frequencies = [440, 880, 1320, 2000, 3000]  # Hz
    audio_data = sum(np.sin(2 * np.pi * f * t) for f in frequencies)
    
    # Anadir un poco de ruido
    audio_data += np.random.normal(0, 0.1, len(audio_data))
    
    # Calcular la FFT
    fft_result = np.fft.fft(audio_data)
    
    # Visualizar
    plot_waveform(audio_data, sample_rate)
    plot_fourier_transform(fft_result, sample_rate, num_coefficients=5)
    plot_spectrogram(audio_data, sample_rate)