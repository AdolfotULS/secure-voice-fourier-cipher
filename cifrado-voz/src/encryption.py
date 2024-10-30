    # IGNACIA MIRANDA - NO BORRAR COMENTARIOS PLISS

import numpy as np
from scipy.fft import fft
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

class Encrypter:

    def generate_key(self, fft_coefficients):
        # Calculamos la magnitud (valor absoluto) de los coeficientes de Fourier
        fft_abs = np.abs(fft_coefficients)

        # Seleccionamos los primeros 16 valores, los convertimos en enteros sin signo de 8 bits y los transformamos en bytes
        key = np.array(fft_abs[:16]).astype(np.uint8).tobytes()

        # Si la longitud de la clave es menor a 16 bytes, la rellenamos con ceros para que sea exactamente de 16 bytes
        if len(key) < 16:
            key = key.ljust(16, b'0')

        return key  # Devolvemos la clave generada

    def encrypt_file(self, file, key):
        # Generamos un vector de inicialización (IV) de 16 bytes para el modo CFB del cifrado AES
        iv = get_random_bytes(16)

        # Creamos un cifrador AES en modo CFB usando la clave generada y el IV
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)

        # Abrimos el archivo original en modo binario para leer sus datos
        with open(file, 'rb') as f:
            encrypted_data = cipher.encrypt(f.read())  # Ciframos el contenido del archivo

        # Guardamos los datos cifrados junto con el IV en un nuevo archivo con extensión '.enc'
        with open(file + '.enc', 'wb') as f_enc:
            f_enc.write(iv + encrypted_data)

        return file + '.enc'  # Devolvemos el nombre del archivo cifrado

    def decrypt_file(self, encrypted_file, key):
        # Abrimos el archivo cifrado y leemos los primeros 16 bytes (el IV) y el resto (los datos cifrados)
        with open(encrypted_file, 'rb') as f_enc:
            iv = f_enc.read(16)  # Leemos el IV (16 bytes)
            encrypted_data = f_enc.read()  # Leemos el contenido cifrado restante

        # Creamos un cifrador AES en modo CFB usando la misma clave y el IV leído del archivo
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)

        # Desciframos los datos y los guardamos
        with open(encrypted_file.replace('.enc', '.dec'), 'wb') as f_dec:
            f_dec.write(cipher.decrypt(encrypted_data))  # Desciframos y escribimos el contenido

        return encrypted_file.replace('.enc', '.dec')  # Devolvemos el nombre del archivo descifrado