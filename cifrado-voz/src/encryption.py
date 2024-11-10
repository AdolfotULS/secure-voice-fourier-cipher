import numpy as np
from scipy.fft import fft
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

class Encrypter:

    def generate_key(self, fft_coefficients):
        try:
            # Calcula la magnitud de los coeficientes de Fourier
            fft_abs = np.abs(fft_coefficients)
            # Selecciona los primeros 16 valores y los convierte en una cadena de bytes
            key = np.array(fft_abs[:16]).astype(np.uint8).tobytes()
            # Asegura que la clave tenga 16 bytes, completando con ceros si es necesario
            if len(key) < 16:
                key = key.ljust(16, b'0')
            return key
        except Exception as e:
            print(f"Error al generar la clave: {e}")
            return None

    def encrypt_file(self, file, key):
        try:
            # Genera un vector de inicialización (IV) de 16 bytes
            iv = get_random_bytes(16)
            # Crea el cifrador AES en modo CFB con la clave y el IV
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
            # Lee y cifra el contenido del archivo original
            with open(file, 'rb') as f:
                encrypted_data = cipher.encrypt(f.read())

            # Guarda los datos cifrados junto con el IV en un nuevo archivo con extensión '.enc'
            encrypted_file = file + '.enc'
            with open(encrypted_file, 'wb') as f_enc:
                f_enc.write(iv + encrypted_data)

            return encrypted_file
        except Exception as e:
            print(f"Error al encriptar el archivo {file}: {e}")
            return None

    def decrypt_file(self, encrypted_file, key):
        try:
            # Lee el IV y los datos cifrados del archivo
            with open(encrypted_file, 'rb') as f_enc:
                iv = f_enc.read(16)
                encrypted_data = f_enc.read()

            # Crea el cifrador AES en modo CFB con la misma clave e IV
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)

            # Elimina la extensión '.enc' para restaurar el nombre y extensión originales
            original_filename = encrypted_file.replace('.enc', '')

            # Descifra los datos y los guarda en un archivo con el nombre original
            with open(original_filename, 'wb') as f_dec:
                f_dec.write(cipher.decrypt(encrypted_data))

            return original_filename
        except Exception as e:
            print(f"Error al desencriptar el archivo {encrypted_file}: {e}")
            return None
