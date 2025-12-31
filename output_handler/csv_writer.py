import csv

class CSVWriter:
    def __init__(self, output_path):
        self.output_path = output_path

    def write(self, findings):
        with open(self.output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "severity",
                "checker",
                "module",
                "message"
            ])

            for fnd in findings:
                writer.writerow([
                    fnd.timestamp,
                    fnd.severity,
                    fnd.checker,
                    fnd.module,
                    fnd.message
                ])