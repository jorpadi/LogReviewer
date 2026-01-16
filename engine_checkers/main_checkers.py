from datetime import datetime
from dataclasses import dataclass
import re
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

class CaptureTriggerChecker(BaseChecker):
    name = "capture_trigger_checker"

    PATTERN = re.compile(
        r"\b(requesting new capture|start code)\b",
        re.IGNORECASE
    )

    def process(self, entry, log_name):
        if self.PATTERN.search(entry.message):
            return [Finding(
                checker=self.name,
                severity="LOW",
                timestamp=entry.datetime,
                module=entry.module,
                message=entry.message,
                log_name=log_name,
                data= None
            )]
        return []

class CaptureFinalizationChecker(BaseChecker):
    name = "capture_finalization_checker"

    PATTERN = re.compile(
        r"\[(?P<event_id>[^\]]+)\]\s+Finalizing Event\s+\((?P<finalization>[^\)]+)\)",
        re.IGNORECASE
    )

    def process(self, entry, log_name):
        match = self.PATTERN.search(entry.message)
        if not match:
            return []

        event_id = match.group("event_id")
        finalization = match.group("finalization")

        severity = "HIGH" if "aborted" in finalization else "LOW"

        return [Finding(
            checker=self.name,
            severity=severity,
            timestamp=entry.datetime,
            module=entry.module,
            message=f"Event {event_id} finalized as {finalization}",
            log_name=log_name,
            data={
                "event_id": event_id,
                "finalization": finalization
            }
        )]

def engine_checkers_main():
    return [
        CaptureTriggerChecker(),
        CaptureFinalizationChecker(),
    ]
