from vault.crypto.aes import decrypt, encrypt
from vault.crypto.kdf import derive_key, generate_salt

password = "StrongPassword123!"
salt = generate_salt()

key = derive_key(password, salt)

data = b"super-secret-data"
iv, ciphertext = encrypt(key, data)
plaintext = decrypt(key, iv, ciphertext)

assert plaintext == data
print("Crypto test passed.")
