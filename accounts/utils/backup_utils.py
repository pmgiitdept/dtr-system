import os
import subprocess
import datetime
from django.conf import settings

def run_backup():
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.json")

    # Run dumpdata and capture output
    result = subprocess.run(
        ["python", "manage.py", "dumpdata", "--indent", "2"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Backup failed: {result.stderr}")

    # Write output to file
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    return backup_file

def run_restore(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Backup file not found: {file_path}")

    result = subprocess.run(
        ["python", "manage.py", "loaddata", file_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Restore failed: {result.stderr}")

    return True