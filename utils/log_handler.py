from datetime import datetime
from pathlib import Path

class LogHandler:

    def __init__(self, log_dir: str = "logs", log_name: str = "LogReviewer"):
        """
        log_name should be base name without extension.
        Final file will look like: app_2025-12-02.log
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_base_name = log_name

        # Build dated log path
        self.log_path = self._build_log_path()

    def _build_log_path(self) -> Path:
        """Return log file path with today's date."""
        today = datetime.now().strftime("%Y-%m-%d")  # change format here
        filename = f"{today}.{self.log_base_name}.log"
        return self.log_dir / filename

    def _timestamp(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _rotate_daily(self):
        """If date changed, refresh the log file path."""
        current_expected = self._build_log_path()
        if current_expected != self.log_path:
            self.log_path = current_expected

    def _write(self, module: str, level: str, message: str):
        # Before writing, verify date hasn’t changed
        self._rotate_daily()

        log_line = f"[{self._timestamp()}][{module.upper()}][{level.upper()}] {message}"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        print(log_line)

    # Public API
    def info(self, module: str, message: str):
        self._write(module, "INFO", message)

    def warning(self, module: str, message: str):
        self._write(module, "WARNING", message)

    def error(self, module: str, message: str):
        self._write(module, "ERROR", message)

    def debug(self, module: str, message: str):
        self._write(module, "DEBUG", message)

logger = LogHandler() # global singleton logger