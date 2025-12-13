from vault.crypto.kdf import generate_salt, derive_key
from vault.crypto.aes import encrypt, decrypt

password = "StrongPassword123!"
salt = generate_salt()

key = derive_key(password, salt)

data = b"super-secret-data"
iv, ciphertext = encrypt(key, data)
plaintext = decrypt(key, iv, ciphertext)

assert plaintext == data
print("Crypto test passed.")
