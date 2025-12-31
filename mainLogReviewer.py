from utils.logs_folder_management import check_logs_period
from core.run_core import log_file_iterator
from pathlib import Path
from datetime import datetime

current_main_folder = Path(r"C:\Users\jpalma\Documents\LogsDataset\CNA3")

engine_files_path =  current_main_folder / "Engine"
webservice_file_path = current_main_folder / "Webservice"
start_analysis_date = datetime(2025,12,20)
end_analysis_date = datetime(2025,12,21)
dates = [start_analysis_date, end_analysis_date]
parameters = [dates]
log_type = str('engine') # engine or webservice

def main():
    logs_files_to_check = check_logs_period(engine_files_path, dates, log_type)
    print(f"Logs files to check {logs_files_to_check}")
    #logs_files_to_check = check_logs_period(webservice_file_path, dates, 'webservice')
    #print(f"Logs files to check {logs_files_to_check}")
    findings = log_file_iterator(engine_files_path, logs_files_to_check, parameters)
    print(f"Total findings: {len(findings)}")
    for f in findings:
        print(f"[{f.severity}] {f.checker} @ {f.timestamp} → {f.message}")

if __name__ == "__main__":
    main()