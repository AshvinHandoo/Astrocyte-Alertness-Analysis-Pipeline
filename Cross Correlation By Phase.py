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

    # Define the segments with correct indexing
    segments = [(0, 299), (299, 598), (598, 898), (898, 1198), (0, 1198)]
    correlations = []

    for start, end in segments:
        if end < len(pupil_diameter) and end < len(calcium_activity):
            pd_segment = pupil_diameter[start:end + 1]
            ca_segment = calcium_activity[start:end + 1]

            # Compute the cross-correlation for the segment
            correlation = np.correlate(pd_segment - np.mean(pd_segment), ca_segment - np.mean(ca_segment), mode='full')
            lags = np.arange(-len(pd_segment) + 1, len(pd_segment))

            correlations.append((lags, correlation))

    return correlations


def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    stimconditions = ['stimcondition_1', 'stimcondition_2', 'stimcondition_3', 'stimcondition_4', 'stimcondition_5']
    trial_folders = [f'trial_{i}' for i in range(1, 4)]

    segment_names = ['pre', 'stim', 'post-stim', 'post', 'overall']  # Adjust segment names as needed
    results = []

    for stimcondition in stimconditions:
        all_correlations = {i: [] for i in range(5)}  # Dictionary to hold correlations for each segment
        for trial_folder in trial_folders:
            trial_path = os.path.join(input_folder, trial_folder, stimcondition)
            if os.path.exists(trial_path):
                for filename in os.listdir(trial_path):
                    if filename == 'bindist_2000.csv':
                        file_path = os.path.join(trial_path, filename)
                        segment_correlations = process_file(file_path)
                        for i, (lags, correlation) in enumerate(segment_correlations):
                            all_correlations[i].append(correlation)

        for i, segment in all_correlations.items():
            if segment:
                # Average the correlations for this segment
                avg_correlation = np.mean(segment, axis=0)

                # Get the lags from the first segment's lags (assuming all have the same length)
                lags = segment_correlations[i][0]

                # Find the max correlation and corresponding lag
                max_corr = np.max(avg_correlation)
                max_lag = lags[np.argmax(avg_correlation)]

                results.append(
                    f"{stimcondition} Segment {segment_names[i]}: Max Correlation = {max_corr}, Lag = {max_lag} samples")

                # Plot the average cross-correlation for this segment
                plt.figure(figsize=(10, 5))
                plt.plot(lags, avg_correlation)
                plt.xlabel('Lag (samples)')
                plt.ylabel('Cross-correlation')
                plt.title(f'Average Cross-correlation for {stimcondition} - Segment {segment_names[i]}')
                plt.axvline(max_lag, color='r', linestyle='--', label=f'Lag={max_lag:.1f} samples')
                plt.legend()

                # Save the plot
                plot_filename = os.path.join(output_folder,
                                             f'{stimcondition}_{segment_names[i]}_average_cross_correlation.png')
                plt.savefig(plot_filename)
                plt.close()

                print(
                    f"Processed {stimcondition} Segment {segment_names[i]}. The average cross-correlation plot has been saved.")

    # Write the results to a text file
    results_filename = os.path.join(output_folder, 'correlation_results.txt')
    with open(results_filename, 'w') as f:
        for result in results:
            f.write(result + '\n')


input_folder = r'C:\Users\ASH213\Documents\Correlated\890\d084'
output_folder = r'C:\Users\ASH213\Documents\Correlated\890\d084\average_cross_correlations'

# Process all relevant files and create averaged cross-correlation graphs
process_folder(input_folder, output_folder)
