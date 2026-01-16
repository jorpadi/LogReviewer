from common_checkers import checkers
from engine_checkers.main_checkers import engine_checkers_main
from datetime import datetime
import re
from dataclasses import dataclass
from typing import Optional
from config.config_loader import load_config
from pathlib import Path
from utils.logs_folder_management import check_logs_period
from output_handler.csv_writer import CSVWriter
from utils.log_handler import logger

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

LOG_TYPE_BY_FOLDER = {
    "Engine": "engine",
    "LSA": "engine",        # same date format
    "AgenteETL": "engine",  # adjust if needed
    "WebService": "webservice"
}

def log_line_generator(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        logger.error("ERROR",f"Error: File not found at {file_path}")

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

        log_name = Path(log_path).stem
        for checker in checkers:
            checker_findings = checker.process(entry, log_name)
            if checker_findings:
                findings.extend(checker_findings)

    return findings

def check_extension_pathlib(filename, expected_extension):
    file_path = Path(filename)

    return file_path.suffix.lower() == expected_extension.lower()

def log_file_iterator(logs_to_work, log_type):
    all_findings = []

    #print(f"Tipo de log: {log_type}")

    common_checkers = checkers.checkers()
    engine_specific_checkers = engine_checkers_main()

    active_checkers = list(common_checkers)
    if log_type == 'engine':
        active_checkers.extend(engine_specific_checkers)

    for full_log_path in logs_to_work:
        if check_extension_pathlib(full_log_path, '.log'):
            logger.info("log_file_iterator", f"Processing {full_log_path}")
            findings = log_parser(full_log_path, active_checkers, log_type)
            all_findings.extend(findings)
        else:
            continue
    return all_findings

def run_batch_log():

    config = load_config("config/config.json")
    main_folder = Path(config["main_logs_path"])
    folders = config["FoldersToCheck"]
    initial_date = config['start_date']
    final_date = config['end_date']
    date_range = (initial_date, final_date)
    all_findings = []
    all_logs_to_check = []
    logger.info("run_batch_log", "Log Reviewer started!")

    for folder in folders:
        full_path = main_folder / folder
        log_type = LOG_TYPE_BY_FOLDER.get(folder)
        if not log_type:
            logger.warning("run_batch_log", f"Unknown log type for folder {folder}")
            continue

        logs = check_logs_period(full_path, date_range, log_type)
        all_logs_to_check.extend(logs)
        if not logs:
            continue
        findings = log_file_iterator(logs, log_type)
        all_findings.extend(findings)

    plant_acronym = str(main_folder.name)
    output_file_name = Path(f'output/findings_{plant_acronym}_from_{str(initial_date.date())}_to_{str(final_date.date())}.csv')
    CSVWriter(output_file_name).write(all_findings)
    logger.info("run_batch_log",f"Output written on {str(output_file_name)}")
    logger.info("run_batch_log","Log Reviewer Ended!")

    return
