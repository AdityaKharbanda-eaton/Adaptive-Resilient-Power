def main():
    import pandas as pd
    import glob

    # Specify the path to the folder containing the CSV files
    csv_folder_path = "Final_Summary_Tables"

    # Use glob to get all CSV file paths in the folder
    csv_files = glob.glob(f"{csv_folder_path}/*.csv")

    # Read and concatenate all CSV files into a single DataFrame
    merged_df = pd.concat(
        (pd.read_csv(file, parse_dates=True, infer_datetime_format=False) for file in csv_files),
        ignore_index=True
    )

    # # Ensure datetime columns are displayed as whole and exact
    # for col in merged_df.select_dtypes(include=['datetime64']).columns:
    #     merged_df[col] = merged_df[col].dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Save the merged DataFrame back to a CSV file
    output_csv_file = "final_waveform_summary.csv"
    merged_df.to_csv(output_csv_file, index=False)

    print(f"Merged CSV saved to {output_csv_file}")


if __name__ == "__main__":
    main()
