from pathlib import Path
import os
from datetime import datetime
import re

def is_datetime_in_range(current_datetime, start_datetime, end_datetime):
    return start_datetime <= current_datetime <= end_datetime

def check_logs_period(file_path, dates, log_type : str):
    logs_file_path = []
    initial_date = dates[0]
    ending_date = dates[1]
    print(f"Searching logs between {initial_date} and {ending_date}...")

    for entry_name in os.listdir(file_path):
        date_match = re.search(r".((\d+).(\d+).(\d+))", entry_name)

        if date_match:
            datetime_str = date_match.group(1)
            # Define the format pattern matching the extracted string
            if log_type == 'engine':
                format_pattern = '%Y-%m-%d' # -> engine, lsa, etl, etc
            if log_type == 'webservice':
                format_pattern = '%d-%m-%Y' # -> Webservice
            # Convert the string to a datetime object
            file_time = datetime.strptime(datetime_str, format_pattern)
            log_in_data_range = is_datetime_in_range(file_time,initial_date,ending_date)
            if log_in_data_range:
                logs_file_path.append(entry_name)
        else:
            print("No matching date/time pattern found in filename.")

    return logs_file_path