import pandas as pd
import os

def split_csv_by_trial_condition_and_bindist(input_csv, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the input CSV file into a DataFrame, specifying dtype and handling low memory
    df = pd.read_csv(input_csv, dtype=str, low_memory=False)

    # Replace 'NaN' strings with an empty string
    df.replace('NaN', '', inplace=True)

    # Fill actual NaN values with an empty string
    df.fillna('', inplace=True)

    # Ensure the necessary columns are of string type
    df['trial'] = df['trial'].astype(str)
    df['stimcondition'] = df['stimcondition'].astype(str)
    df['bindist'] = df['bindist'].astype(str)

    # Check if the necessary columns are named correctly
    if df.columns[0] != 'trial' or df.columns[1] != 'stimcondition' or df.columns[2] != 'bindist':
        df.rename(columns={df.columns[0]: 'trial', df.columns[1]: 'stimcondition', df.columns[2]: 'bindist'}, inplace=True)

    # Initialize variables to keep track of the current trial, stimcondition, and bindist
    current_trial = None
    current_condition = None
    current_bindist = None

    # Initialize an empty DataFrame to collect rows
    segment_df = pd.DataFrame()

    # Function to check if a string is a number
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        trial = row['trial']
        condition = row['stimcondition']
        bindist = row['bindist']

        # Only slice when there is a number in trial, stimcondition, or bindist
        if (is_number(trial) and trial != current_trial) or (is_number(condition) and condition != current_condition) or (is_number(bindist) and bindist != current_bindist):
            # If there is an existing segment, save it to a CSV file
            if not segment_df.empty:
                trial_dir = os.path.join(output_dir, f'trial_{current_trial}')
                if not os.path.exists(trial_dir):
                    os.makedirs(trial_dir)

                condition_dir = os.path.join(trial_dir, f'stimcondition_{current_condition}')
                if not os.path.exists(condition_dir):
                    os.makedirs(condition_dir)

                output_file = os.path.join(condition_dir, f'bindist_{current_bindist}.csv')
                segment_df.to_csv(output_file, index=False)
                print(f'Saved trial {current_trial}, stimcondition {current_condition}, bindist {current_bindist} to {output_file}')

            # Reset the current segment DataFrame
            segment_df = pd.DataFrame()

            # Update the current trial, stimcondition, and bindist
            if is_number(trial):
                current_trial = trial
            if is_number(condition):
                current_condition = condition
            if is_number(bindist):
                current_bindist = bindist

        # Append the current row to the segment DataFrame
        segment_df = pd.concat([segment_df, pd.DataFrame([row])], ignore_index=True)

    # Save the last segment if it exists
    if not segment_df.empty:
        trial_dir = os.path.join(output_dir, f'trial_{current_trial}')
        if not os.path.exists(trial_dir):
            os.makedirs(trial_dir)

        condition_dir = os.path.join(trial_dir, f'stimcondition_{current_condition}')
        if not os.path.exists(condition_dir):
            os.makedirs(condition_dir)

        output_file = os.path.join(condition_dir, f'bindist_{current_bindist}.csv')
        segment_df.to_csv(output_file, index=False)
        print(f'Saved trial {current_trial}, stimcondition {current_condition}, bindist {current_bindist} to {output_file}')

# Example usage
input_csv = r"C:\Users\ASH213\Documents\Calcium activity\890\d002\Astim890_d002_MVX.csv"  # Replace with the path to your input CSV file
output_dir = r"C:\Users\ASH213\Documents\Calcium activity\890\d002"  # Replace with your desired output directory
split_csv_by_trial_condition_and_bindist(input_csv, output_dir)
