# test_encryption.py
# IGNACIA MIRANDA - NO BORRAR COMENTARIOS PLISS

import unittest
import numpy as np
import os
from Crypto.Cipher import AES
from src.encryption import Encrypter

class TestEncrypter(unittest.TestCase):

    def setUp(self):
        self.encrypter = Encrypter()
        self.sample_file = 'sample.txt'
        self.encrypted_file = self.sample_file + '.enc'
        self.decrypted_file = self.sample_file + '.dec'

        # Crear un archivo de prueba
        with open(self.sample_file, 'w') as f:
            f.write('Este es un texto de prueba para cifrado y descifrado.')

    def tearDown(self):
        # Eliminar archivos de prueba generados
        for file in [self.sample_file, self.encrypted_file, self.decrypted_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_generate_key(self):
        # Generar coeficientes de Fourier de prueba
        fft_coefficients = np.random.random(20)

        # Generar la clave
        key = self.encrypter.generate_key(fft_coefficients)

        # Verificar que la clave tenga exactamente 16 bytes
        self.assertEqual(len(key), 16)

    def test_encrypt_file(self):
        # Generar una clave aleatoria de 16 bytes
        fft_coefficients = np.random.random(20)
        key = self.encrypter.generate_key(fft_coefficients)

        # Cifrar el archivo
        encrypted_file = self.encrypter.encrypt_file(self.sample_file, key)

        # Verificar que el archivo cifrado fue creado
        self.assertTrue(os.path.exists(encrypted_file))

    def test_decrypt_file(self):
        # Generar una clave aleatoria de 16 bytes
        fft_coefficients = np.random.random(20)
        key = self.encrypter.generate_key(fft_coefficients)

        # Cifrar el archivo
        self.encrypter.encrypt_file(self.sample_file, key)

        # Descifrar el archivo cifrado
        decrypted_file = self.encrypter.decrypt_file(self.encrypted_file, key)

        # Verificar que el archivo descifrado fue creado
        self.assertTrue(os.path.exists(decrypted_file))

        # Verificar que el contenido descifrado es igual al original
        with open(self.sample_file, 'rb') as f_orig, open(decrypted_file, 'rb') as f_dec:
            original_content = f_orig.read()
            decrypted_content = f_dec.read()
            self.assertEqual(original_content, decrypted_content)

if __name__ == '__main__':
    unittest.main()
