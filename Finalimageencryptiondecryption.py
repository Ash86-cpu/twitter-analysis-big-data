import os
import time
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from memory_profiler import profile


def generate_key():
    key = os.urandom(16)  # Generate a random 16-byte key
    return key


@profile
def encrypt_image_symmetric(image_path, key):
    with open(image_path, 'rb') as file:
        image_data = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    padded_image_data = pad(image_data, cipher.block_size)  # Apply PKCS7 padding

    encrypted_image_data = cipher.encrypt(padded_image_data)

    encrypted_image_path = os.path.splitext(image_path)[0] + '_blowfish_encrypted.png'
    with open(encrypted_image_path, 'wb') as file:
        file.write(encrypted_image_data)

    key_path = os.path.join(os.path.dirname(image_path), 'encryption_key.bin')
    with open(key_path, 'wb') as file:
        file.write(key)

    print('Symmetric encryption complete.')
    print('Encrypted image saved as', encrypted_image_path)
    print('Encryption key saved as', key_path)


@profile
def decrypt_image_symmetric(encrypted_image_path, key_path):
    with open(encrypted_image_path, 'rb') as file:
        encrypted_image_data = file.read()

    with open(key_path, 'rb') as file:
        key = file.read()

    cipher = Blowfish.new(key, Blowfish.MODE_ECB)

    decrypted_image_data = cipher.decrypt(encrypted_image_data)

    unpadded_image_data = unpad(decrypted_image_data, cipher.block_size)  # Remove PKCS7 padding

    decrypted_image_path = os.path.splitext(encrypted_image_path)[0] + '_blowfish_decrypted.png'
    with open(decrypted_image_path, 'wb') as file:
        file.write(unpadded_image_data)

    print('Symmetric decryption complete.')
    print('Decrypted image saved as', decrypted_image_path)


@profile
def encrypt_image_asymmetric(image_path, public_key_pem):
    with open(image_path, 'rb') as file:
        image_data = file.read()

    segment_size = 214  # Adjust segment size as needed
    segments = segment_plaintext(image_data, segment_size)

    encrypted_segments = encrypt_segments(segments, RSA.import_key(public_key_pem))
    combined_encrypted_text = combine_encrypted_segments(encrypted_segments)

    encrypted_image_path = os.path.splitext(image_path)[0] + '_keygeneration_encrypted.png'
    with open(encrypted_image_path, 'wb') as file:
        file.write(combined_encrypted_text)

    print('Asymmetric encryption complete.')
    print('Encrypted image saved as', encrypted_image_path)


@profile
def decrypt_image_asymmetric(encrypted_image_path, private_key_pem):
    private_key = RSA.import_key(private_key_pem)

    with open(encrypted_image_path, 'rb') as file:
        encrypted_image_data = file.read()

    decrypted_image_data = decrypt_combined_encrypted_text(encrypted_image_data, private_key)

    decrypted_image_path = os.path.splitext(encrypted_image_path)[0] + '_keygeneration_decrypted.png'
    with open(decrypted_image_path, 'wb') as file:
        file.write(decrypted_image_data)

    print('Asymmetric decryption complete.')
    print('Decrypted image saved as', decrypted_image_path)


def segment_plaintext(plaintext, segment_size):
    segments = []
    for i in range(0, len(plaintext), segment_size):
        segment = plaintext[i:i + segment_size]
        segments.append(segment)
    return segments


def encrypt_segments(segments, public_key):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_segments = []
    for segment in segments:
        encrypted_segment = cipher_rsa.encrypt(segment)
        encrypted_segments.append(encrypted_segment)
    return encrypted_segments


def combine_encrypted_segments(encrypted_segments):
    combined_encrypted_text = b"".join(encrypted_segments)
    return combined_encrypted_text


def decrypt_combined_encrypted_text(combined_encrypted_text, private_key):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_segments = []
    segment_size = private_key.size_in_bytes()  # Adjust segment size to match the key size
    for i in range(0, len(combined_encrypted_text), segment_size):
        segment = combined_encrypted_text[i:i + segment_size]
        decrypted_segment = cipher_rsa.decrypt(segment)
        decrypted_segments.append(decrypted_segment)
    decrypted_text = b"".join(decrypted_segments)
    return decrypted_text


def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


def main():
    encryption_choice = input("Choose encryption type (Symmetric:1 or Asymmetric:2): ")
    if encryption_choice.lower() == "1":
        operation_choice = input("Do you want to encrypt or decrypt? (E/D): ")
        if operation_choice.lower() == "e":
            image_path = input("Enter the path of the image: ").strip('"')
            key = generate_key()
            encrypt_image_symmetric(image_path, key)
        elif operation_choice.lower() == "d":
            encrypted_image_path = input("Enter the path of the encrypted image: ").strip('"')
            key_path = input("Enter the path to the encryption key: ").strip('"')
            decrypt_image_symmetric(encrypted_image_path, key_path)
        else:
            print('Invalid choice. Please choose "E" for encryption or "D" for decryption.')
    elif encryption_choice.lower() == "2":
        operation_choice = input("Do you want to encrypt or decrypt? (E/D): ")
        if operation_choice.lower() == "e":
            image_path = input("Enter the path of the image: ").strip('"')

            private_key, public_key = generate_key_pair()

            encrypted_image_folder = os.path.dirname(image_path)
            private_key_path = os.path.join(encrypted_image_folder, 'private_key.pem')

            with open(private_key_path, 'wb') as file:
                file.write(private_key)

            encrypt_image_asymmetric(image_path, public_key)
            
        elif operation_choice.lower() == "d":
            encrypted_image_path = input("Enter the path of the encrypted image: ").strip('"')
            private_key_path = input("Enter the path to the private key: ").strip('"')

            with open(private_key_path, 'rb') as file:
                private_key = file.read()

            decrypt_image_asymmetric(encrypted_image_path, private_key)
        else:
            print('Invalid choice. Please choose "E" for encryption or "D" for decryption.')
    else:
        print('Invalid encryption choice. Please choose either "Symmetric" or "Asymmetric".')


if __name__ == "__main__":
    start_time = time.time()
    main()
    execution_time = time.time() - start_time
    print('Total Execution Time:', '{:.6f} seconds'.format(execution_time))
