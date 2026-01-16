from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Finding:
    checker: str
    severity: str
    timestamp: datetime
    module: str
    message: str
    log_name: str
    data: Optional[Dict[str, Any]] = None

class BaseChecker:
    name = "base"

    def process(self, entry, log_name):
        """
        Receives a LogEntry
        Returns list[Finding]
        """
        return []

class ErrorChecker(BaseChecker):
    name = "error_checker"

    def process(self, entry, log_name):
        if entry.level == "ERROR":
            return [Finding(
                checker=self.name,
                severity="HIGH",
                timestamp=entry.datetime,
                module=entry.module,
                log_name=log_name,
                message=entry.message),
            ]
        return []

class ErrorMessageChecker(BaseChecker):
    name = "error_message_checker"

    ERROR_KEYWORDS = (
        "error",
        "ERROR"
        "failed",
        "exception",
        "fatal",
        "abort",
    )

    def process(self, entry, log_name):

        msg = entry.message.lower()

        if any(keyword in msg for keyword in self.ERROR_KEYWORDS):
            return  [Finding(
                checker=self.name,
                severity="HIGH",
                timestamp=entry.datetime,
                module=entry.module,
                log_name=log_name,
                message=entry.message)]
        return []

class WarningChecker(BaseChecker):
    name = "warning_checker"

    def process(self, entry, log_name):
        if entry.level == "WARN" or entry.level == "WARNING":
            return [Finding(
                checker=self.name,
                severity="MEDIUM",
                timestamp=entry.datetime,
                module=entry.module,
                log_name=log_name,
                message=entry.message)]
        return []

class WarningMessageChecker(BaseChecker):
    name = "warning_message_checker"

    WARNING_KEYWORDS = (
        "warning",
        "timeout",
        "offline"
    )

    def process(self, entry,log_name):
        msg = entry.message.lower()

        if any(keyword in msg for keyword in self.WARNING_KEYWORDS):
            return [Finding(
                checker=self.name,
                severity="MEDIUM",
                timestamp=entry.datetime,
                module=entry.module,
                log_name=log_name,
                message=entry.message)]
        return []

class UptimeChecker(BaseChecker):
    name = "uptime_checker"

    def __init__(self, threshold_sec):
        self.threshold = threshold_sec
        self.prev_timestamp = None

    def process(self, entry,log_name):
        findings = []

        if self.prev_timestamp:
            diff = (entry.datetime - self.prev_timestamp).total_seconds()
            if diff > self.threshold:
                findings.append(Finding(
                    checker=self.name,
                    severity="HIGH",
                    timestamp=entry.datetime,
                    module=entry.module,
                    log_name=log_name,
                    message=f"Uptime gap od {diff:.1f}s"))
        self.prev_timestamp = entry.datetime
        return findings


def checkers():
    common_checkers = [
        ErrorChecker(),
        ErrorMessageChecker(),
        WarningChecker(),
        WarningMessageChecker(),
        UptimeChecker(threshold_sec=300),
    ]
    return common_checkers