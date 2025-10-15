import pandas as pd
import numpy as np
import os

def calculate_derivative_and_threshold(input_csv, output_csv, stimcondition):
    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Normalize the "calcium" column to its maximum value
    df['calcium'] = df['calcium'] / df['calcium'].max()

    # Calculate the derivative using numpy's gradient function
    df['Pupil Diameter Ratio Derivative'] = np.gradient(df['Pupil Diameter Ratio'], df['time'])

    # Define primary thresholds based on stimcondition
    primary_thresholds = {
        1: (0.3155, -0.3174),
        2: (0.3174, -0.3192),
        3: (0.3377, -0.3426),
        4: (0.3250, -0.3317),
        5: (0.3257, -0.3298)
    }

    # Define secondary thresholds based on stimcondition
    secondary_thresholds = {
        1: (0.1571, -0.1591),
        2: (0.1569, -0.1602),
        3: (0.1674, -0.1708),
        4: (0.1618, -0.1644),
        5: (0.1617, -0.1660)
    }

    # Get the thresholds for the given stimcondition
    upper_primary_threshold, lower_primary_threshold = primary_thresholds.get(stimcondition)
    upper_secondary_threshold, lower_secondary_threshold = secondary_thresholds.get(stimcondition)

    if upper_primary_threshold is None or upper_secondary_threshold is None:
        raise ValueError("Invalid stimcondition")

    # Add the "threshold" column
    df['threshold'] = df['Pupil Diameter Ratio Derivative'].apply(
        lambda x: 'yes' if x > upper_primary_threshold else 'no'
    )

    # Check for the secondary threshold condition
    above_secondary_threshold = df['Pupil Diameter Ratio Derivative'] > upper_secondary_threshold
    consecutive_counts = (above_secondary_threshold.groupby((~above_secondary_threshold).cumsum()).cumsum() >= 5)
    df.loc[consecutive_counts, 'threshold'] = 'yes'

    # Save the modified dataframe to a new CSV file
    df.to_csv(output_csv, index=False)


def process_directory(base_input_dir, base_output_dir):
    # Ensure the output directory exists
    os.makedirs(base_output_dir, exist_ok=True)

    days = ["d084", "d070", "d056", "d028", "d021", "d014", "d007", "d003", "d001"]
    for day in days:
        input_dir = os.path.join(base_input_dir, day)
        output_dir = os.path.join(base_output_dir, day)
        for trial in range(1, 4):
            trial_dir = f"trial_{trial}"
            for stimcondition in range(1, 6):
                stimcondition_dir = f"stimcondition_{stimcondition}"
                input_file = os.path.join(input_dir, trial_dir, stimcondition_dir, "bindist_2000.csv")
                output_file = os.path.join(output_dir, trial_dir, stimcondition_dir, "bindist_2020.csv")

                # Ensure the output subdirectory exists
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                if os.path.exists(input_file):
                    calculate_derivative_and_threshold(input_file, output_file, stimcondition)
                else:
                    print(f"File {input_file} does not exist.")


base_input_dir = r"C:\Users\ASH213\Documents\Correlated\890"
base_output_dir = r"C:\Users\ASH213\Documents\Correlated\890"
process_directory(base_input_dir, base_output_dir)
