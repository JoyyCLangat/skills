# Security

## What must never be in this repository

This repository is **public**. Never commit:

- client names, client-specific configuration, or anything under NDA
- environment URLs, tenant IDs, credentials, keys, certificates, or connection strings
- customer or staff personal data: exports, migration files, screenshots
- pricing, rates, or margins

## How it's enforced

| Layer | What it does |
|---|---|
| Guard hook (`plugins/impax-crm/hooks/guard.py`) | In Claude Code, blocks writing secrets to files, passing them on the command line, and committing or pushing secrets or credential files. Asks before commands that change a Power Platform environment, and before committing data files or bulk personal data. |
| `scripts/validate.py` (CI) | Scans every tracked file for credentials and the public playbook for URLs, emails, and phone numbers. |
| GitHub | Turn on **secret scanning** and **push protection** under Settings → Code security, and protect `main` (require pull requests and passing CI). |

The guard is a safety net, not a sandbox. It matches the normal spelling of commands and known secret formats. Claude Code's permission settings remain the hard control.

## If a secret was committed

1. **Rotate it first** (Entra ID app registration, M-Pesa portal, Azure). Removing it from git doesn't un-leak it.
2. Remove it from the code and replace it with a reference (Key Vault, environment variable).
3. Tell your lead, and the client if the credential was theirs.

## Reporting a problem

Open a private security advisory on this repository (Security → Advisories → Report a vulnerability), or contact the maintainer directly. Don't open a public issue for security problems.
