import os

# Global set to store unique strings
global_set = set()

def update_global_set_from_txt(directory):
    """
    Reads all .txt files in the given directory and updates the global set
    with unique strings from each row of the files.
    """
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            txt_file_path = os.path.join(directory, file)
            with open(txt_file_path, 'r') as txt_file:
                for line in txt_file:
                    # Strip whitespace and add the string to the global set
                    global_set.add(line.strip())

def write_combined_classes(directory):
    """
    Writes the content of the global set to a file named 'combined_classes'
    in the specified directory.
    """
    combined_file_path = directory + "/combined_classes.txt"
    with open(combined_file_path, 'w') as combined_file:
        for item in sorted(global_set):  # Sort for consistent output
            combined_file.write(item + '\n')
    print(f"Combined classes written to {combined_file_path}")

# Update global set from Classes folder and write combined_classes file
classes_folder = "Classes"
update_global_set_from_txt(classes_folder)
write_combined_classes(classes_folder)