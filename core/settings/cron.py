
CRONJOBS = [
    ('00 21 * * 1', 'main.cron.setMagicNumber'),
    ('00 22 * * 1', 'main.cron.DBBackup'),
    ('00 23 * * 1', 'main.cron.cleanupOldLogs'),
    ('00 00 * * 2', 'main.cron.uploadDBBackupToGoogleDrive'),
    ('00 02 * * 2', 'main.cron.uploadDocumentsToGoogleDrive'),
]
