from collections import Counter
from datetime import timedelta

class StatisticsAggregator:

    def __init__(self):
        self.level_counter = Counter()
        self.message_error_counter = 0
        self.message_warning_counter = 0
        self.finalization_counter = Counter()

        self.first_timestamp = None
        self.last_timestamp = None

    def consume(self, finding):
        # Track time window
        ts = finding.timestamp
        if not self.first_timestamp or ts < self.first_timestamp:
            self.first_timestamp = ts
        if not self.last_timestamp or ts > self.last_timestamp:
            self.last_timestamp = ts

        # Level-based stats
        self.level_counter[finding.severity] += 1

        # Checker-based stats
        if finding.checker == "error_message_checker":
            self.message_error_counter += 1

        if finding.checker == "warning_message_checker":
            self.message_warning_counter += 1

        if finding.checker == "capture_finalization_checker" and finding.data:
            finalization = finding.data.get("finalization")
            if finalization:
                self.finalization_counter[finalization] += 1

    def uptime_summary(self):
        if not self.first_timestamp or not self.last_timestamp:
            return None

        duration = self.last_timestamp - self.first_timestamp
        return duration

    def summary(self):
        return {
            "time_window": (self.first_timestamp, self.last_timestamp),
            "duration": self.uptime_summary(),
            "levels": dict(self.level_counter),
            "error_messages": self.message_error_counter,
            "warning_messages": self.message_warning_counter,
            "finalizations": dict(self.finalization_counter),
        }