import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from mpl_toolkits.mplot3d import Axes3D
def load_data(file_path):
    """
    Load data from a JSON file and convert it into a DataFrame.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_graphs_from_data(file_path):
    # Extract participant ID and date from the filename
    base_name = os.path.basename(file_path)
    parts = base_name.split('_')
    if len(parts) >= 3:
        participant_id = parts[1]
        date = parts[2].split('.')[0]  # Assuming the date is before the .json extension
    else:
        participant_id = 'Unknown'
        date = 'UnknownDate'
    directory = create_directory(participant_id)

    data = load_data(file_path)
    plot_combined_data(data, participant_id, date, directory)
    plot_level_duration(data, participant_id, date, directory)

def create_directory(participant_id):
    """
    Create a directory for the participant if it doesn't exist.
    """
    directory = os.path.join('participants', participant_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def plot_combined_data(data, participant_id, date, directory):
    """
    Plot headpose, rotation, and controller data in a single image for each level condition.
    """
    df = pd.DataFrame(data['experimentDataList'])
    df_levels = pd.DataFrame(data['levelDataList'])

    # Extract head position data
    df['HeadPosX'] = df['HeadposeData'].apply(lambda x: x['Position']['x'])
    df['HeadPosY'] = df['HeadposeData'].apply(lambda x: x['Position']['y'])
    df['HeadPosZ'] = df['HeadposeData'].apply(lambda x: x['Position']['z'])

    # Extract controller position data
    df['ControllerPosX'] = df['ControllerData'].apply(lambda x: x['Position']['x'])
    df['ControllerPosY'] = df['ControllerData'].apply(lambda x: x['Position']['y'])
    df['ControllerPosZ'] = df['ControllerData'].apply(lambda x: x['Position']['z'])

    # Create subplots
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 5))

    # Plotting head position
    axes[0].plot(df['Timestamp'], df['HeadPosX'], label='X')
    axes[0].plot(df['Timestamp'], df['HeadPosY'], label='Y')
    axes[0].plot(df['Timestamp'], df['HeadPosZ'], label='Z')
    axes[0].set_title('Head Position')
    axes[0].legend()

    # Plotting controller position
    axes[1].plot(df['Timestamp'], df['ControllerPosX'], label='X')
    axes[1].plot(df['Timestamp'], df['ControllerPosY'], label='Y')
    axes[1].plot(df['Timestamp'], df['ControllerPosZ'], label='Z')
    axes[1].set_title('Controller Position')
    axes[1].legend()

    # Add plots for rotation data if available
    # Example for head rotation (assuming it's in Euler angles)
    if 'Rotation' in df['HeadposeData'][0]:
        df['HeadRotX'] = df['HeadposeData'].apply(lambda x: x['Rotation']['x'])
        df['HeadRotY'] = df['HeadposeData'].apply(lambda x: x['Rotation']['y'])
        df['HeadRotZ'] = df['HeadposeData'].apply(lambda x: x['Rotation']['z'])

        axes[2].plot(df['Timestamp'], df['HeadRotX'], label='X')
        axes[2].plot(df['Timestamp'], df['HeadRotY'], label='Y')
        axes[2].plot(df['Timestamp'], df['HeadRotZ'], label='Z')
        axes[2].set_title('Head Rotation')
        axes[2].legend()

    df_levels['Duration'] = df_levels['EndTime'] - df_levels['StartTime']
    df_levels['LevelName'] = df_levels.apply(lambda row: row['LevelType'] + ('_Tandem' if row['IsTandem'] else '_Solo'),
                                             axis=1)
    df_levels.groupby('LevelName')['Duration'].mean().plot(kind='bar', ax=axes[3])
    axes[3].set_title('Average Level Duration')
    axes[3].set_xlabel('Level Name')
    axes[3].set_ylabel('Duration (seconds)')

    plt.tight_layout()
    plt.savefig(os.path.join(directory, f'{participant_id}_{date}_CombinedData.png'))



def plot_level_duration(data, participant_id, date, directory):
    """
    Compare and visualize level duration for levels with 'reverse' in their name versus those that do not,
    and save the statistics to a CSV file.
    """
    df = pd.DataFrame(data['levelDataList'])
    df['Duration'] = df['EndTime'] - df['StartTime']
    df['IsReverse'] = df['LevelType'].str.contains('reverse', case=False, na=False)

    # Separate the durations into reverse and non-reverse
    reverse_durations = df[df['IsReverse']]['Duration']
    non_reverse_durations = df[~df['IsReverse']]['Duration']

    # Calculate summary statistics
    reverse_summary = reverse_durations.describe()
    non_reverse_summary = non_reverse_durations.describe()

    # Combine the summaries into a single DataFrame
    summary_df = pd.DataFrame({
        'Reverse': reverse_summary,
        'Non-Reverse': non_reverse_summary
    })

    # Save the summary statistics to a CSV file
    summary_csv_path = os.path.join('participants', f'{participant_id}_level_duration_stats.csv')
    summary_df.to_csv(summary_csv_path)

    # Perform a t-test
    t_stat, p_value = stats.ttest_ind(reverse_durations, non_reverse_durations, equal_var=False)

    # Visualization with boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='IsReverse', y='Duration', data=df)
    plt.title(f'Level Duration: Reverse vs. Non-Reverse for {participant_id}')
    plt.xlabel('Level Type (True for Reverse, False for Non-Reverse)')
    plt.ylabel('Duration (seconds)')

    # Save the figure
    plt.savefig(os.path.join(directory, f'{participant_id}_{date}_LevelDurationComparison.png'))

    # Print the summary statistics and t-test results
    print(f"Summary Statistics for Reverse Levels:\n{reverse_summary}")
    print(f"Summary Statistics for Non-Reverse Levels:\n{non_reverse_summary}")
    print(f"T-test results: t-statistic = {t_stat}, p-value = {p_value}")

    # Return the statistics and p-value for further use if necessary
    return reverse_summary, non_reverse_summary, t_stat, p_value


def generate_master_stats_file(directory):
    """
    Generate a master CSV file that compiles statistics from all participants.
    """
    master_stats_list = []

    # Check if directory exists
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('_level_duration_stats.csv'):
            file_path = os.path.join(directory, filename)
            print(f"Reading stats from {file_path}")
            try:
                participant_stats = pd.read_csv(file_path)
                participant_id = filename.split('_')[0]
                participant_stats['ParticipantID'] = participant_id
                master_stats_list.append(participant_stats)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Ensure there are dataframes to concatenate
    if not master_stats_list:
        print("No stats files found to concatenate.")
        return

    # Combine all the participant stats into a single DataFrame
    master_stats_df = pd.concat(master_stats_list, ignore_index=True)

    # Save the master DataFrame to a CSV file
    master_csv_path = os.path.join(directory, 'master_level_duration_stats.csv')
    master_stats_df.to_csv(master_csv_path, index=False)
    print(f"Master stats CSV file saved to: {master_csv_path}")

    transform_master_stats(master_csv_path)



# Add a call to generate_master_stats_file at the end of process_all_json_files
def process_all_json_files(directory):
    """
    Process all JSON files in the given directory and generate a master stats file.
    """
    directory = os.path.expanduser(directory)

    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(f"Processing file: {file_path}")
            generate_graphs_from_data(file_path)

    # After all files have been processed, generate the master stats file
    participants_directory = 'participants'  # This points to the 'participants' folder in the script's directory
    generate_master_stats_file(participants_directory)

def transform_master_stats(master_csv_path):
    """
    Transforms the master stats CSV file to a more human-readable format.
    """
    # Load the master stats file
    df = pd.read_csv(master_csv_path)

    # Pivot the DataFrame

    if df.duplicated(subset=['ParticipantID', 'Unnamed: 0']).any():
        print("Duplicate entries found. Handling duplicates...")
        # Handling duplicates - this could be as simple as dropping them or more complex logic
        df = df.drop_duplicates(subset=['ParticipantID', 'Unnamed: 0'])


    df_pivoted = df.pivot(index='ParticipantID', columns='Unnamed: 0')
    df_pivoted.columns = ['_'.join(col).strip() for col in df_pivoted.columns.values]
    df_pivoted.reset_index(inplace=True)

    # Rename columns for better understanding
    column_renames = {
        'ParticipantID': 'Participant ID',
        'count_Reverse': 'Reverse Count',
        'mean_Reverse': 'Reverse Mean Duration (sec)',
        'std_Reverse': 'Reverse Std. Deviation (sec)',
        'min_Reverse': 'Reverse Min Duration (sec)',
        '25%_Reverse': 'Reverse 25th Percentile Duration (sec)',
        '50%_Reverse': 'Reverse Median Duration (sec)',
        '75%_Reverse': 'Reverse 75th Percentile Duration (sec)',
        'count_Non-Reverse': 'Non-Reverse Count',
        'mean_Non-Reverse': 'Non-Reverse Mean Duration (sec)',
        'std_Non-Reverse': 'Non-Reverse Std. Deviation (sec)',
        'min_Non-Reverse': 'Non-Reverse Min Duration (sec)',
        '25%_Non-Reverse': 'Non-Reverse 25th Percentile Duration (sec)',
        '50%_Non-Reverse': 'Non-Reverse Median Duration (sec)',
        '75%_Non-Reverse': 'Non-Reverse 75th Percentile Duration (sec)'
    }
    df_pivoted.rename(columns=column_renames, inplace=True)

    # Save the transformed DataFrame to a new CSV file
    transformed_csv_path = master_csv_path.replace('.csv', '_transformed.csv')
    df_pivoted.to_csv(transformed_csv_path, index=False)

    print(f"Transformed master stats CSV file saved to: {transformed_csv_path}")
    return df_pivoted


# Usage
directory_path = '~/MagicLeap/downloads/'
process_all_json_files(directory_path)
