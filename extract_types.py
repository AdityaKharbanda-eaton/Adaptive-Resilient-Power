import os
import pandas as pd
from comtrade import Comtrade
import re
import struct
import traceback
# from comtrade import load_as_dataframe

def unique_classes(base_dir):
    """
    Extracts all the possible classes of Events from the .hdr files of waveforms.
    """
    # Define paths
    waveform_dir = os.path.join(base_dir, "waveforms")

    class_set = set()
    
    
    # Initialize Comtrade object
    comtrade = Comtrade()
    
    # Iterate through all .dat files in the waveform directory
    for file in os.listdir(waveform_dir):
        if file.endswith(".dat"):
            dat_file = os.path.join(waveform_dir, file)
            cfg_file = dat_file.replace(".dat", ".cfg")
            
            try:
                # Log file details
                print(f"Processing files: {cfg_file} (size: {os.path.getsize(cfg_file)} bytes), {dat_file} (size: {os.path.getsize(dat_file)} bytes)")
                
                # Load the .cfg and .dat files
                comtrade.load(cfg_file, dat_file)
            except struct.error as e:
                print(f"Struct error loading files: {cfg_file}, {dat_file} - {e}")
                traceback.print_exc()  # Print the full traceback for debugging
                continue
            except Exception as e:
                print(f"Unexpected error with files: {cfg_file}, {dat_file} - {e}")
                traceback.print_exc()  # Print the full traceback for debugging
                continue

            # Extract the hdr content as string from the .hdr file
            hdr_content = comtrade.hdr

            # Implement re string matching to extract the class
            matches = re.findall(r"Description:.*?[+-]\d{4} ([^\n]+)", hdr_content)

            # Add the extracted class to the set of classes
            class_set.update(matches)
            
    return class_set

base_directory = "Substation feed to Non-UPS Load from Utility A"
class_set = sorted(unique_classes(base_directory))
# Write the class_set to a .txt file


os.makedirs(f"Classes", exist_ok=True)
output_dir = os.path.join("Classes", base_directory)
output_file = f"Classes/{base_directory}_types.txt"
with open(output_file, "w") as f:
    f.write("\n".join(class_set))

    