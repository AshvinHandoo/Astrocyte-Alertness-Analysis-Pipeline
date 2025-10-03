import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def process_file(file_path):
    # Load the data from the CSV file
    data = pd.read_csv(file_path)

    # Extract the relevant columns
    pupil_diameter = data['Pupil Diameter Ratio'].values
    calcium_activity = data['calcium'].values

    # Define the segment ranges (bins)
    segment_ranges = [(i, i + 100) for i in range(0, 1200, 5)]
    max_correlations = []
    max_lags = []

    for start, end in segment_ranges:
        if end <= len(pupil_diameter) and end <= len(calcium_activity):
            pd_segment = pupil_diameter[start:end]
            ca_segment = calcium_activity[start:end]

            # Compute the cross-correlation for the segment
            correlation = np.correlate(pd_segment - np.mean(pd_segment), ca_segment - np.mean(ca_segment), mode='full')
            lag = np.argmax(correlation) - (len(pd_segment) - 1)

            # Record the maximum correlation value and its lag
            max_correlation = np.max(correlation)
            max_correlations.append(max_correlation)
            max_lags.append(lag)

    return list(range(0, 1200, 5))[:len(max_correlations)], max_correlations, max_lags, pupil_diameter

def assign_color(lag):
    if lag >= -5 and lag <= 5:
        return 'blue'
    elif lag > 5 and lag <= 20:
        return 'lightcoral'
    elif lag > 20 and lag <= 50:
        return 'red'
    elif lag > 50:
        return 'darkred'
    elif lag < -50:
        return 'darkgreen'
    elif lag < -20:
        return 'green'
    elif lag < -5:
        return 'lightgreen'
    else:
        return 'black'  # Default color, should not occur with above conditions

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    stimconditions = ['stimcondition_1', 'stimcondition_2', 'stimcondition_3', 'stimcondition_4', 'stimcondition_5']
    trial_folders = [f'trial_{i}' for i in range(1, 4)]

    for stimcondition in stimconditions:
        all_max_correlations = []
        all_max_lags = []
        all_pupil_diameter_ratios = []

        for trial_folder in trial_folders:
            trial_path = os.path.join(input_folder, trial_folder, stimcondition)
            if os.path.exists(trial_path):
                for filename in os.listdir(trial_path):
                    if filename == 'bindist_2000.csv':
                        file_path = os.path.join(trial_path, filename)
                        segment_lengths, max_correlations, max_lags, pupil_diameter = process_file(file_path)
                        all_max_correlations.append(max_correlations)
                        all_max_lags.append(max_lags)
                        all_pupil_diameter_ratios.append(pupil_diameter)

        if all_max_correlations:
            # Convert all_max_correlations and all_pupil_diameter_ratios to numpy arrays and handle different lengths
            all_max_correlations = [np.array(corr) for corr in all_max_correlations]
            all_max_lags = [np.array(lag) for lag in all_max_lags]
            all_pupil_diameter_ratios = [np.array(pd) for pd in all_pupil_diameter_ratios]
            min_length = min(len(corr) for corr in all_max_correlations)
            all_max_correlations = np.array([corr[:min_length] for corr in all_max_correlations])
            all_max_lags = np.array([lag[:min_length] for lag in all_max_lags])
            min_length_pd = min(len(pd) for pd in all_pupil_diameter_ratios)
            all_pupil_diameter_ratios = np.array([pd[:min_length_pd] for pd in all_pupil_diameter_ratios])

            # Average the max correlations, lags, and pupil diameter ratios for each segment length
            avg_max_correlations = np.mean(all_max_correlations, axis=0)
            avg_max_lags = np.mean(all_max_lags, axis=0)
            avg_pupil_diameter_ratios = np.mean(all_pupil_diameter_ratios, axis=0)

            # Truncate segment_lengths to match avg_max_correlations
            segment_lengths = segment_lengths[:len(avg_max_correlations)]

            # Assign colors based on average max lags
            colors = [assign_color(lag) for lag in avg_max_lags]

            # Plot the average maximum cross-correlation for each segment length
            plt.figure(figsize=(10, 10))

            plt.subplot(2, 1, 1)
            plt.scatter(segment_lengths, avg_max_correlations, c=colors)
            plt.axvline(x=300, color='red', linestyle='--')
            plt.axvline(x=601, color='red', linestyle='--')
            plt.xlabel('Segment Start (points)')
            plt.ylabel('Maximum Cross-correlation')
            plt.title(f'Average Maximum Cross-correlation for {stimcondition}')
            plt.grid(True)

            # Plot the average pupil diameter ratio for each segment length
            plt.subplot(2, 1, 2)
            plt.plot(range(len(avg_pupil_diameter_ratios)), avg_pupil_diameter_ratios, color='blue')
            plt.axvline(x=300, color='red', linestyle='--')
            plt.axvline(x=601, color='red', linestyle='--')
            plt.xlabel('Time (points)')
            plt.ylabel('Average Pupil Diameter Ratio')
            plt.title(f'Average Pupil Diameter Ratio for {stimcondition}')
            plt.grid(True)

            # Save the plot
            plot_filename = os.path.join(output_folder, f'{stimcondition}_average_max_cross_correlation_and_pupil_diameter.png')
            plt.tight_layout()
            plt.savefig(plot_filename)
            plt.close()

            print(f"Processed {stimcondition}. The average maximum cross-correlation and pupil diameter ratio plot has been saved.")

input_folder = r'C:\Users\ASH213\Documents\Correlated\890\d084'
output_folder = r'C:\Users\ASH213\Documents\Correlated\890\d084\bin_cross_correlations'

# Process all relevant files and create averaged maximum cross-correlation graphs
process_folder(input_folder, output_folder)
