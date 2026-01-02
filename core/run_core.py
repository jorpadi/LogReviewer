from common_checkers import checkers
from engine_checkers.main_checkers import engine_checkers_main
from datetime import datetime
import re
from dataclasses import dataclass
import os
from typing import Optional

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

WEBSERVICE_PATTERN = re.compile(
    r'^(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+'
    r'(?P<pid>\d+)\s+'
    r'\[(?P<thread>[^\]]+)\]\s+'
    r'(?P<level>TRACE|DEBUG|INFO|WARN|ERROR)\s+'
    r'(?P<module>[^-]+)\s+-\s+'
    r'(?P<message>.*)$'
)
def log_line_generator(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")

def parse_engine_log(line: str) -> Optional[LogEntry]:
    match = LOG_ENGINE_PATTERN.match(line)
    if not match:
        return None
    return LogEntry(
        datetime=datetime.strptime(match.group("datetime"), "%Y-%m-%d %H:%M:%S.%f"),
        module=match.group("module").strip(),
        level=match.group("level").strip(),
        message=match.group("message").strip(),
    )

def parse_webservice_log(line: str) -> Optional[LogEntry]:
    match = WEBSERVICE_PATTERN.match(line)
    if not match:
        return None
    return LogEntry(
        datetime=datetime.strptime(match.group("datetime"), "%Y-%m-%d %H:%M:%S,%f"),
        module=match.group("module").strip(),
        level=match.group("level"),
        message=match.group("message").strip(),
    )

PARSERS = {
    "engine": parse_engine_log,
    "webservice": parse_webservice_log,
}

def parse_log_line(line: str, log_type: str) -> Optional[LogEntry]:
    parser = PARSERS.get(log_type)
    if not parser:
        raise ValueError(f"Unknown log type: {log_type}")
    return parser(line)


def log_parser(log_path, checkers, log_type):
    findings = []

    for log_line in log_line_generator(log_path):
        entry = parse_log_line(log_line, log_type)
        if not entry:
            continue

        for checker in checkers:
            checker_findings = checker.process(entry)
            if checker_findings:
                findings.extend(checker_findings)

    return findings

def log_file_iterator(file_path, logs_to_work, parameters):

    all_findings = []
    log_type = parameters[1]

    common_checkers = checkers.checkers()
    engine_checkers = engine_checkers_main()

    # decice active checkers
    active_checkers = list(common_checkers)
    if log_type == 'engine':
        active_checkers.extend(engine_checkers)

    for log_file in range(len(logs_to_work)):
    #for log_file in logs_to_work:
        full_log_path = os.path.join(file_path,logs_to_work[log_file])
        print(f"Processing {full_log_path}")

        findings = log_parser(full_log_path, active_checkers, log_type)
        all_findings.extend(findings)

    return all_findings