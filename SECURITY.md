# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, report security issues via:
- **GitHub Security Advisories**: [Report a vulnerability](https://github.com/dburge86/kenpom-mcp/security/advisories/new)
- **Email**: dburge86@gmail.com (use "SECURITY" in subject line)

### What to Include

Please include the following information in your report:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (critical issues prioritized)

### Disclosure Policy

- We follow coordinated vulnerability disclosure
- Please allow us reasonable time to fix the issue before public disclosure
- We will credit you in the fix (unless you prefer to remain anonymous)

## Security Best Practices for Users

### Credential Protection

**Never commit credentials to version control:**
- Your `.env` file contains sensitive KenPom credentials
- Always keep `.env` in `.gitignore` (already configured)
- Use `.env.example` as a template (contains no real credentials)

### API Key Security

If deploying to production:
- Rotate your API key if it's ever exposed
- Use strong, randomly generated API keys: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Store API keys in environment variables, not code
- Use different API keys for dev/staging/production

### Cloud Run Security

If deploying to Google Cloud Run:
- Set environment variables via `gcloud run deploy --set-env-vars` (not in code)
- Enable authentication if you don't need public access
- Use `--max-instances 1` to prevent runaway scaling costs
- Monitor usage and set billing alerts

### KenPom Account Security

- Use a unique password for your KenPom account
- Enable 2FA on your email account (password reset protection)
- Don't share KenPom credentials between multiple deployments
- Monitor your KenPom subscription for unusual activity

## Known Security Considerations

### Rate Limiting
- The scraper implements caching to reduce load on KenPom servers
- Default cache TTLs: 60s (live games) to 3600s (static data)
- Respect KenPom's terms of service - don't abuse the service

### Authentication
- Login credentials are stored in memory only (not persisted to disk)
- Session cookies are ephemeral and expire after logout
- No credentials are logged (even in debug mode)

### Dependencies
- We use GitHub Dependabot to monitor for vulnerable dependencies
- Pre-commit hooks enforce code quality and catch common issues
- CI pipeline runs security linting via ruff

## Security Features

✅ **Environment Variable Usage**: All credentials loaded from `.env`
✅ **No Hardcoded Secrets**: Code contains no credentials
✅ **API Key Protection**: Cloud deployment requires authentication
✅ **Retry Logic**: Exponential backoff prevents credential lockout
✅ **Input Validation**: All user inputs validated before processing
✅ **HTTPS Only**: All external requests use secure connections

## Questions?

For general security questions (non-vulnerability), feel free to:
- Open a GitHub Discussion
- Email dburge86@gmail.com with "QUESTION" in subject

---

**Last Updated**: 2026-02-02
