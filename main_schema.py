import pandas as pd 
from pathlib import Path
import re
import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

current_main_folder = Path(r"C:\Users\jpalma\Documents\LogsDataset\CNA3")

engine_files_path =  current_main_folder / "Engine"
webservice_file_path = current_main_folder / "Webservice"

start_analysis_date = datetime(2025,12,20)
end_analysis_date = datetime(2025,12,21)
dates = [start_analysis_date, end_analysis_date]
parameters = [dates]

@dataclass
class Finding:
    checker: str
    severity: str
    timestamp: datetime
    module: str
    message: str

@dataclass
class LogEntry:
    datetime: datetime
    module: str
    level: str
    message: str

LOG_ENGINE_PATTERN = re.compile(
    r'^\['
    r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})'
    r'\]\['
    r'(?P<module>[^\]]+)'
    r'\]\['
    r'(?P<level>[^\]]+)'
    r'\]\s*'
    r'(?P<message>.*)$'
)

class BaseChecker:
    name = "base"

    def process(self, entry):
        """
        Receives a LogEntry
        Returns list[Finding]
        """
        return []

class ErrorChecker(BaseChecker):
    name = "error_checker"

    def process(self, entry):
        if entry.level == "ERROR":
            return [Finding(
                checker=self.name,
                severity="HIGH",
                timestamp=entry.datetime,
                module=entry.module,
                message=entry.message)]
        return []

class WarningChecker(BaseChecker):
    name = "warning_checker"

    def process(self, entry):
        if entry.level == "WARN" or entry.level == "WARNING":
            return [Finding(
                checker=self.name,
                severity="HIGH",
                timestamp=entry.datetime,
                module=entry.module,
                message=entry.message)]
        return []

class UptimeChecker(BaseChecker):
    name = "uptime_checker"

    def __init__(self, threshold_sec):
        self.threshold = threshold_sec
        self.prev_timestamp = None

    def process(self, entry):
        findings = []

        if self.prev_timestamp:
            diff = (entry.datetime - self.prev_timestamp).total_seconds()
            if diff > self.threshold:
                findings.append(Finding(
                    checker=self.name,
                    severity="HIGH",
                    timestamp=entry.datetime,
                    module=entry.module,
                    message=f"Uptime gap od {diff:.1f}s"))
        self.prev_timestamp = entry.datetime
        return findings

common_checkers = [
    ErrorChecker(),
    WarningChecker(),
    UptimeChecker(threshold_sec=300),
]

def is_datetime_in_range(current_datetime, start_datetime, end_datetime):
    return start_datetime <= current_datetime <= end_datetime

def check_logs_period(file_path, dates):
    logs_file_path = []
    initial_date = dates[0]
    ending_date = dates[1]
    print(f"Searching logs between {initial_date} and {ending_date}...")

    for entry_name in os.listdir(file_path):
        date_match = re.search(r".((\d+).(\d+).(\d+))", entry_name)

        if date_match:
            datetime_str = date_match.group(1)
            # Define the format pattern matching the extracted string
            format_pattern = '%Y-%m-%d' # -> engine, lsa, etl, etc
            #format_pattern = '%d-%m-%Y' # -> Webservice
            # Convert the string to a datetime object
            file_time = datetime.strptime(datetime_str, format_pattern)
            log_in_data_range = is_datetime_in_range(file_time,initial_date,ending_date)
            if log_in_data_range:
                logs_file_path.append(entry_name)
        else:
            print("No matching date/time pattern found in filename.")

    return logs_file_path

def log_line_generator(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")

def parse_log_line(line: str) -> LogEntry:
    match = LOG_ENGINE_PATTERN.match(line)
    if not match:
        return

    return LogEntry(
        datetime = datetime.strptime(match.group("datetime"),"%Y-%m-%d %H:%M:%S.%f"),
        module = match.group("module").strip(),
        level = match.group("level").strip(),
        message = match.group("message").strip(),
    )


def log_parser(log_path, checkers):
    findings = []

    for log_line in log_line_generator(log_path):
        entry = parse_log_line(log_line)
        if not entry:
            continue

        for checker in checkers:
            checker_findings = checker.process(entry)
            if checker_findings:
                findings.extend(checker_findings)

    return findings

def log_file_iterator(file_path, logs_to_work, parameters):

    all_findings = []

    for log_file in range(len(logs_to_work)):
        full_log_path = os.path.join(file_path,logs_to_work[log_file])
        print(f"Processing {full_log_path}")
        findings = log_parser(full_log_path, common_checkers)
        all_findings.extend(findings)

    return all_findings

def main():
    engine_files_to_check = check_logs_period(engine_files_path, dates)
    print(f"Total logs found: {len(engine_files_to_check)}")

    findings = log_file_iterator(engine_files_path, engine_files_to_check, parameters)

    print(f"Total findings: {len(findings)}")
    for f in findings:
        print(f"[{f.severity}] {f.checker} @ {f.timestamp} → {f.message}")

if __name__ == "__main__":
    main()