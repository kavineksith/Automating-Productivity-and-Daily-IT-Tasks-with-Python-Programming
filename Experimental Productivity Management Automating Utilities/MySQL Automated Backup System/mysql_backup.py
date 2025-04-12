#!/usr/bin/env python3
"""
MySQL Automated Backup System
A production-ready solution for scheduled database backups with integrity verification,
email notifications, and comprehensive logging.
"""

import os
import sys
import time
import hashlib
import smtplib
import logging
import argparse
import configparser
import subprocess
import traceback
import calendar
import socket
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import tempfile
import shutil
import threading
import schedule


class BackupError(Exception):
    """Base exception class for all backup related errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConfigurationError(BackupError):
    """Raised when there's an error in the configuration."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConnectionError(BackupError):
    """Raised when there's an error connecting to the database."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BackupProcessError(BackupError):
    """Raised when the backup process fails."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class StorageError(BackupError):
    """Raised when there's an error with the backup storage."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class IntegrityError(BackupError):
    """Raised when the backup integrity check fails."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotificationError(BackupError):
    """Raised when there's an error sending notifications."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Logger:
    """Handles all logging operations."""
    
    def __init__(self, log_dir: str, log_level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory where log files will be stored
            log_level: Logging level
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("mysql_backup")
        self.logger.setLevel(log_level)
        
        # Create log file handler with rotation
        self.current_log_file = self.log_dir / f"mysql_backup_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(self.current_log_file)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_current_log_file(self) -> str:
        """Return the path to the current log file."""
        return str(self.current_log_file)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Log exception with stack trace."""
        self.logger.exception(message)


class EmailNotifier:
    """Handles email notifications with optional file attachments."""
    
    def __init__(self, config: Dict[str, str], logger: Logger = None):
        """
        Initialize the email notifier.
        
        Args:
            config: Email configuration including server, port, credentials, etc.
            logger: Logger instance for logging notification events
        """
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = int(config.get('smtp_port', 587))
        self.use_tls = config.get('use_tls', 'true').lower() == 'true'
        self.use_ssl = config.get('use_ssl', 'false').lower() == 'true'
        self.username = config.get('username')
        self.password = config.get('password')
        self.sender = config.get('sender')
        self.recipients = config.get('recipients', '').split(',')
        self.hostname = socket.gethostname()
        self.logger = logger
        self.attach_logs = config.get('attach_logs', 'false').lower() == 'true'
    
    def send_notification(self, subject: str, message: str, attachments: List[str] = None) -> None:
        """
        Send an email notification with optional attachments.
        
        Args:
            subject: Email subject
            message: Email body
            attachments: List of file paths to attach
            
        Raises:
            NotificationError: If notification cannot be sent
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)
            msg['Subject'] = f"[MySQL Backup] {subject} - {self.hostname}"
            
            # Add timestamp and hostname to the message
            full_message = f"""
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Host: {self.hostname}
            
            {message}
            """
            
            msg.attach(MIMEText(full_message))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        # Encode file in ASCII characters to send by email
                        encoders.encode_base64(part)
                        
                        # Add header as key/value pair to attachment part
                        filename = os.path.basename(file_path)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename}',
                        )
                        
                        msg.attach(part)
                        if self.logger:
                            self.logger.info(f"Attached file {filename} to notification")
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Failed to attach file {file_path}: {str(e)}")
            
            # Create the appropriate SMTP connection based on settings
            if self.use_ssl:
                # Use SSL context for direct SSL connection
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # Use standard connection with optional TLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    
                    server.send_message(msg)
            
            if self.logger:
                self.logger.info(f"Email notification sent: {subject}")
        
        except Exception as e:
            error_msg = f"Failed to send notification: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            raise NotificationError(error_msg)

    def send_backup_notification(self, backup_type: str, backup_path: str = None, 
                               duration: float = None, size_mb: float = None, 
                               checksum: str = None, success: bool = True,
                               error_message: str = None) -> None:
        """
        Send a specialized backup notification.
        
        Args:
            backup_type: Type of backup (daily, weekly, monthly)
            backup_path: Path to the backup file
            duration: Backup duration in seconds
            size_mb: Backup size in MB
            checksum: Backup file checksum
            success: Whether the backup was successful
            error_message: Error message if backup failed
        """
        if success:
            subject = f"{backup_type.capitalize()} Backup Successful"
            message = (
                f"{backup_type.capitalize()} backup completed successfully.\n"
                f"Duration: {duration:.2f} seconds\n"
                f"Size: {size_mb:.2f} MB\n"
                f"File: {backup_path}\n"
                f"Checksum: {checksum}"
            )
        else:
            subject = f"{backup_type.capitalize()} Backup Failed"
            message = f"Error: {error_message}\n\n"
            if backup_path:
                message += f"Attempted backup file: {backup_path}\n"
        
        attachments = []
        
        # Attach log file if requested and logger is available
        if self.attach_logs and self.logger and error_message:
            log_file = self.logger.get_current_log_file()
            if log_file and os.path.exists(log_file):
                attachments.append(log_file)
        
        self.send_notification(subject, message, attachments)


class IntegrityVerifier:
    """Handles backup integrity verification using checksums."""
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """
        Calculate SHA-256 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Hexadecimal digest of the file's SHA-256 hash
            
        Raises:
            IntegrityError: If the file cannot be read
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise IntegrityError(f"Failed to calculate checksum for {file_path}: {str(e)}")
    
    @staticmethod
    def save_checksum(file_path: str, checksum: str) -> None:
        """
        Save checksum to a file.
        
        Args:
            file_path: Path to the backup file
            checksum: Calculated checksum
            
        Raises:
            IntegrityError: If the checksum cannot be saved
        """
        try:
            checksum_file = f"{file_path}.sha256"
            with open(checksum_file, "w") as f:
                f.write(checksum)
        except Exception as e:
            raise IntegrityError(f"Failed to save checksum for {file_path}: {str(e)}")
    
    @staticmethod
    def verify_checksum(file_path: str) -> Tuple[bool, str]:
        """
        Verify file integrity by comparing stored and calculated checksums.
        
        Args:
            file_path: Path to the backup file
            
        Returns:
            tuple: (is_valid, message)
            
        Raises:
            IntegrityError: If the verification process fails
        """
        try:
            checksum_file = f"{file_path}.sha256"
            
            if not os.path.exists(checksum_file):
                return False, "Checksum file not found"
            
            with open(checksum_file, "r") as f:
                stored_checksum = f.read().strip()
            
            calculated_checksum = IntegrityVerifier.calculate_checksum(file_path)
            
            if stored_checksum == calculated_checksum:
                return True, "Checksum verification passed"
            else:
                return False, "Checksum verification failed"
                
        except Exception as e:
            raise IntegrityError(f"Failed to verify checksum for {file_path}: {str(e)}")


class BackupManager:
    """Main class for database backup operations."""
    
    def __init__(self, config_path: str):
        """
        Initialize the backup manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = Logger(self.config['general']['log_dir'])
        
        # Initialize email notifier if enabled
        self.email_notifier = None
        if self.config['notification'].get('enabled', 'false').lower() == 'true':
            self.email_notifier = EmailNotifier(self.config['notification'], self.logger)
        
        # Initialize integrity verifier
        self.integrity_verifier = IntegrityVerifier()
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load and validate configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            dict: Configuration dictionary
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            if not os.path.exists(config_path):
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Validate required sections
            required_sections = ['general', 'database', 'backup', 'notification']
            for section in required_sections:
                if section not in config:
                    raise ConfigurationError(f"Missing required section in config: {section}")
            
            # Convert to dictionary for easier access
            config_dict = {section: dict(config[section]) for section in config.sections()}
            
            # Validate required paths
            backup_dir = Path(config_dict['backup']['backup_dir'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            log_dir = Path(config_dict['general']['log_dir'])
            log_dir.mkdir(parents=True, exist_ok=True)
            
            return config_dict
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            else:
                raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def _get_backup_filename(self, backup_type: str) -> str:
        """
        Generate backup filename based on type and current date.
        
        Args:
            backup_type: Type of backup (daily, weekly, monthly)
            
        Returns:
            str: Backup filename
        """
        db_name = self.config['database']['database']
        now = datetime.now()
        
        if backup_type == 'daily':
            date_str = now.strftime('%Y%m%d')
            return f"{db_name}_daily_{date_str}.sql.gz"
        elif backup_type == 'weekly':
            # Get the week number (1-52)
            week_num = now.isocalendar()[1]
            return f"{db_name}_weekly_{now.year}_week{week_num:02d}.sql.gz"
        elif backup_type == 'monthly':
            return f"{db_name}_monthly_{now.year}_{now.month:02d}.sql.gz"
        else:
            return f"{db_name}_ad_hoc_{now.strftime('%Y%m%d_%H%M%S')}.sql.gz"
    
    def perform_backup(self, backup_type: str) -> Optional[str]:
        """
        Perform database backup.
        
        Args:
            backup_type: Type of backup (daily, weekly, monthly)
            
        Returns:
            str: Path to the backup file if successful, None otherwise
            
        Raises:
            Various exceptions depending on what goes wrong
        """
        start_time = time.time()
        self.logger.info(f"Starting {backup_type} backup...")
        
        # Create backup directory if it doesn't exist
        backup_dir = Path(self.config['backup']['backup_dir']) / backup_type
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename
        backup_filename = self._get_backup_filename(backup_type)
        backup_path = backup_dir / backup_filename
        
        # Create temporary directory for backup
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_backup_path = Path(temp_dir) / backup_filename
            
            try:
                # Build mysqldump command
                cmd = [
                    "mysqldump",
                    f"--host={self.config['database']['host']}",
                    f"--port={self.config['database'].get('port', '3306')}",
                    f"--user={self.config['database']['user']}",
                ]
                
                # Add password if provided
                if 'password' in self.config['database']:
                    cmd.append(f"--password={self.config['database']['password']}")
                
                # Add database name
                cmd.append(self.config['database']['database'])
                
                # Add optional parameters
                options = self.config['backup'].get('mysqldump_options', '')
                if options:
                    cmd.extend(options.split())
                
                # Redirect output to gzip
                cmd.extend(["|", "gzip", ">", str(temp_backup_path)])
                
                # Execute the command
                self.logger.info(f"Executing backup command: {' '.join(cmd)}")
                process = subprocess.run(
                    " ".join(cmd),
                    shell=True,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                if process.returncode != 0:
                    raise BackupProcessError(f"Backup process failed: {process.stderr}")
                
                # Calculate and save checksum
                checksum = self.integrity_verifier.calculate_checksum(str(temp_backup_path))
                self.integrity_verifier.save_checksum(str(temp_backup_path), checksum)
                
                # Move backup and checksum to final location
                shutil.move(str(temp_backup_path), str(backup_path))
                shutil.move(f"{str(temp_backup_path)}.sha256", f"{str(backup_path)}.sha256")
                
                # Verify the backup
                is_valid, message = self.integrity_verifier.verify_checksum(str(backup_path))
                if not is_valid:
                    raise IntegrityError(f"Backup integrity check failed: {message}")
                
                # Calculate backup size
                backup_size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                
                # Log completion
                duration = time.time() - start_time
                self.logger.info(
                    f"{backup_type.capitalize()} backup completed successfully in {duration:.2f} seconds. "
                    f"Size: {backup_size_mb:.2f} MB. Path: {backup_path}"
                )
                
                # Send notification if enabled
                if self.email_notifier:
                    self.email_notifier.send_backup_notification(
                        backup_type=backup_type,
                        backup_path=str(backup_path),
                        duration=duration,
                        size_mb=backup_size_mb,
                        checksum=checksum,
                        success=True
                    )
                
                return str(backup_path)
                
            except Exception as e:
                self.logger.exception(f"Backup failed: {str(e)}")
                
                # Send failure notification if enabled
                if self.email_notifier:
                    self.email_notifier.send_backup_notification(
                        backup_type=backup_type,
                        backup_path=str(backup_path) if 'backup_path' in locals() else None,
                        success=False,
                        error_message=f"{str(e)}\n\nStack trace:\n{traceback.format_exc()}"
                    )
                
                # Re-raise the exception
                raise
    
    def cleanup_old_backups(self) -> None:
        """
        Clean up old backups according to retention policy.
        """
        try:
            self.logger.info("Starting backup cleanup...")
            
            retention = {
                'daily': int(self.config['backup'].get('daily_retention', 7)),
                'weekly': int(self.config['backup'].get('weekly_retention', 4)),
                'monthly': int(self.config['backup'].get('monthly_retention', 12))
            }
            
            for backup_type, days in retention.items():
                backup_dir = Path(self.config['backup']['backup_dir']) / backup_type
                if not backup_dir.exists():
                    continue
                
                self.logger.info(f"Cleaning up {backup_type} backups (retention: {days} units)...")
                
                # Get all backup files
                backup_files = list(backup_dir.glob('*.sql.gz'))
                
                # Sort by modification time (oldest first)
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Keep only the newest 'days' backups
                files_to_delete = backup_files[:-days] if len(backup_files) > days else []
                
                for file_path in files_to_delete:
                    try:
                        # Also remove the checksum file if it exists
                        checksum_path = Path(f"{file_path}.sha256")
                        if checksum_path.exists():
                            checksum_path.unlink()
                        
                        # Remove the backup file
                        file_path.unlink()
                        self.logger.info(f"Deleted old backup: {file_path}")
                    
                    except Exception as e:
                        self.logger.error(f"Failed to delete old backup {file_path}: {str(e)}")
            
            self.logger.info("Backup cleanup completed.")
            
        except Exception as e:
            self.logger.exception(f"Backup cleanup failed: {str(e)}")
            
            # Send failure notification if enabled
            if self.email_notifier:
                self.email_notifier.send_backup_notification(
                    backup_type="cleanup",
                    success=False,
                    error_message=f"{str(e)}\n\nStack trace:\n{traceback.format_exc()}"
                )
    
    def run_daily_backup(self) -> None:
        """Execute daily backup."""
        try:
            self.perform_backup('daily')
            self.cleanup_old_backups()  # Run cleanup after successful backup
        except Exception as e:
            self.logger.error(f"Daily backup failed: {str(e)}")
    
    def run_weekly_backup(self) -> None:
        """Execute weekly backup."""
        try:
            self.perform_backup('weekly')
        except Exception as e:
            self.logger.error(f"Weekly backup failed: {str(e)}")
    
    def run_monthly_backup(self) -> None:
        """Execute monthly backup."""
        try:
            self.perform_backup('monthly')
        except Exception as e:
            self.logger.error(f"Monthly backup failed: {str(e)}")
    
    def start_scheduler(self) -> None:
        """Start the backup scheduler."""
        self.logger.info("Starting backup scheduler...")
        
        # Schedule daily backups at midnight
        schedule.every().day.at("00:00").do(self.run_daily_backup)
        
        # Schedule weekly backups on Sunday at 01:00
        schedule.every().sunday.at("01:00").do(self.run_weekly_backup)
        
        # Schedule monthly backups on the 1st day of each month at 02:00
        schedule.every().month.at("02:00").do(self.run_monthly_backup)
        
        # Schedule cleanup to run every day at 03:00
        schedule.every().day.at("03:00").do(self.cleanup_old_backups)
        
        self.logger.info("Backup scheduler started. Running continuously...")
        
        try:
            # Run the scheduler in a loop
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Backup scheduler stopped by user.")
        except Exception as e:
            self.logger.critical(f"Scheduler crashed: {str(e)}")
            if self.email_notifier:
                self.email_notifier.send_backup_notification(
                    backup_type="scheduler",
                    success=False,
                    error_message=f"Scheduler crashed: {str(e)}\n\nStack trace:\n{traceback.format_exc()}"
                )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="MySQL Backup Tool")
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--backup-type",
        choices=["daily", "weekly", "monthly", "all"],
        help="Run a specific backup type once and exit"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Run cleanup of old backups according to retention policy"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as a daemon with scheduled backups"
    )
    parser.add_argument(
        "--test-notification",
        action="store_true",
        help="Send a test notification email and exit"
    )
    
    args = parser.parse_args()
    
    try:
        backup_manager = BackupManager(args.config)
        
        if args.test_notification:
            if backup_manager.email_notifier:
                backup_manager.logger.info("Sending test notification...")
                backup_manager.email_notifier.send_notification(
                    "Test Notification",
                    "This is a test notification from the MySQL Backup System.",
                    [backup_manager.logger.get_current_log_file()]
                )
                backup_manager.logger.info("Test notification sent.")
            else:
                backup_manager.logger.error("Email notifications not enabled in config.")
                return 1
        elif args.backup_type:
            if args.backup_type == "all":
                backup_manager.perform_backup("daily")
                backup_manager.perform_backup("weekly")
                backup_manager.perform_backup("monthly")
            else:
                backup_manager.perform_backup(args.backup_type)
        elif args.cleanup:
            backup_manager.cleanup_old_backups()
        elif args.daemon:
            backup_manager.start_scheduler()
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())