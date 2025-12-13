# Architecture Overview

Vault CLI's components:

- CLI (`src/vault/cli.py`): click-based command dispatcher.
- Commands (`src/vault/commands/*`): Each command group registers subcommands and handles input and user interaction.
- Crypto (`src/vault/crypto/*`): AES-GCM and KDF logic, deriving keys from passphrases, and handling salts/IVs.
- Storage (`src/vault/storage/*`): SQLite DB operations, secret model, backups and backup encryption.
- Config (`src/vault/config.py`): Local config file at `~/.vault-cli/config.json`.
- Logging (`src/vault/logging.py`): Redaction and logging helper utilities.

Design Decisions:
- Zero-knowledge encryption: secrets are encrypted locally; no background decryption or cloud storage.
- Filename-as-key: file secrets use the filename (including extension) as the logical key, helping versioning and workspace workflows.
- Config-driven architecture: operations use configuration values specified by the user; default locations exist but can be changed via `vault config set`.

Security:
- Uses AES-GCM with 12-byte IV (recommended) and unique salt per secret.
- KDF is PBKDF2-HMAC111 with security parameters in constants; consider Argon2 for future improvements.
- Temporary files are created via `mkstemp` and permissions are set; cleanup overwrites file contents in a best-effort manner.

Database:
- SQLite with WAL mode and indices for performance on project/environment queries.
- Upsert logic preserves `created_at` while updating `updated_at` on secret updates.
