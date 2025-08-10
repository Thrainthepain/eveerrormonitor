# Security Policy

## Supported Versions

The following versions of the Eve Online Crash Monitor are currently supported with security updates:

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | :white_check_mark: | Current stable release |
| 0.9.x   | :warning:          | Legacy support (critical fixes only) |
| < 0.9   | :x:                | No longer supported |

## Security Considerations

This project monitors system processes and Windows Event Logs, which requires consideration of the following security aspects:

### System Access
- **Process Monitoring**: Requires access to system process information
- **Event Log Access**: Reads Windows Event Logs (may require administrative privileges)
- **File System Access**: Creates log files in the project directory

### Data Handling
- **Process Information**: Collects process names, PIDs, and memory usage
- **Event Log Data**: Reads system crash and error events
- **Local Storage**: All data is stored locally in text files
- **No Network Communication**: The monitor does not send data externally

### Recommended Security Practices
1. **Run with Minimum Privileges**: While the monitor can run without admin rights, some Event Log features require elevation
2. **Review Log Files**: Regularly review generated log files for sensitive information
3. **Secure Log Directory**: Ensure the `logs/` directory has appropriate file permissions
4. **Virtual Environment**: Use the provided virtual environment to isolate dependencies

## Reporting a Vulnerability

If you discover a security vulnerability in the Eve Online Crash Monitor, please report it responsibly:

### Where to Report
- **Issues**: Create an issue on the project repository with the label "security"
- **Private Disclosure**: For sensitive vulnerabilities, contact the maintainer directly

### What to Include
Please provide the following information in your report:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested remediation (if available)
- Your contact information for follow-up

### Response Timeline
- **Initial Acknowledgment**: Within 48 hours
- **Preliminary Assessment**: Within 1 week
- **Resolution Timeline**: Varies based on severity
  - Critical: 1-7 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next scheduled release

### What to Expect
- **Accepted Vulnerabilities**: Will receive a CVE identifier if applicable, and a fix will be prioritized
- **Declined Reports**: Will receive an explanation of why the issue doesn't qualify as a security vulnerability
- **Credit**: Security researchers will be credited in release notes (unless anonymity is requested)

## Security Features

### Built-in Protections
- **Read-Only Monitoring**: The monitor only reads system information, never modifies processes
- **Local Data Storage**: No external data transmission
- **Configurable Scope**: Monitoring can be limited to specific processes
- **Minimal Dependencies**: Uses only essential, well-maintained Python packages

### Configuration Security
- **Default Safe Settings**: Conservative default configuration
- **Process Filtering**: Ability to limit monitoring scope
- **Log Rotation**: Prevents unbounded log file growth
- **No Credential Storage**: No passwords or sensitive credentials are stored

## Threat Model

### In Scope
- Privilege escalation vulnerabilities
- Information disclosure through log files
- Code injection through configuration files
- Dependency vulnerabilities in required packages

### Out of Scope
- Physical access to the system
- Vulnerabilities in Eve Online itself
- Windows operating system vulnerabilities
- Network-based attacks (project has no network components)

## Security Updates

Security updates will be:
- Released as soon as possible after verification
- Documented in release notes
- Tagged with security labels
- Backward compatible when possible

## Contact

For security-related questions or concerns that don't rise to the level of a vulnerability report, feel free to open a general issue or contact the maintainer.

---

**Note**: This project is designed for personal use to monitor Eve Online crashes. While security is important, the scope is limited to local system monitoring without network exposure.

