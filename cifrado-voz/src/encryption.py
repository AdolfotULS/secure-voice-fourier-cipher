import numpy as np
from scipy.linalg import inv

class Encryption:
    def __init__(self):
        pass

    def generate_key(self, fft_coefficients):
        """
        Genera una matriz de clave a partir de los coeficientes FFT.
        Asegura que la matriz generada sea invertible para el cifrado de Hill.
        """
        size = int(np.sqrt(len(fft_coefficients)))  # Crear una matriz cuadrada
        if size * size != len(fft_coefficients):
            raise ValueError("Los coeficientes FFT deben permitir una matriz cuadrada.")
        
        matrix = np.array(fft_coefficients[:size*size]).reshape(size, size)
        if np.linalg.det(matrix) == 0:
            raise ValueError("La matriz generada debe ser invertible.")
        
        # Asegurar que la matriz sea invertible en aritmetica modular (mod 256 aqui)
        # Ajustar la matriz para que sea adecuada para el cifrado
        matrix = np.mod(matrix, 256)
        return matrix.astype(int)

    def encrypt_file(self, file, key):
        """
        Cifra un archivo usando la matriz de clave proporcionada.
        """
        with open(file, 'rb') as f:
            data = f.read()
        
        # Rellenar para hacer que el tamano de los datos sea un multiplo del tamano de la clave
        key_size = key.shape[0]
        if len(data) % key_size != 0:
            padding_length = key_size - (len(data) % key_size)
            data += bytes([0] * padding_length)
        
        data_array = np.array([data[i:i + key_size] for i in range(0, len(data), key_size)])
        encrypted_data = []

        for block in data_array:
            vector = np.array(list(block)).reshape(-1, 1)
            encrypted_vector = np.mod(np.dot(key, vector), 256).flatten()
            encrypted_data.extend(encrypted_vector.astype(int).tolist())

        encrypted_bytes = bytes(encrypted_data)

        # Escribir los datos cifrados en un nuevo archivo
        encrypted_file = file + '.enc'
        with open(encrypted_file, 'wb') as f:
            f.write(encrypted_bytes)
        
        return encrypted_file

    def decrypt_file(self, encrypted_file, key):
        """
        Descifra un archivo usando la matriz de clave proporcionada.
        """
        # Calcular la inversa modular de la matriz de clave (mod 256)
        key_inv = np.round(inv(key)).astype(int) % 256

        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        key_size = key.shape[0]
        data_array = np.array([encrypted_data[i:i + key_size] for i in range(0, len(encrypted_data), key_size)])
        decrypted_data = []

        for block in data_array:
            vector = np.array(list(block)).reshape(-1, 1)
            decrypted_vector = np.mod(np.dot(key_inv, vector), 256).flatten()
            decrypted_data.extend(decrypted_vector.astype(int).tolist())

        decrypted_bytes = bytes(decrypted_data).rstrip(b'\x00')  # Remover relleno

        decrypted_file = encrypted_file.replace('.enc', '_dec')
        with open(decrypted_file, 'wb') as f:
            f.write(decrypted_bytes)
        
        return decrypted_file
