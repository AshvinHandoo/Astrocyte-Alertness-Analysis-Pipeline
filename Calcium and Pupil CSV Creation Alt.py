import pandas as pd
import os
import re
import logging

# Set up logging configuration
logging.basicConfig(filename='pupil_diameter_averaging.log', level=logging.INFO, format='%(message)s')

def extract_averaged_pupil_diameters(filtered_file):
    # Read the filtered CSV file
    df_filtered = pd.read_csv(filtered_file)
    df_filtered = df_filtered.iloc[1:]  # Skip the first row

    # Calculate the pupil diameter ratio
    if 'Pupil Diameter' in df_filtered.columns and 'Eye gap' in df_filtered.columns:
        df_filtered['Pupil Diameter Ratio'] = df_filtered['Pupil Diameter'] / df_filtered['Eye gap']
    else:
        logging.error(f"Missing necessary columns in {filtered_file}")
        return None, 0

    # Get the total number of pupil diameter data points
    total_pupil_points = len(df_filtered)
    logging.info(f"Total pupil points in {os.path.basename(filtered_file)} (excluding first row): {total_pupil_points}")  # Log the info

    return df_filtered, total_pupil_points

def add_pupil_diameters_to_untouched(untouched_folder, df_filtered, total_pupil_points, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the untouched folder
    for file in os.listdir(untouched_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(untouched_folder, file)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            # Ensure the DataFrame has exactly 1198 rows
            if len(df) > 1198:
                df = df.iloc[:1198]  # Truncate to 1198 rows if there are more
            elif len(df) < 1198:
                # Add empty rows if less than 1198 frames
                missing_rows = 1198 - len(df)
                df = df.append(pd.DataFrame([{}] * missing_rows), ignore_index=True)

            # Skip files with no data points in the "calcium" column
            if "calcium" not in df.columns or df["calcium"].count() == 0:
                logging.info(f"Skipping {file} because it has 0 calcium data points.")
                continue

            # Calculate the ratio for this specific file
            calcium_count = df["calcium"].count()
            logging.info(f"File: {file} | Calcium data points: {calcium_count}")  # Log the info
            if calcium_count == 0:
                ratio = 1  # To avoid division by zero
            else:
                ratio = total_pupil_points / calcium_count
            logging.info(f"File: {file} | Ratio: {ratio}")  # Log the info

            # Initialize an empty list to store averaged pupil diameter ratio values for this file
            averaged_pupil_diameter_ratios = []

            # Initialize variables to manage the cumulative ratio
            cumulative_ratio = 0
            start_idx = 0

            # Calculate the average of 'ratio' rows starting from the second row
            for i in range(calcium_count):
                cumulative_ratio += ratio
                end_idx = round(cumulative_ratio)
                subset = df_filtered['Pupil Diameter Ratio'].iloc[start_idx:end_idx]
                num_points = end_idx - start_idx
                logging.info(f"Averaging {num_points} points from index {start_idx} to {end_idx} for file {file}.")  # Log the info
                if len(subset) > 0:  # Ensure subset is not empty
                    averaged_pupil_diameter_ratios.append(subset.mean())
                start_idx = end_idx

            # Create an iterator for the pupil diameter ratios list
            pupil_diameters_iter = iter(averaged_pupil_diameter_ratios)
            # Add the pupil diameter ratio values to the DataFrame starting from the first row
            pupil_diameters_to_add = [next(pupil_diameters_iter, '') for _ in range(1198)]
            if len(pupil_diameters_to_add) < 1198:
                logging.info(f"Warning: Not enough pupil diameters for file {file}")
                pupil_diameters_to_add.extend([''] * (1198 - len(pupil_diameters_to_add)))
            df['Pupil Diameter Ratio'] = pupil_diameters_to_add
            # Save the modified DataFrame to the output folder
            output_file_path = os.path.join(output_folder, file)
            df.to_csv(output_file_path, index=False)

def process_folders(filtered_folder, untouched_base_folder, output_base_folder):
    for filtered_file in os.listdir(filtered_folder):
        if filtered_file.endswith(".csv"):
            filtered_file_path = os.path.join(filtered_folder, filtered_file)
            stimulation = None
            if 'contra' in filtered_file:
                logging.info(f"Skipping {filtered_file} due to unknown stimulation type.")
                continue
            elif 'burst' in filtered_file:
                stimulation = "stimcondition_2"
            elif '10Hz' in filtered_file:
                stimulation = 'stimcondition_1'
            elif '100Hz' in filtered_file:
                stimulation = 'stimcondition_4'
            elif 'tbs' in filtered_file:
                stimulation = 'stimcondition_3'
            elif 'line' in filtered_file:
                stimulation = 'stimcondition_5'
            if not stimulation:
                logging.info(f"Skipping {filtered_file} due to unknown stimulation type.")
                continue

            if '890' in filtered_file:
                animal = '890'
            elif '889' in filtered_file:
                animal = '889'
            else:
                logging.info(f"Skipping {filtered_file} due to unknown animal ID.")
                continue

            match = re.search(r"trial(\d)|t(\d)", filtered_file)
            if match:
                trial = match.group(1) or match.group(2)
            else:
                logging.info(f"Skipping {filtered_file} due to unknown trial number.")
                continue

            match = re.search(r"d\d{3}", filtered_file)
            if match:
                day = match.group()
            else:
                logging.info(f"Skipping {filtered_file} due to unknown day.")
                continue

            untouched_folder = os.path.join(untouched_base_folder, animal, day, "trial_" + trial, stimulation)
            output_folder = os.path.join(output_base_folder, animal, day, "trial_" + trial, stimulation)

            df_filtered, total_pupil_points = extract_averaged_pupil_diameters(filtered_file_path)

            # Add averaged pupil diameter ratios to the untouched CSV files and save them to the output folder
            if df_filtered is not None:
                add_pupil_diameters_to_untouched(untouched_folder, df_filtered, total_pupil_points, output_folder)

# Example usage
filtered_folder = r"C:\Users\ASH213\Documents\Pupil activity\890"
untouched_base_folder = r"C:\Users\ASH213\Documents\Calcium activity"
output_base_folder = r"C:\Users\ASH213\Documents\Correlated"

process_folders(filtered_folder, untouched_base_folder, output_base_folder)
