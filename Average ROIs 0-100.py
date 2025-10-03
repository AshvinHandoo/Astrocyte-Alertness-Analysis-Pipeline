import os
import pandas as pd

def average_calcium(csv_files, output_path):
    # List to store the calcium column data
    calcium_data = []

    # Read the CSV files and extract the calcium column
    for file in csv_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            if 'calcium' in df.columns:
                calcium_data.append(df['calcium'])
            else:
                print(f"Warning: 'calcium' column not found in {file}")
        else:
            print(f"Warning: File not found: {file}")

    if not calcium_data:
        print(f"No valid calcium data found for {output_path}. Skipping.")
        return

    # Concatenate the calcium columns into a DataFrame and calculate the row-wise mean
    calcium_df = pd.concat(calcium_data, axis=1)
    avg_calcium = calcium_df.mean(axis=1)

    # Read the first CSV file to use its other columns
    first_df = pd.read_csv(csv_files[0])

    # Replace the calcium column with the average values
    first_df['calcium'] = avg_calcium

    # Save the result to the specified output path
    first_df.to_csv(output_path, index=False)

    print(f"Averaged calcium data saved to '{output_path}'")


# Base paths and file names
base_path = r"C:\Users\ASH213\Documents\Correlated\890\d084"
trials = [f"trial_{i}" for i in range(1, 4)]
stimconditions = [f"stimcondition_{i}" for i in range(1, 6)]
bin_distances = [0, 20, 40, 60, 80, 100]

# Iterate through trials and stimconditions
for trial in trials:
    for stimcondition in stimconditions:
        # Generate the list of CSV file paths
        csv_files = [os.path.join(base_path, trial, stimcondition, f"bindist_{bd}.csv") for bd in bin_distances]
        output_path = os.path.join(base_path, trial, stimcondition, 'bindist_2000.csv')

        # Call the function to average calcium data
        average_calcium(csv_files, output_path)
