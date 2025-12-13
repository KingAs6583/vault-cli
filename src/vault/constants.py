# vault/constants.py

# Crypto
AES_KEY_LENGTH = 32        # 256 bits
AES_GCM_IV_LENGTH = 12     # Recommended for GCM
KDF_ITERATIONS = 200_000
KDF_SALT_LENGTH = 16

# Password
MIN_PASSWORD_LENGTH = 8

# Temp files
TEMP_FILE_PREFIX = "vault_tmp_"
