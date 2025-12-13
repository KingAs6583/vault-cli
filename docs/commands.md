# Commands Reference

## Setup

`vault setup` - Walks user through first-time setup, asks for DB path, backup dir, workspace, and optional git repo.

## Status

`vault status` - Prints initialized status and paths.

## Config

`vault config show` - Prints config JSON.
`vault config set <key> <value>` - Set config values.

Valid keys:
- `vault_db_path`
- `backup_dir`
- `workspace_dir`
- `git_repo_path`

## Add/Get Secrets

Text:
- `vault add <app> <env> <key>` - adds textual secret (interactive prompt for secret value)
- `vault get <app> <env> <key> [--show]` - retrieves secret (--show reveals the value)
- `vault list <app> <env>` - lists keys for app/env

Files:
- `vault add_file <app> <env> <path>` - add file; filename is used as key
- `vault get_file <app> <env> <filename> [--to-workspace]` - get file; writes to secure temp or workspace

## Workspace

`vault workspace import <app> <env> <filename>` - import decrypted copy into workspace
`vault workspace open` - opens workspace path in file explorer

## Backup

`vault backup` - create a local backup of DB (plaintext DB file)
`vault backup_encrypt` - interactive password encrypt the backup
`vault decrypt_backup <encrypted_file>` - decrypt backup with password

## Git Push

`vault git_push <message>` - create an encrypted backup and push to the configured git repo

