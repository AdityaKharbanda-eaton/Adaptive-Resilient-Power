import os
# import pandas as pd
from comtrade import load_as_dataframe
import struct

def convert_dat_to_csv(base_dir):
    """
    Converts all .dat files in the waveform folder of the given base directory
    to CSV files and stores them in the respective folder (Input or Output) 
    in the 'Waveform CSVs' directory.
    """
    # Define paths
    waveform_dir = os.path.join(base_dir, "waveforms")
    output_dir = os.path.join("Waveform CSVs", os.path.basename(base_dir))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Comtrade object
    # comtrade = Comtrade()
    
    # Iterate through all .dat files in the waveform directory
    for file in os.listdir(waveform_dir):
        if file.endswith(".dat"):
            dat_file = os.path.join(waveform_dir, file)
            cfg_file = dat_file.replace(".dat", ".cfg")
            
            print(f"Processing file: {file}")
            try:
                # Convert to pandas DataFrame using load_as_dataframe method
                df = load_as_dataframe(cfg_file, dat_file)
                
                # Save DataFrame to CSV
                csv_file = os.path.join(output_dir, file.replace(".dat", ".csv"))
                df.to_csv(csv_file, index=True)
                print(f"Converted {file} to {csv_file}")
            except struct.error as e:
                print(f"Struct error while processing {file}: {e}")
            except Exception as e:
                print(f"Error while processing {file}: {e}")

# Replace 'UPS1-A-Input' or 'UPS1-A-Output' with the actual base directory path
base_directory = "Substation feed to Non-UPS Load from Utility A"  # or "UPS1-A-Output"
convert_dat_to_csv(base_directory)