from utils.logs_folder_management import check_logs_period
from core.run_core import log_file_iterator
from pathlib import Path
from datetime import datetime
from output_handler.text_writer import TextWriter
from output_handler.csv_writer import CSVWriter
from output_handler.statistics_builder import StatisticsBuilder
from output_handler.statistics_aggregator import StatisticsAggregator

#current_main_folder = Path(r"C:\Users\jpalma\Documents\LogsDataset\CNA3")
current_main_folder = Path(r"C:\Users\jpalma\Documents\LogsDataset\ULT1")

engine_files_path =  current_main_folder / "Engine"
webservice_file_path = current_main_folder / "Webservice"
start_analysis_date = datetime(2025,12,1)
end_analysis_date = datetime(2025,12,5)
dates = [start_analysis_date, end_analysis_date]
parameters = [dates,'engine']
#print(parameters[1])
log_type = str('engine') # engine or webservice

def main():
    logs_files_to_check = check_logs_period(engine_files_path, dates, log_type)
    #print(f"Logs files to check {logs_files_to_check}")

    findings = log_file_iterator(engine_files_path, logs_files_to_check, parameters)

    #print(f"Total findings: {len(findings)}")
    #for f in findings:
    #    print(f"[{f.severity}] {f.checker} @ {f.timestamp} → {f.message}")
    TextWriter().write(findings)
    CSVWriter("output/findings.csv").write(findings)

    stats_builder = StatisticsBuilder()

    for finding in findings:
        stats_builder.consume(finding)

    stats = stats_builder.summary()
    #logs_files_to_check = check_logs_period(webservice_file_path, dates, 'webservice')
    #print(f"Logs files to check {logs_files_to_check}")
    #findings = log_file_iterator(webservice_file_path, logs_files_to_check, parameters)
    #print(f"Total findings: {len(findings)}")
    #for f in findings:
    #    print(f"[{f.severity}] {f.checker} @ {f.timestamp} → {f.message}")
    print(stats)
    stats = StatisticsAggregator()

    for finding in findings:
        stats.consume(finding)

    summary = stats.summary()
    start, end = summary["time_window"]
    duration = summary["duration"]

    print("\n=== ENGINE ANALYSIS SUMMARY ===")
    print(f"Time window: {start} → {end}")
    print(f"Uptime window: {duration}")

    print("\nLevels:")
    for level, count in summary["levels"].items():
        print(f"  {level}: {count}")

    print("\nMessage-based counters:")
    print(f"  Error messages: {summary['error_messages']}")
    print(f"  Warning messages: {summary['warning_messages']}")

    print("\nFinalizations:")
    for k, v in summary["finalizations"].items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()