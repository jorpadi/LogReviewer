from datetime import datetime
from dataclasses import dataclass

@dataclass
class Finding:
    checker: str
    severity: str
    timestamp: datetime
    module: str
    message: str

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


def checkers():
    common_checkers = [
        ErrorChecker(),
        WarningChecker(),
        UptimeChecker(threshold_sec=300),
    ]
    return common_checkers