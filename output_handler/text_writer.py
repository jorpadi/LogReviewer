class TextWriter:
    def write(self, findings):
        for f in findings:
            print(
                f"[{f.severity}] {f.checker} | "
                f"{f.timestamp} | {f.module} → {f.message}"
            )