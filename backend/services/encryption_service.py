from Crypto.Cipher import AES, DES3, Blowfish
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

def encrypt_data(data, algo):

    if algo == "AES":
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted = cipher.encrypt(pad(data, AES.block_size))

    elif algo == "3DES":
        key = DES3.adjust_key_parity(get_random_bytes(24))
        cipher = DES3.new(key, DES3.MODE_ECB)
        encrypted = cipher.encrypt(pad(data, DES3.block_size))

    elif algo == "Blowfish":
        key = get_random_bytes(16)
        cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        encrypted = cipher.encrypt(pad(data, Blowfish.block_size))

    return encrypted, key



def decrypt_data(encrypted_data, key, algo):
    if algo == "AES":
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    elif algo == "3DES":
        cipher = DES3.new(key, DES3.MODE_ECB)
        decrypted = unpad(cipher.decrypt(encrypted_data), DES3.block_size)

    elif algo == "Blowfish":
        cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        decrypted = unpad(cipher.decrypt(encrypted_data), Blowfish.block_size)

    return decrypted