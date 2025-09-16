# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions of Scentinel:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Scentinel seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please send an email to the project maintainer with:
- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (if available)

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt of your report within 48 hours
- **Initial Assessment**: We'll provide an initial assessment within 5 business days
- **Progress Updates**: Regular updates on our progress toward a fix
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Responsible Disclosure

We follow responsible disclosure practices:
- We'll work with you to understand and resolve the issue
- We'll credit you for the discovery (unless you prefer to remain anonymous)
- We'll coordinate the timing of any public disclosure

## Security Considerations

### Data Protection

Scentinel stores personal fragrance data locally in SQLite databases. Users should be aware that:

- **Local Storage**: All data is stored locally on your device
- **No Cloud Sync**: We don't transmit personal data to external servers
- **Backup Security**: Exported JSON/CSV files contain your personal collection data
- **Import Validation**: Be cautious when importing data from untrusted sources

### File Import Security

When importing CSV/JSON files:
- Only import files from trusted sources
- Review imported data before saving
- Be aware that malicious files could potentially corrupt your database
- Keep backups of your collection before importing large datasets

### Dependencies

We regularly update our dependencies to address known vulnerabilities:
- Monitor security advisories for Python packages
- Update dependencies promptly when security patches are available
- Review `requirements.txt` for any vulnerable packages

### Executable Security

When using the pre-built executable:
- Download only from official GitHub releases
- Verify the integrity of downloaded files
- Run antivirus scans if desired
- Be aware that some antivirus software may flag Python executables as suspicious

### Development Security

For developers:
- Use virtual environments to isolate dependencies
- Keep development dependencies updated
- Review code changes for potential security implications
- Sanitize any user inputs in new features

## Best Practices for Users

1. **Regular Backups**: Export your collection data regularly
2. **Trusted Sources**: Only import data from trusted sources
3. **Updates**: Keep Scentinel updated to the latest version
4. **Local Access**: Be mindful of who has access to your device and data
5. **File Permissions**: Ensure appropriate file permissions on your database files

## Security Features

Scentinel includes several security-conscious design decisions:

- **Local-First**: No external data transmission
- **Input Validation**: User inputs are validated and sanitized
- **Database Integrity**: SQLAlchemy helps prevent SQL injection
- **File Handling**: Safe file import/export procedures

## Known Limitations

- **Local Storage Only**: Data is not encrypted at rest
- **Single User**: No user authentication system (designed for personal use)
- **File Imports**: Limited validation of imported data structure

## Contact

For security-related questions or concerns, please contact the project maintainer through GitHub.

---

**Note**: This security policy may be updated as the project evolves. Please check back regularly for the most current information.