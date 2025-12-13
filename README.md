# Vault CLI 🔐

[![CI Tests](https://github.com/kinga/vault-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/kinga/vault-cli/actions/workflows/ci.yml)
[![Lint](https://github.com/kinga/vault-cli/actions/workflows/lint.yml/badge.svg)](https://github.com/kinga/vault-cli/actions/workflows/lint.yml)

A secure, user-friendly CLI for encrypting and storing local secrets and files using an encrypted SQLite vault.

Key features:
- Encrypted local secrets (AES-GCM) with per-secret salt and IV
- File secrets supported (e.g., .jks), stored with original filename as the key
- Optional plaintext workspace for working copies (explicitly import and clean)
- Git-friendly encrypted backups with `vault git_push`
- Configuration via `~/.vault-cli/config.json`
- CLI commands for setup, config, secrets and backups

Version: 0.2.0

## Installation

Install via pip in editable mode for development:

```bash
pip install -e .
```

The `vault` CLI entry point is setup via `pyproject.toml`.

## First-Time Setup

Run:

```bash
vault setup
```

You will be prompted for:
- Where to store the encrypted vault DB (default `~/.vault-cli/vault.db`)
- Backup directory for encrypted backups
- An optional plaintext workspace path (user-controlled)
- Optional Git repo to store encrypted backups

Configuration is stored at:

`~/.vault-cli/config.json`

## Core Commands

### Status

```bash
vault status
```

Shows initialization status, configuration paths, and checks for repo/backup/workspace.

### Config

Show configuration values:

```bash
vault config show
```

Set configuration values:

```bash
vault config set vault_db_path /path/to/vault.db
vault config set backup_dir /path/to/backups
vault config set workspace_dir /path/to/workspace
vault config set git_repo_path /path/to/git/repo
```

### Text Secrets

Add a text secret (interactive prompt for value):

```bash
vault add myapp dev SECRET_KEY
```

Get a stored text secret (prompts for master password):

```bash
vault get myapp dev SECRET_KEY
```

List secrets for an app/environment:

```bash
vault list myapp dev
```

### File Secrets (filename-as-key)

Files are stored by default using their filename as the key (including extension).

To add a file secret:

```bash
vault add_file myapp dev /full/path/to/app-release.jks
```

To retrieve a file secret into a secure temporary file (preserves filename and extension):

```bash
vault get_file myapp dev app-release.jks
```

You can copy a decrypted file into your configured workspace using `--to-workspace`:

```bash
vault get_file myapp dev app-release.jks --to-workspace
```

### Workspace

Import a file decrypted copy into the configured workspace:

```bash
vault workspace import myapp dev app-release.jks
```

Open the workspace directory in the system file explorer:

```bash
vault workspace open
```

Note: When running in a headless CI environment (for example, GitHub Actions), the `workspace open` command will not attempt to launch a system file explorer and will emit a message: "Skipping opening workspace in CI environment". This prevents errors during automated testing and CI runs.

### Backups and Git Push

Create an encrypted backup of the vault DB:

```bash
vault backup
```

Encrypt a backup using your passphrase (the backup is not stored in plaintext):

```bash
vault backup-encrypt
```

Push encrypted backup into a configured local Git repo:

```bash
vault git_push "daily backup"
```

`git_push` will prompt to set `git_repo_path` if not configured.

## Configuration Keys
- `vault_db_path`: Path to SQLite DB
- `backup_dir`: Directory used to place encrypted backups
- `workspace_dir`: Directory where decrypted files can be copied (optional)
- `git_repo_path`: Local git repo path to store encrypted backups

## Security Model
- Secrets are encrypted client-side using AES-GCM with a per-secret IV and salt
- Password-based key derivation is PBKDF2-HMAC with a configurable iteration count
- Decrypted files are written to temporary files and cleaned up after use. Files copied to workspace are user-controlled
- The DB is not stored in plaintext—only its encrypted content is stored on disk

## Developer Notes

- Code structure:
  - `src/vault/cli.py` — CLI entry point using Click
  - `src/vault/commands/` — Command groups (backup, config, file, text, setup, workspace, git)
  - `src/vault/storage/` — Database and backup utilities
  - `src/vault/crypto/` — AES and KDF utilities
  - `src/vault/logging.py` — Redaction-sensitive logging helpers
  - `docs/` — Developer docs and architecture overview

- Run tests with:

```bash
pytest
```

## Changelog
See `CHANGELOG.md` for a full history.

## Contributing
- Please use `pre-commit` hooks (Black, Ruff, pytest). Linting and format checks run on code pushes and are executed before tests on `push` events. For ad-hoc lint checks, use the `Lint` workflow from the Actions tab (manual run).
- Open a PR for any feature or security changes

### Pre-commit Hooks
To run the project's pre-commit hooks locally (the hooks run `scripts/clean.sh`, linters, formatters, and tests):

```bash
pip install -r requirements-dev.txt
pre-commit install
```

If you want to run the hooks manually against all files, use:

```bash
pre-commit run --all-files
```

Notes:
- Pre-commit is configured to run `scripts/clean.sh` once before commits, run code linters/formatters, run `pytest` (tests), and finally run `clean.sh` after the commit.
- Because `pytest` can be slow, these pre-commit hooks can be disabled temporarily by using `git commit --no-verify` when needed, but it is recommended to keep them enabled for CI parity.

## License
See [LICENSE](LICENSE)
