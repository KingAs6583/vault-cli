# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-12-13
### Added
- Filename-as-key behavior for file secrets: filenames (including extension) are used as keys when adding files.
- Workspace commands: `workspace import` and `workspace open` for importing decrypted files into a local workspace and opening the directory.
- `vault config` subcommands: `show` and `set` for managing configuration values.
- CLI `--version` support retrieving the package version from packaging metadata.
- Documentation and developer guides in `docs/`.
- Basic changelog and version bump to 0.2.0.

### Changed
- Backup and git commands use configured `backup_dir` and `git_repo_path`.
- Added secure temp file handling and cleanup.
- Database upsert preserves `created_at` timestamps.
- Added WAL mode and index on the DB for performance.
- Logging redaction for secrets.

### Fixed
- IV length validation for AES-GCM operations.
- Avoid passing secrets on the CLI command line (interactive prompts used instead).


## [Unreleased]
### Added
- Lightweight DB migrations system with a migration to add `filename` to the `secrets` table.

### Changed
- Datetime usage migrated to timezone-aware UTC across the codebase.

### Planned
- Consider migrating KDF to Argon2
- Streaming backup encryption for large DB files
