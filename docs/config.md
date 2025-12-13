# Config Reference

Config file: `~/.vault-cli/config.json`.

- `vault_db_path` (string): Path to SQLite DB. Defaults to `~/.vault-cli/vault.db`.
- `backup_dir` (string): Directory where `vault backup` places DB backups.
- `workspace_dir` (string): Optional directory where decrypted files can be copied when using `--to-workspace`.
- `git_repo_path` (string): Optional local git repository path for `vault git_push`.

Use `vault config show` and `vault config set <key> <value>` to update values.

Permissions:
- The config file is stored under user home; permissions are set to be readable and writable by the user only where possible.
