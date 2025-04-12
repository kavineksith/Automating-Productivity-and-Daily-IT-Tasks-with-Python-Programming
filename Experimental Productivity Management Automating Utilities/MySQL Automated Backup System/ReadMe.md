# MySQL Automated Backup System Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
   - [General Settings](#general-settings)
   - [Database Settings](#database-settings)
   - [Backup Settings](#backup-settings)
   - [Notification Settings](#notification-settings)
6. [Command-Line Interface](#command-line-interface)
7. [Usage Examples](#usage-examples)
8. [Architecture](#architecture)
   - [Class Hierarchy](#class-hierarchy)
   - [Process Flow](#process-flow)
9. [Error Handling](#error-handling)
10. [Scheduling](#scheduling)
11. [Security Considerations](#security-considerations)
12. [Backup Integrity Verification](#backup-integrity-verification)
13. [Email Notifications](#email-notifications)
14. [Logging](#logging)
15. [Production Deployment](#production-deployment)
    - [Systemd Service](#systemd-service)
    - [Docker Deployment](#docker-deployment)
16. [Troubleshooting](#troubleshooting)
17. [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

The MySQL Automated Backup System is a production-ready solution for scheduling and managing MySQL database backups. It provides a comprehensive framework for performing daily, weekly, and monthly backups with integrity verification, email notifications, and detailed logging.

The system is designed for DevOps and database administrators who need a reliable, secure, and configurable tool for automating MySQL database backups across development and production environments.

## Features

- **Scheduled Backups**: Supports daily, weekly, and monthly backup schedules
- **Integrity Verification**: SHA-256 checksums for all backups
- **Email Notifications**: Detailed alerts for successful and failed backup operations
- **Comprehensive Logging**: Detailed logging of all operations with daily rotation
- **Customizable Retention Policies**: Configure how long to keep different types of backups
- **Secure Handling**: Temporary directories for atomic operations, secure credential handling
- **Object-Oriented Design**: Well-structured, maintainable code with clear separation of concerns
- **Advanced Exception Handling**: Custom exception hierarchy with detailed error reporting
- **Production-Ready**: Designed for reliability, security, and maintainability

## System Requirements

- Python 3.6 or higher
- MySQL/MariaDB server
- `mysqldump` command-line utility
- SMTP server for email notifications (optional)
- The `schedule` Python package

## Installation

1. Install the required Python package:

```bash
pip install schedule
```

2. Clone or download the script files:

```bash
git clone https://github.com/your-username/mysql-backup-system.git
cd mysql-backup-system
```

3. Make the script executable:

```bash
chmod +x mysql_backup.py
```

4. Create a configuration file (see [Configuration](#configuration))

## Configuration

The system uses an INI-style configuration file with the following sections:

### General Settings

```ini
[general]
log_dir = /var/log/mysql-backup
environment = production
```

- `log_dir`: Directory for storing log files
- `environment`: Current environment (e.g., production, development)

### Database Settings

```ini
[database]
host = localhost
port = 3306
user = backup_user
password = your_secure_password
database = production_db
```

- `host`: MySQL server hostname or IP address
- `port`: MySQL server port (default: 3306)
- `user`: MySQL username with backup privileges
- `password`: MySQL user password
- `database`: Database name to back up

### Backup Settings

```ini
[backup]
backup_dir = /var/backup/mysql
mysqldump_options = --single-transaction --routines --events --triggers --add-drop-table --extended-insert
daily_retention = 7
weekly_retention = 4
monthly_retention = 12
```

- `backup_dir`: Base directory for storing backup files
- `mysqldump_options`: Options to pass to the mysqldump command
- `daily_retention`: Number of daily backups to keep
- `weekly_retention`: Number of weekly backups to keep
- `monthly_retention`: Number of monthly backups to keep

### Notification Settings

```ini
[notification]
enabled = true
smtp_server = smtp.example.com
smtp_port = 587
use_tls = true
use_ssl = false
username = alerts@example.com
password = email_password
sender = mysql-backup@example.com
recipients = dba@example.com,admin@example.com
attach_logs = true
```

- `enabled`: Whether to enable email notifications
- `smtp_server`: SMTP server hostname
- `smtp_port`: SMTP server port
- `use_tls`: Whether to use STARTTLS (typically for port 587)
- `use_ssl`: Whether to use direct SSL connection (typically for port 465)
- `username`: SMTP username
- `password`: SMTP password
- `sender`: Email address to send from
- `recipients`: Comma-separated list of email recipients
- `attach_logs`: Whether to attach log files to failure notifications

## Command-Line Interface

The system provides a command-line interface with the following options:

```
usage: mysql_backup.py [-h] --config CONFIG [--backup-type {daily,weekly,monthly,all}] [--cleanup] [--daemon] [--test-notification]

MySQL Backup Tool

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to configuration file
  --backup-type {daily,weekly,monthly,all}
                        Run a specific backup type once and exit
  --cleanup             Run cleanup of old backups according to retention policy
  --daemon              Run as a daemon with scheduled backups
  --test-notification   Send a test notification email and exit
```

## Usage Examples

### Performing a Manual Backup

```bash
# Perform a daily backup
./mysql_backup.py --config mysql_backup.conf --backup-type daily

# Perform all backup types (daily, weekly, monthly)
./mysql_backup.py --config mysql_backup.conf --backup-type all
```

### Running in Daemon Mode

```bash
# Start the backup scheduler as a background process
nohup ./mysql_backup.py --config mysql_backup.conf --daemon > /dev/null 2>&1 &

# Or use screen/tmux for interactive sessions
screen -S mysql-backup
./mysql_backup.py --config mysql_backup.conf --daemon
# Press Ctrl+A+D to detach from screen
```

### Testing Email Configuration

```bash
# Send a test notification email
./mysql_backup.py --config mysql_backup.conf --test-notification
```

### Cleaning Up Old Backups

```bash
# Run the cleanup process manually
./mysql_backup.py --config mysql_backup.conf --cleanup
```

## Architecture

### Class Hierarchy

The system is designed using an object-oriented approach with the following key classes:

1. **BackupManager**: Main class orchestrating the backup process
2. **Logger**: Handles logging operations
3. **EmailNotifier**: Manages email notifications
4. **IntegrityVerifier**: Verifies backup integrity using checksums

Exception hierarchy:
- **BackupError**: Base exception class
  - **ConfigurationError**: Configuration-related errors
  - **ConnectionError**: Database connection errors
  - **BackupProcessError**: Backup process errors
  - **StorageError**: Storage-related errors
  - **IntegrityError**: Integrity verification errors
  - **NotificationError**: Email notification errors

### Process Flow

1. Parse command-line arguments and load configuration
2. Initialize Logger, EmailNotifier, and IntegrityVerifier
3. Execute requested operation (backup, cleanup, daemon mode, etc.)
4. For backups:
   - Create temporary directory
   - Execute mysqldump command
   - Calculate and store checksum
   - Move files to final location
   - Verify integrity
   - Send notifications
   - Log results
5. For daemon mode:
   - Schedule daily, weekly, and monthly backups
   - Schedule cleanup operations
   - Run continuously, executing tasks at scheduled times

## Error Handling

The system employs a comprehensive error handling strategy:

1. **Custom Exception Hierarchy**: Specialized exceptions for different error types
2. **Try-Except-Finally Blocks**: Proper resource cleanup and error handling
3. **Detailed Logging**: Full error details including stack traces
4. **Error Notifications**: Email alerts with error information and log attachments

## Scheduling

When running in daemon mode, the system schedules backups as follows:

- **Daily Backups**: Every day at midnight (00:00)
- **Weekly Backups**: Every Sunday at 1:00 AM
- **Monthly Backups**: First day of each month at 2:00 AM
- **Cleanup Operations**: Every day at 3:00 AM

## Security Considerations

The system employs several security best practices:

1. **Temporary Directories**: Uses temporary directories for initial backup files
2. **Atomic Operations**: Ensures backup files are only moved to final location when complete
3. **Checksums**: Verifies backup integrity to detect corruption or tampering
4. **Secure Connections**: Supports TLS/SSL for email notifications
5. **Credential Handling**: Properly handles database and SMTP credentials

## Backup Integrity Verification

Every backup includes a SHA-256 checksum file to verify integrity:

1. During backup, a SHA-256 hash is calculated for the backup file
2. The hash is stored in a separate `.sha256` file
3. After moving files to the final location, integrity is verified
4. During restoration (not included), checksums can be verified again

## Email Notifications

The system sends detailed email notifications for backup events:

- **Success Notifications**: Include backup size, duration, path, and checksum
- **Failure Notifications**: Include error details, stack traces, and optionally attached log files
- **Test Notifications**: Can be triggered manually to verify email configuration

## Logging

The system maintains detailed logs of all operations:

1. Logs are stored in the configured log directory
2. Log files are named with the current date (e.g., `mysql_backup_20250410.log`)
3. Log entries include timestamp, log level, and detailed message
4. Log files can be attached to failure notifications

## Production Deployment

### Systemd Service

For production deployment on Linux systems with systemd, create a service file:

```ini
[Unit]
Description=MySQL Automated Backup System
After=network.target mysql.service

[Service]
Type=simple
User=backup
Group=backup
ExecStart=/path/to/mysql_backup.py --config /etc/mysql-backup/mysql_backup.conf --daemon
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Install and enable the service:

```bash
sudo cp mysql-backup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mysql-backup.service
sudo systemctl start mysql-backup.service
```

### Docker Deployment

A sample Dockerfile:

```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y default-mysql-client && \
    pip install schedule

WORKDIR /app

COPY mysql_backup.py /app/
COPY mysql_backup.conf /app/

CMD ["python", "mysql_backup.py", "--config", "mysql_backup.conf", "--daemon"]
```

Build and run the container:

```bash
docker build -t mysql-backup .
docker run -d \
  --name mysql-backup \
  -v /path/to/backups:/var/backup/mysql \
  -v /path/to/logs:/var/log/mysql-backup \
  mysql-backup
```

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   - Ensure the script has executable permissions
   - Verify the user has write access to backup and log directories

2. **Database Connection Failed**:
   - Check database credentials and connection settings
   - Ensure the MySQL user has sufficient privileges

3. **Email Notifications Not Working**:
   - Verify SMTP server settings
   - Check if the server requires authentication
   - Test with `--test-notification` option

4. **Backup Process Failed**:
   - Check mysqldump is installed and in PATH
   - Verify mysqldump options are compatible with your MySQL version
   - Check disk space

### Diagnostic Steps

1. Run with specific backup type to test functionality:
   ```bash
   ./mysql_backup.py --config mysql_backup.conf --backup-type daily
   ```

2. Check log files for detailed error information:
   ```bash
   tail -n 50 /var/log/mysql-backup/mysql_backup_YYYYMMDD.log
   ```

3. Test email notifications:
   ```bash
   ./mysql_backup.py --config mysql_backup.conf --test-notification
   ```

## Frequently Asked Questions

### Q: How do I add additional databases to back up?
A: Currently, the system backs up one database per configuration. For multiple databases, you can create separate configuration files and run multiple instances of the script.

### Q: Can I customize the backup schedule?
A: Yes, you can modify the scheduling code in the `start_scheduler` method of the `BackupManager` class. The system uses the `schedule` library, which supports various scheduling patterns.

### Q: How do I restore a backup?
A: To restore a backup, use the standard MySQL command:
```bash
gunzip < /path/to/backup.sql.gz | mysql -u username -p database_name
```

### Q: Does this support incremental backups?
A: No, this system creates full backups. For incremental backups, consider technologies like binary log backups.

### Q: How can I extend the system to back up to cloud storage?
A: You could extend the `BackupManager` class to upload backups to cloud storage (AWS S3, Google Cloud Storage, etc.) after the local backup is complete and verified.