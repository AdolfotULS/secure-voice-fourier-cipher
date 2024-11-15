# Sistema de Cifrado Biométrico por Voz

Universidad de La Serena  
Departamento de Matemáticas  
Asignatura: Matemática IV  
Profesor: Dr. Eric Jeltsch Figueroa

Sistema de cifrado dual que combina biometría de voz con análisis de Transformada de Fourier para el cifrado seguro de archivos.

## Características

- Autenticación biométrica basada en voz
- Análisis de Transformada de Fourier para generación de claves únicas
- Cifrado AES en modo CFB
- Manejo seguro de archivos a través de interfaz de bot de Telegram
- Visualización en tiempo real de señales de voz
- Manejo robusto de errores y medidas de seguridad

## Requisitos

- Python 3.8+
- Paquetes requeridos:
  ```
  numpy
  scipy
  python-telegram-bot
  pycryptodome
  librosa
  matplotlib
  python_speech_features
  ```

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone [url-repositorio]
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar token del bot de Telegram en `bot_interface.py`

4. Crear directorios requeridos:
   ```
   /data
     /audio_samples    # Para muestras de audio
     /test_files      # Para archivos de prueba
     /output          # Para archivos cifrados
     /to_encrypt      # Para archivos a cifrar
   ```

## Uso

1. Iniciar el bot:
   ```bash
   python bot_interface.py
   ```

2. Comandos disponibles en Telegram:
   - `/start` - Iniciar el bot
   - `/cifrar` - Cifrar un archivo
   - `/descifrar` - Descifrar un archivo
   - `/grabar_audio` - Grabar mensaje de voz
   - `/eliminar_audio` - Eliminar muestra de voz
   - `/mostrar_graficos` - Ver visualizaciones
   - `/Agregar_archivo` - Añadir archivo para cifrar

## Estructura del Proyecto

```
├── src/
│   ├── encryption.py         # Implementación del cifrado
│   ├── voice_processing.py   # Procesamiento de voz y FFT
│   ├── visualization.py      # Visualizaciones y gráficos
│   └── bot_interface.py      # Interfaz de Telegram
├── data/                     # Directorio de datos
└── tests/                    # Pruebas unitarias
```

## Seguridad

- Utiliza cifrado AES en modo CFB
- Implementa verificación de voz biométrica
- Manejo seguro de archivos temporales
- Protección contra ataques de reproducción
- Validación de integridad de datos

## Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -m 'Añadir nueva característica'`
4. Push a la rama: `git push origin feature/nueva-caracteristica`
5. Enviar Pull Request
