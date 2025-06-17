import pandas as pd
import os
import regex as re
from comtrade import Comtrade
import struct
import traceback
from datetime import datetime

class_list = ["Sub-Cycle Disturbance", "Sag", "Swell", "Fast Transient", "Out of Limits"]
sub_class_dict = {"Fast Transient": ["AbsThr", "DvThr"],
               "Sag": ["ITIC", "SEMI F47"],
               "Swell": ["ITIC"],
               "Out of Limits": ["Low", "Reset"]}
severity_list = ["L1", "L2", "L3", "L4", "L8"]
target_variables = ["Vab", "Van", "Vbc", "Vbn", "Vca", "Vcn", "Vllavg", "Vag", "Vbg", "Vcg"]
directory_summary_dict = {"Substation feed to Non-UPS Load from Utility A": "Non UPS load A",
                          "Substation feed to Non-UPS Load from Utility B": "Non UPS load B",
                          "Substation feed to UPS1-A": "UPS A input",
                          "Substation Feed to UPS1-B": "UPS B input",
                          "UPS1-A Output": "UPS A output",
                          "UPS1-B Output": "UPS B Output",
                          "Utility B": "Utility B"}
base_directory = "Substation feed to Non-UPS Load from Utility A"
# base_directory = "Substation feed to Non-UPS Load from Utility B"
# base_directory = "Substation feed to UPS1-A"
# base_directory = "Substation Feed to UPS1-B"
# base_directory = "UPS1-A Output"
# base_directory = "UPS1-B Output"
# base_directory = "Utility B"
sub_directory = "waveforms"

def find_matches(comtrade, file_path) -> list:
    # Iterate through all .dat files in the waveform directory
    dat_file = file_path
    cfg_file = dat_file.replace(".dat", ".cfg")
    
    try:
        # Log file details
        print(f"Processing files: {cfg_file} (size: {os.path.getsize(cfg_file)} bytes), {dat_file} (size: {os.path.getsize(dat_file)} bytes)")
        
        # Load the .cfg and .dat files
        comtrade.load(cfg_file, dat_file)
    except struct.error as e:
        print(f"Struct error loading files: {cfg_file}, {dat_file} - {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return []
    except Exception as e:
        print(f"Unexpected error with files: {cfg_file}, {dat_file} - {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return []

    # Extract the hdr content as string from the .hdr file
    hdr_content = comtrade.hdr

    # Implement re string matching to extract the class
    matches = re.findall(r"Description:.*?[+-]\d{4} ([^\n]+)", hdr_content)
    return matches

def extract_classes(matches) -> list:
    classes = []
    if not matches:
        return classes
    i = 0
    for match in matches:
        no_class_found = True
        # Check if any class in class_list is present in match
        for cls in class_list:
            if i >= len(matches):
                break
            if cls in match and i < len(matches):
                classes.append(cls)
                i += 1
                no_class_found = False
        if no_class_found:
            classes.append(None)
            i += 1
    return classes

def extract_subclass(matches, classes) -> list:
    sub_classes = []
    i = 0
    for cls in classes:
        if i >= len(matches):
            break
        if cls in sub_class_dict:
            for sub_cls in sub_class_dict[cls]:
                found = re.search(sub_cls, matches[i])
                if found:
                    sub_classes.append(sub_cls)
                    i += 1
                    break
                else:
                    continue
        else:
            sub_classes.append(None)
            i += 1
    return sub_classes

def extract_severity(matches) -> list:
    severities = []
    for match in matches:
        severity_match = re.search(r"(L[0-9])", match)
        if severity_match:
            severities.append(severity_match.group(1))
        else:
            severities.append(None)
    return severities

def extract_variables(matches) -> list:
    variables = []
    if matches == []:
        return variables
    i = 0
    for match in matches:
        if "Fast Transient" in match:
            letter  = re.findall(r"FastTransient[AD][a-zA-Z]*([A|B|C|N])", match)
            variables.append(letter[0])
            i += 1
        elif i >= len(matches):
            break
        else:
            for match in matches:
                if i >= len(matches):
                    break
                no_variable_found = True
                for variable in target_variables:
                    if variable in match and i < len(matches):
                        variables.append(variable)
                        i += 1
                        no_variable_found = False
                if no_variable_found:
                    variables.append(None)
                    i+= 1
    return variables

def extract_trigger_timestamp(comtrade):
    hdr_content = comtrade.hdr
    timestamps = re.findall(r"Description:!?\s+(\d{2}\s\w{3}\s'\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s[+-]", hdr_content)
    for i in range(len(timestamps)):
        timestamps[i] = datetime.strptime(timestamps[i], "%d %b '%y %H:%M:%S.%f")
    return timestamps
def extract_dates(timestamps):
    dates = []
    for tstamp in timestamps:
        dates.append(tstamp.date())
    return dates
def extract_hours(timestamps):
    hours = []
    for tstamp in timestamps:
        hours.append(tstamp.hour)
    return hours
def extract_minutes(timestamps):
    minutes = []
    for tstamp in timestamps:
        minutes.append(tstamp.minute)
    return minutes
def extract_seconds(timestamps):
    seconds = []
    for tstamp in timestamps:
        seconds.append(tstamp.second)
    return seconds
def extract_millisecs(timestamps):
    millisecs = []
    for tstamp in timestamps:
        millisecs.append(tstamp.microsecond // 1000)
    return millisecs
def extract_eventid(comtrade) -> str:
    hdr_content = comtrade.hdr
    eventid_matches = re.findall(r"EventID=(\d+)\n", hdr_content)
    return eventid_matches

def create_summary_table(waveform_dir) -> pd.DataFrame:
    comtrade = Comtrade()
    data = []  # List to store rows for the DataFrame

    for file in os.listdir(waveform_dir):
        if file.endswith(".dat"):
            file_path = os.path.join(waveform_dir, file)
            # file_path = "Substation feed to Non-UPS Load from Utility A/waveforms/wv00000001.dat"
            matches = find_matches(comtrade, file_path)
            classes = extract_classes(matches)
            sub_classes = extract_subclass(matches, classes)
            severities = extract_severity(matches)
            variables = extract_variables(matches)
            trigger_timestamps = extract_trigger_timestamp(comtrade)
            dates = extract_dates(trigger_timestamps)
            hours = extract_hours(trigger_timestamps)
            minutes = extract_minutes(trigger_timestamps)
            seconds = extract_seconds(trigger_timestamps)
            millisecs = extract_millisecs(trigger_timestamps)
            event_ids = extract_eventid(comtrade)

            # Strip the .dat from the file name
            file_name = os.path.splitext(file)[0]

            # Create a row for each combination of class, sub_class, severity, and variable
            for i in range(len(matches)):
                row = {
                    "device": directory_summary_dict[base_directory],  # Static value for device
                    "file": file_name,  # File name without .dat
                    "event_id": event_ids[i] if i < len(event_ids) else None,
                    "trigger_timestamp": trigger_timestamps[i] if i < len(trigger_timestamps) else None,
                    "date": dates[i] if i < len(dates) else None,
                    "hour": hours[i] if i < len(hours) else None,
                    "minute": minutes[i] if i < len(minutes) else None,
                    "second": seconds[i] if i < len(seconds) else None,
                    "millisec": millisecs[i] if i < len(millisecs) else None,
                    "variable": variables[i] if i < len(variables) else None,
                    "class": classes[i] if i < len(classes) else None,
                    "sub_class": sub_classes[i] if i < len(sub_classes) else None,
                    "severity": severities[i] if i < len(severities) else None,
                }
                data.append(row)

    # Create DataFrame with the specified columns
    columns = ["device","file","event_id","trigger_timestamp","date","hour","minute","second","millisec","variable", "class", "sub_class", "severity"]
    summary_table = pd.DataFrame(data, columns=columns)
    return summary_table
    

def main():
    # Define the path to the waveform directory
    waveform_dir = os.path.join(base_directory, sub_directory)

    # Create summary table
    summary_table = create_summary_table(waveform_dir)

    # Save the summary table to a CSV file
    output_dir = "Final_Summary_Tables"
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    output_file = os.path.join(output_dir, f"{base_directory}_summary_table.csv")
    summary_table.to_csv(output_file, index=False)
    print(f"Summary table saved to {output_file}")

if __name__ == "__main__":
    main()