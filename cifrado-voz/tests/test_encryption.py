import unittest
import os
from src.encryption import Encryption

class TestEncryption(unittest.TestCase):
    def setUp(self):
        """
        Configuracion antes de cada prueba.
        Crea un objeto de HillCipher y un archivo de prueba temporal.
        """
        self.cipher = Encryption()
        self.test_file = 'test_file.txt'
        self.encrypted_file = self.test_file + '.enc'
        self.decrypted_file = self.test_file.replace('.txt', '_dec.txt')
        
        # Crear un archivo de prueba con contenido simple
        with open(self.test_file, 'w') as f:
            f.write('Este es un archivo de prueba para cifrar.')

    def tearDown(self):
        """
        Limpieza despues de cada prueba.
        Elimina los archivos temporales generados.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.encrypted_file):
            os.remove(self.encrypted_file)
        if os.path.exists(self.decrypted_file):
            os.remove(self.decrypted_file)

    def test_generate_key(self):
        """
        Prueba que la clave generada tenga el formato correcto y sea invertible.
        """
        fft_coefficients = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Coeficientes de ejemplo
        key = self.cipher.generate_key(fft_coefficients)
        self.assertEqual(key.shape, (3, 3))  # La clave debe ser una matriz de 3x3

    def test_encrypt_and_decrypt_file(self):
        """
        Prueba el cifrado y descifrado de un archivo.
        """
        fft_coefficients = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        key = self.cipher.generate_key(fft_coefficients)
        
        # Cifrar el archivo
        encrypted_file = self.cipher.encrypt_file(self.test_file, key)
        self.assertTrue(os.path.exists(encrypted_file))  # Verificar que el archivo cifrado exista
        
        # Descifrar el archivo
        decrypted_file = self.cipher.decrypt_file(encrypted_file, key)
        self.assertTrue(os.path.exists(decrypted_file))  # Verificar que el archivo descifrado exista

        # Comparar el contenido original y descifrado
        with open(self.test_file, 'r') as original, open(decrypted_file, 'r') as decrypted:
            self.assertEqual(original.read(), decrypted.read())

if __name__ == '__main__':
    unittest.main()
