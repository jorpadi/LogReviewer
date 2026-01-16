from pathlib import Path
import os
from datetime import datetime
import re
from utils.log_handler import logger

def is_datetime_in_range(current_datetime, start_datetime, end_datetime):
    return start_datetime <= current_datetime <= end_datetime

def check_logs_period(file_path, dates, log_type: str):

    initial_date, ending_date = dates
    logs_file_path = []

    logger.info("check_logs_period",f"Checking logs Between {str(initial_date.date())} and {str(ending_date.date())} in {file_path}")

    if log_type == 'engine':
        date_pattern = r"(\d{4}-\d{2}-\d{2})"
        format_pattern = '%Y-%m-%d'
    elif log_type == 'webservice':
        date_pattern = r"(\d{2}-\d{2}-\d{4})"
        format_pattern = '%d-%m-%Y'
    else:
        raise ValueError(f"Unsupported log type: {log_type}")

    for entry_name in os.listdir(file_path):
        full_path = Path(file_path) / entry_name

        if not full_path.is_file():
            continue

        match = re.search(date_pattern, entry_name)
        if not match:
            continue

        try:
            file_time = datetime.strptime(match.group(1), format_pattern)
        except ValueError:
            continue

        if is_datetime_in_range(file_time, initial_date, ending_date):
            logs_file_path.append(full_path)

    return logs_file_path