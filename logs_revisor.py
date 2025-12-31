import pandas as pd 
from pathlib import Path
import re
import os
import json
from datetime import datetime, timedelta

current_main_folder = Path(r"C:\Users\jpalma\Documents\ANALISIS\CAC3_Registros")

events_expired = current_main_folder / "events_not_founded.txt"
engine_files_path =  current_main_folder / "LogsEngine" 
webservice_file_path = current_main_folder / "LogsWebservice" 

output_file_engine = current_main_folder / "events_expired_engine.txt"
output_ws_cs = current_main_folder / "dataframe_licence_ws.csv"

ws_csv = current_main_folder / "dataframe_licence_ws.csv"
xml_csv = current_main_folder / "extracted_data_2025-11-10_09-58-49.csv"

match_csv = current_main_folder / "matched_df.csv"

def log_line_generator(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")

# Engine log revisor
def check_expired_from_engine(engine_files_path, output_file):
    pattern_task_expired = str("Task 'tsk.event_check_task_expired' exited with status 'OK'")
    event_counter = str()
    expired_events_engine = list()

    for entry_name in os.listdir(engine_files_path):
        
        full_path = os.path.join(engine_files_path, entry_name)
        print(f"Checking: {full_path}")
        if os.path.isfile(full_path):
            #print(f"File: {entry_name}")
            for line in log_line_generator(full_path):
                if pattern_task_expired in line:
                    acronym = r'\[(LM-[\w\d]+-[A-Z]-\d+)\]'
                    event_counter = re.search(acronym, line)
                    expired_events_engine.append(event_counter[1])

    print(f"Expired event search Done! Founded {len(expired_events_engine)} expired events")
    with open(output_file, 'w') as fp:
        for event in expired_events_engine:
            fp.write("%s\n" % event)
        print('Done')

# Webservice log revisor
def check_licence_plates_from_ws(webservice_file_path, output_ws_cs):

    rmadera_reception = "INFO  RMaderaInputController - {"
    webservice_status = "Command received: "
    licence_plate_flag = int(0)
    licence_plate_counter = int(0)
    json_pattern = re.compile(r'\{[\s\S]*?\}')
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    extracted_json_objects = []
    extracted_rmadera_response = []

    df_ws = pd.DataFrame(columns=['licence_plate','ws_response','creation_timestamp'])

    for entry_name in os.listdir(webservice_file_path):
        
        full_path = os.path.join(webservice_file_path, entry_name)

        if os.path.isfile(full_path):
            print(f"Checking: {full_path}")
            for line in log_line_generator(full_path):

                if licence_plate_flag == 1:
                    if webservice_status in line:
                        licence_plate_response_line = line.split('-', 3)
                        match = re.search(timestamp_pattern, line)
                        timestamp_str = match.group(0)
                        extracted_rmadera_response.append(licence_plate_response_line[3])
                        #print(f"Command received: {licence_plate_response_line[3]} at {timestamp_str}")
                        # update dataframe: , licence_plate_response_line[3], timestamp_str
                        df_ws.at[licence_plate_counter, 'ws_response'] = licence_plate_response_line[3]
                        df_ws.at[licence_plate_counter, 'creation_timestamp'] = timestamp_str

                if rmadera_reception in line:
                    licence_plate_counter = licence_plate_counter + 1
                    matches = json_pattern.findall(line)
                    for match in matches:
                        try:
                            json_object = json.loads(match)
                            #print(json_object['patenteCabina'])
                            extracted_json_objects.append(json_object)
                        except json.JSONDecodeError:
                            # Handle cases where the extracted string isn't valid JSON
                            print(f"Skipping invalid JSON match: {match}")
                    # update dataframe: json_object['patenteCabina'] , ,
                    df_ws.at[licence_plate_counter, 'licence_plate'] = json_object['patenteCabina']
                    licence_plate_flag = 1
                    #print(f"Flag patente: {licence_plate_flag} | Found rmadera Input: {line} ")
                else:
                    licence_plate_flag = 0

    df_ws.to_csv(output_ws_cs)
    print("Webservice search Done!")
    print(f"Jsons founded: {len(extracted_json_objects)}")
    print(f"ramederas responses: {len(extracted_rmadera_response)}")

def event_licence_plate_ws_match(xml_extracted_csv, ws_csv, output_csv):
    # generar dataframe final con lo siguiente
    # evento_id | patente | fecha creacion logmeter |patente enviada? | enviada dentro rango 1h30m despues de creacion?|* finalizacion captura *| envio1 patente ws | respuesta1 |hora respuesta1 | envio2 patente | respuesta 2 |hora respuesta2

    xml_extracted_df = pd.read_csv(xml_extracted_csv)
    ws_founded_df = pd.read_csv(ws_csv)
    final_info = pd.DataFrame(columns=['Evento','Patente','Fecha creacion','patente recepcionada?','enviada dentro rango 1h30m despues de creacion?','envio1 patente ws', 'respuesta1','hora respuesta1'])
    licence_plate_founded_counter = int(0)
    licence_plate_not_founded_counter = int(0)
    event_counter = int(0)
    event_licence_plate = str()
    time_window = timedelta(days=0, hours=1, minutes=30)

    for event in range(len(xml_extracted_df['Event ID'])):
        # from each event search licence plate from webservice if Founded
        event_licence_plate = xml_extracted_df['patente1'][event]
        filtered_df = ws_founded_df[ws_founded_df['licence_plate'].str.contains(event_licence_plate)]
        #print(filtered_df.head())
        # not licence plate founded
        if filtered_df.empty:
            #print(f"Patente {xml_extracted_df['patente1'][event]} from event {xml_extracted_df['Event ID'][event]} not founded :(")
            licence_plate_not_founded_counter = licence_plate_not_founded_counter + 1
            final_info.at[event_counter, 'Evento'] = xml_extracted_df['Event ID'][event]
            final_info.at[event_counter, 'Patente'] = xml_extracted_df['patente1'][event]
            final_info.at[event_counter, 'Fecha creacion'] = xml_extracted_df['date_creation'][event]
            final_info.at[event_counter, 'patente recepcionada?'] = "no"

        # licence plate founded
        else:
            final_info.at[event_counter, 'Evento'] = xml_extracted_df['Event ID'][event]
            final_info.at[event_counter, 'Patente'] = xml_extracted_df['patente1'][event]
            final_info.at[event_counter, 'Fecha creacion'] = xml_extracted_df['date_creation'][event]
            final_info.at[event_counter, 'patente recepcionada?'] = "si"

            # si llego mas de una patente en el periodo analizado
            if len((filtered_df)) > 1:
                #print(" ")
                logmeter_timestamp = xml_extracted_df['date_creation'][event]
                t_meter = datetime.strptime(logmeter_timestamp, "%Y-%m-%d %H:%M:%S")
                time_window_end = t_meter + time_window
                #print(type(filtered_df['licence_plate']))
                
                for _, row in filtered_df.iterrows():
                    ws_timestamp = row['creation_timestamp']
                    ws_response = row['ws_response']
                    ws_plate = row['licence_plate']
                    #print(ws_timestamp)
                    # si el timestamp viene como string, convertirlo a datetime
                    try:
                        t_ws = datetime.strptime(ws_timestamp, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                    # manejar NaN o formatos inválidos
                        t_ws = datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

                     # comparar con la ventana temporal
                    if t_meter <= t_ws <= time_window_end:
                        print(f"Patente {ws_plate} dentro del rango: {t_ws}")
                        final_info.at[event_counter, 'enviada dentro rango 1h30m despues de creacion?'] = "si"
                        final_info.at[event_counter, 'envio1 patente ws'] = ws_plate
                        final_info.at[event_counter, 'respuesta1'] = ws_response
                        final_info.at[event_counter, 'hora respuesta1'] = t_ws
                    else:
                        #print(f"Patente {ws_plate} fuera de rango ({t_ws})")
                        final_info.at[event_counter, 'enviada dentro rango 1h30m despues de creacion?'] = "no"
                #print(f"Patentes {xml_extracted_df['patente1'][event]} from event {xml_extracted_df['Event ID'][event]} founded: {len(filtered_df)}")
            # si solo llego una patente en el periodo analizado
            else:
                ws_licence_plate = filtered_df['licence_plate'].to_string()
                ws_timestamp = filtered_df['creation_timestamp'].to_string()
                ws_response = filtered_df['ws_response'].to_string()
                licence_plate_parts = ws_licence_plate.rsplit(' ', 1) # Split at most 1 time from the right
                ws_timestamp_parts = ws_timestamp.rsplit(' ', 2)
                ws_response_parts = ws_response.rsplit(' ', 1)
                ws_timestamp = ws_timestamp_parts[1] + " " + ws_timestamp_parts[2]
                #print(ws_timestamp)
                logmeter_timestamp = xml_extracted_df['date_creation'][event]
                t_meter = datetime.strptime(logmeter_timestamp, "%Y-%m-%d %H:%M:%S")

                # lidiar con los campos NaN (agregar espacio asi: NaN)
                if ws_timestamp == ' NaN':
                    ws_timestamp = datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                else:
                    t_ws    = datetime.strptime(ws_timestamp, "%Y-%m-%d %H:%M:%S")
                    time_window_end = t_meter + time_window
                    # si la patente encontrada esta dentro de las 1h30min luego de creado el evento
                    if t_meter <= t_ws <= time_window_end:
                        #print(f"{t_ws} esta entre {t_meter} y {time_window_end}")
                        final_info.at[event_counter, 'enviada dentro rango 1h30m despues de creacion?'] = "si"
                        final_info.at[event_counter, 'envio1 patente ws'] = licence_plate_parts[1]
                        final_info.at[event_counter, 'respuesta1'] = ws_response_parts[1]
                        final_info.at[event_counter, 'hora respuesta1'] = t_ws
                    else:
                        #print(f"{t_ws} no esta entre {t_meter} y {time_window_end}, fuera de rango horario")
                        final_info.at[event_counter, 'enviada dentro rango 1h30m despues de creacion?'] = "no"

            licence_plate_founded_counter = licence_plate_founded_counter + 1

        event_counter = event_counter + 1

    final_info.to_csv(output_csv)
    not_founded_percentage = (licence_plate_not_founded_counter/len(xml_extracted_df['patente1'])) * 100
    licence_plate_founded_percentage = 100 - not_founded_percentage
    print(f"Licence plate founded: {licence_plate_founded_counter} ({licence_plate_founded_percentage:.2f}%)")
    print(f"Licence plate not founded: {licence_plate_not_founded_counter} ({not_founded_percentage:.2f}%)")

def main():
    #check_expired_from_engine(engine_files_path, output_file_engine)
    #check_licence_plates_from_ws(webservice_file_path, output_ws_cs)
    event_licence_plate_ws_match(xml_csv, ws_csv, match_csv)

if __name__ == "__main__":
    main()