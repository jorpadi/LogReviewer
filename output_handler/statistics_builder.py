from collections import Counter, defaultdict

class StatisticsBuilder:

    def __init__(self):
        self.stats = defaultdict(Counter)

    def consume(self, finding):
        if not finding.data:
            return

        if finding.checker == "capture_finalization_checker":
            finalization = finding.data.get("finalization")
            if finalization:
                self.stats["capture_finalization"][finalization] += 1

    def summary(self):
        return dict(self.stats)