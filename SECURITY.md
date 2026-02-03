# Security Policy

## Reporting a Vulnerability

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, report via:
- [GitHub Security Advisories](https://github.com/dburge86/kenpom-mcp/security/advisories/new)

## Security Notes

- Never commit your `.env` file (it's gitignored)
- The `.env.example` file contains only placeholders
- All credentials are loaded from environment variables
- Cloud Run deployment uses API key authentication
