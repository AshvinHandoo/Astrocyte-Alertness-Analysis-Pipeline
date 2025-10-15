import os
import pandas as pd
import re
import numpy as np

def create_file_dictionary(folder_path1):
    file_dict = {}

    # Walk through the folder
    for root, dirs, files in os.walk(folder_path1):
        for file in files:
            # Remove file extension
            file_without_extension = os.path.splitext(file)[0]
            # Get the full file path
            file_path = os.path.join(root, file)
            # Add to the dictionary
            file_dict[file_without_extension] = file_path

    return file_dict

# Specify the folder path for bad pupil videos
folder_path1 = r"D:\Bad pupil vids"

# Create the file dictionary
file_dict = create_file_dictionary(folder_path1)

# Folder containing CSV files
folder_path = r"C:\Users\ASH213\Documents\Pupil activity"

# Output directory for processed CSV files
output_dir = r"C:\Users\ASH213\Documents\Pupil activity\890"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Iterate over each CSV file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        # Remove file extension from the CSV filename
        csv_file_without_extension = os.path.splitext(file_name)[0]

        # Check if the CSV filename (or part of it) is in the bad pupil videos dictionary
        skip_file = any(bad_file in csv_file_without_extension for bad_file in file_dict)
        if skip_file:
            print(f"Skipping bad video: {file_name}")
            continue

        # Path to the CSV file
        csv_file_path = os.path.join(folder_path, file_name)

        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(csv_file_path, header=[0, 1, 2])

        # Extract frame numbers and pupil diameters
        frame_numbers = df[('scorer', 'bodyparts', 'coords')].values
        bot_pupils = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Bot pupil', 'y')]
        top_pupils = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Top pupil', 'y')]
        left_pupilsx = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Left pupil', 'x')]
        left_pupilsy = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Left pupil', 'y')]
        right_pupilsx = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Right pupil', 'x')]
        right_pupilsy = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Right pupil', 'y')]
        left_cornerx = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Left corner of eye', 'x')]
        left_cornery = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Left corner of eye', 'y')]
        right_cornerx = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Right corner of eye', 'x')]
        right_cornery = df[('DLC_resnet101_Pupil DialationMay1shuffle1_100000', 'Right corner of eye', 'y')]

        # Debug print to check extracted data
        print(f"File: {file_name}")
        print(f"Left corner x: {left_cornerx.head()}")
        print(f"Left corner y: {left_cornery.head()}")
        print(f"Right corner x: {right_cornerx.head()}")
        print(f"Right corner y: {right_cornery.head()}")

        # Calculate pupil diameter
        pupil_diameters = np.sqrt((right_pupilsx - left_pupilsx)**2 + (right_pupilsy - left_pupilsy)**2)
        eye_gap = np.sqrt((right_cornerx - left_cornerx)**2 + (right_cornery - left_cornery)**2)

        # Debug print to check calculations
        print(f"Pupil diameters: {pupil_diameters.head()}")
        print(f"Eye gap: {eye_gap.head()}")

        # Determine imaging type
        imaging = '2p' if '2p' in file_name else 'MVX'

        # Determine stimulation type
        if 'burst' in file_name:
            stimulation = '10Hz burst'
        elif '10Hz' in file_name:
            stimulation = '10Hz'
        elif '100Hz' in file_name:
            stimulation = '100Hz'
        elif 'tbs' in file_name:
            stimulation = 'tbs'
        elif 'vstim' in file_name:
            stimulation = 'vstim'
        elif 'line' in file_name:
            stimulation = 'baseline'
        else:
            stimulation = 'NA'

        # Determine animal sex
        sex = 'male' if 'm1' in file_name else ('female' if 'f1' in file_name else 'NA')

        # Extract name from file name
        name = file_name.split('_')[0]

        # Extract trial number from file name
        match = re.search(r"trial(\d)|t(\d)", file_name)
        trial = match.group(1) or match.group(2) if match else 'NA'

        # Extract site number from file name
        match = re.search(r"site(\d)", file_name)
        site = match.group(1) if match else 'NA'

        # Create table data for current file
        table_data = [['Name', 'Sex', 'Imaging', 'Site', 'Stimulation', 'Trial', "Frame number", "Pupil Diameter", 'Eye gap', 'Calcium Activity'],
                      [name, sex, imaging, site, stimulation, trial, '', '', '', '']]
        for frame_number, pupil_diameter, gap in zip(frame_numbers, pupil_diameters, eye_gap):
            table_data.append(['', '', '', '', '', '', frame_number, pupil_diameter, gap, ''])

        # Create a DataFrame from the collected data for the current file
        df_current = pd.DataFrame(table_data[1:], columns=table_data[0])

        # Save the DataFrame to a CSV file
        output_csv_path = os.path.join(output_dir, f'{csv_file_without_extension}_processed.csv')
        df_current.to_csv(output_csv_path, index=False)
        print(f"DataFrame saved to: {output_csv_path}")

print("All files processed and saved.")
