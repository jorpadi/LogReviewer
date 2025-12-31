from common_checkers import checkers
from datetime import datetime
import re
from dataclasses import dataclass
import os

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
        common_checkers = checkers.checkers()
        findings = log_parser(full_log_path, common_checkers)
        all_findings.extend(findings)

    return all_findings