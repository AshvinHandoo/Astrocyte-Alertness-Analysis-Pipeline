import pandas as pd
import numpy as np
import os
import re

def extract_info_from_filename(filename):
    match = re.search(r'(d\d+)_trial_(\d+)_stimcondition_(\d+)_index_(\d+)', filename)
    if match:
        day = match.group(1)
        trial = f"trial_{match.group(2)}"
        stimcondition = f"stimcondition_{match.group(3)}"
        index = int(match.group(4))
        return day, trial, stimcondition, index
    return None

def calculate_avg_std(csv_file, folder_path):
    # Extract the relevant parts from filenames in the folder
    file_info = []
    for filename in os.listdir(folder_path):
        info = extract_info_from_filename(filename)
        if info:
            file_info.append(info)

    print(f"Extracted information from filenames: {file_info}")

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Ensure the required columns exist in the CSV
    required_columns = ['Day', 'Trial', 'StimCondition', 'Index', 'TimeDifference']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The CSV file must contain columns: {required_columns}")

    # Print the first few rows of the DataFrame for debugging
    print("First few rows of the CSV DataFrame:")
    print(df.head())

    # Filter the DataFrame based on the extracted information
    filtered_df = pd.DataFrame()
    for day, trial, stimcondition, index in file_info:
        temp_df = df[(df['Day'] == day) &
                     (df['Trial'] == trial) &
                     (df['StimCondition'] == stimcondition) &
                     (df['Index'] == index)]
        if not temp_df.empty:
            filtered_df = pd.concat([filtered_df, temp_df])

    print(f"Filtered DataFrame:\n{filtered_df}")

    # Extract the TimeDifference column from the filtered DataFrame
    time_differences = filtered_df['TimeDifference']

    # Ensure TimeDifference column is numeric
    time_differences = pd.to_numeric(time_differences, errors='coerce')
    time_differences = time_differences.dropna()

    if time_differences.empty:
        raise ValueError("No matching time differences found after filtering and converting to numeric values")

    # Calculate average and standard deviation
    average = np.mean(time_differences)
    std_deviation = np.std(time_differences)

    return average, std_deviation

# Example usage:
if __name__ == "__main__":
    csv_file = r"C:\Users\ASH213\Documents\Correlated\890\dilation+constriction_events\time_differences.csv"  # Replace with your CSV file path
    folder_path = r"C:\Users\ASH213\Documents\Correlated\890\dilation+constriction_events\good"  # Replace with your folder path
    avg, std = calculate_avg_std(csv_file, folder_path)
    print(f"Average TimeDifference: {avg}")
    print(f"Standard Deviation of TimeDifference: {std}")
