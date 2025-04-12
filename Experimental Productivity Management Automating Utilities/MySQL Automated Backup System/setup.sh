#!/bin/bash
# Sample scripts for common MySQL Automated Backup operations

# ============================================================================
# 1. Setup script for a new installation
# ============================================================================

setup_mysql_backup() {
    echo "Setting up MySQL Automated Backup System..."
    
    # Create directories
    sudo mkdir -p /var/backup/mysql/{daily,weekly,monthly}
    sudo mkdir -p /var/log/mysql-backup
    sudo mkdir -p /etc/mysql-backup
    
    # Set proper permissions
    sudo chown -R ${USER}:${USER} /var/backup/mysql
    sudo chown -R ${USER}:${USER} /var/log/mysql-backup
    
    # Install required Python package
    pip install schedule
    
    # Copy files to appropriate locations
    cp mysql_backup.py /usr/local/bin/
    chmod +x /usr/local/bin/mysql_backup.py
    
    # Create config file from template
    cp mysql_backup.conf.template /etc/mysql-backup/mysql_backup.conf
    
    echo "Please edit /etc/mysql-backup/mysql_backup.conf with your database credentials"
    echo "Setup complete!"
}

# ============================================================================
# 2. Create a systemd service for continuous operation
# ============================================================================

install_systemd_service() {
    echo "Installing MySQL Backup systemd service..."
    
    # Create service file
    cat > mysql-backup.service << EOF
[Unit]
Description=MySQL Automated Backup System
After=network.target mysql.service

[Service]
Type=simple
User=${USER}
Group=${USER}
ExecStart=/usr/local/bin/mysql_backup.py --config /etc/mysql-backup/mysql_backup.conf --daemon
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    # Install service
    sudo cp mysql-backup.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable mysql-backup.service
    sudo systemctl start mysql-backup.service
    
    echo "Service installed and started!"
    echo "Check status with: sudo systemctl status mysql-backup.service"
}

# ============================================================================
# 3. Verify backup integrity
# ============================================================================

verify_backup_integrity() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: verify_backup_integrity path/to/backup.sql.gz"
        return 1
    fi
    
    backup_file=$1
    checksum_file="${backup_file}.sha256"
    
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file"
        return 1
    fi
    
    if [ ! -f "$checksum_file" ]; then
        echo "Error: Checksum file not found: $checksum_file"
        return 1
    fi
    
    stored_checksum=$(cat "$checksum_file")
    calculated_checksum=$(sha256sum "$backup_file" | awk '{print $1}')
    
    if [ "$stored_checksum" = "$calculated_checksum" ]; then
        echo "✓ Integrity verification passed for $backup_file"
        return 0
    else
        echo "✗ Integrity verification FAILED for $backup_file"
        echo "  Stored checksum:     $stored_checksum"
        echo "  Calculated checksum: $calculated_checksum"
        return 1
    fi
}

# ============================================================================
# 4. Restore a backup
# ============================================================================

restore_backup() {
    if [ "$#" -lt 3 ]; then
        echo "Usage: restore_backup backup_file host db_name [user] [password]"
        echo "Example: restore_backup /var/backup/mysql/daily/db_daily_20250410.sql.gz localhost mydb"
        return 1
    fi
    
    backup_file=$1
    host=$2
    db_name=$3
    user=${4:-root}
    password=$5
    
    # Verify backup integrity
    verify_backup_integrity "$backup_file"
    if [ $? -ne 0 ]; then
        echo "Backup integrity check failed! Aborting restore."
        return 1
    fi
    
    echo "Warning: This will OVERWRITE the database $db_name on $host"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Restore aborted."
        return 1
    fi
    
    # Construct MySQL command
    if [ -z "$password" ]; then
        mysql_cmd="mysql -h $host -u $user $db_name"
    else
        mysql_cmd="mysql -h $host -u $user -p'$password' $db_name"
    fi
    
    # Restore the backup
    echo "Restoring backup to $db_name on $host..."
    gunzip < "$backup_file" | eval $mysql_cmd
    
    if [ $? -eq 0 ]; then
        echo "Restore completed successfully!"
    else
        echo "Error during restore. Please check MySQL error logs."
    fi
}

# ============================================================================
# 5. Run regular health check on backups 
# ============================================================================

backup_health_check() {
    backup_dir=${1:-/var/backup/mysql}
    log_file=${2:-/var/log/mysql-backup/health_check.log}
    
    echo "$(date): Running backup health check..." | tee -a $log_file
    
    # Check for recent daily backups
    latest_daily=$(find $backup_dir/daily -name "*.sql.gz" -type f -mtime -1 | wc -l)
    if [ $latest_daily -eq 0 ]; then
        echo "WARNING: No daily backups found from the last 24 hours!" | tee -a $log_file
    else
        echo "✓ Found $latest_daily daily backups from the last 24 hours" | tee -a $log_file
    fi
    
    # Check backup sizes
    echo "Backup sizes:" | tee -a $log_file
    echo "- Daily backups:" | tee -a $log_file
    du -sh $backup_dir/daily | tee -a $log_file
    echo "- Weekly backups:" | tee -a $log_file
    du -sh $backup_dir/weekly | tee -a $log_file
    echo "- Monthly backups:" | tee -a $log_file
    du -sh $backup_dir/monthly | tee -a $log_file
    
    # Check integrity of latest backups
    echo "Checking integrity of latest backups:" | tee -a $log_file
    
    # Find latest backup of each type
    latest_daily_backup=$(find $backup_dir/daily -name "*.sql.gz" -type f -print0 | xargs -0 ls -t | head -n1)
    latest_weekly_backup=$(find $backup_dir/weekly -name "*.sql.gz" -type f -print0 | xargs -0 ls -t | head -n1)
    latest_monthly_backup=$(find $backup_dir/monthly -name "*.sql.gz" -type f -print0 | xargs -0 ls -t | head -n1)
    
    # Check integrity
    [ -n "$latest_daily_backup" ] && verify_backup_integrity "$latest_daily_backup" | tee -a $log_file
    [ -n "$latest_weekly_backup" ] && verify_backup_integrity "$latest_weekly_backup" | tee -a $log_file
    [ -n "$latest_monthly_backup" ] && verify_backup_integrity "$latest_monthly_backup" | tee -a $log_file
    
    echo "Health check completed at $(date)" | tee -a $log_file
}

# ============================================================================
# 6. Example cron job to run health checks
# ============================================================================

install_health_check_cron() {
    echo "Installing daily backup health check cron job..."
    
    # Create health check script
    cat > /tmp/backup_health_check.sh << 'EOF'
#!/bin/bash
backup_dir=/var/backup/mysql
log_file=/var/log/mysql-backup/health_check.log

echo "$(date): Running backup health check..." >> $log_file

# Check for recent daily backups
latest_daily=$(find $backup_dir/daily -name "*.sql.gz" -type f -mtime -1 | wc -l)
if [ $latest_daily -eq 0 ]; then
    echo "WARNING: No daily backups found from the last 24 hours!" >> $log_file
    echo "WARNING: No daily backups found from the last 24 hours!" | mail -s "MySQL Backup Health Check ALERT" admin@example.com
else
    echo "✓ Found $latest_daily daily backups from the last 24 hours" >> $log_file
fi

# Check backup sizes
find $backup_dir -name "*.sql.gz" -type f -mtime -7 -exec ls -lh {} \; >> $log_file

# Check integrity of latest backups
latest_daily_backup=$(find $backup_dir/daily -name "*.sql.gz" -type f -print0 | xargs -0 ls -t | head -n1)
if [ -n "$latest_daily_backup" ]; then
    stored_checksum=$(cat "${latest_daily_backup}.sha256")
    calculated_checksum=$(sha256sum "$latest_daily_backup" | awk '{print $1}')
    
    if [ "$stored_checksum" = "$calculated_checksum" ]; then
        echo "✓ Latest daily backup integrity verified" >> $log_file
    else
        echo "✗ Latest daily backup integrity check FAILED!" >> $log_file
        echo "✗ Latest daily backup integrity check FAILED!" | mail -s "MySQL Backup Health Check ALERT" admin@example.com
    fi
fi
EOF
    
    chmod +x /tmp/backup_health_check.sh
    sudo mv /tmp/backup_health_check.sh /usr/local/bin/
    
    # Add cron job
    (crontab -l 2>/dev/null; echo "0 9 * * * /usr/local/bin/backup_health_check.sh") | crontab -
    
    echo "Health check cron job installed! Will run daily at 9:00 AM."
}

# ============================================================================
# Usage examples
# ============================================================================

# Uncomment the function you want to run:
# setup_mysql_backup
# install_systemd_service
# verify_backup_integrity "/var/backup/mysql/daily/mydb_daily_20250410.sql.gz"
# restore_backup "/var/backup/mysql/daily/mydb_daily_20250410.sql.gz" "localhost" "mydb" "root" "password"
# backup_health_check
# install_health_check_cron

echo "MySQL Backup Sample Scripts"
echo "Please edit this file and uncomment the function you want to run"