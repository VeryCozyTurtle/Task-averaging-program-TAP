import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import filedialog
import matplotlib.colors as mcolors
import numpy as np

# Define RGB values for High, Medium, and Low
color_h = (1, 0, 0)
color_m = (0, 0, 1)
color_l = (0, 1, 0)

# Let the user choose a .TAP file for visualization
file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.TAP")])

# Check if a file was selected or if the dialog was canceled
if not file_path:
    print("No file selected. Exiting...")
else:
    # Lists to store the data
    times = []  # Store the task times

    # Open the selected file for reading
    with open(file_path, 'r') as file:
        for line in file:
            date_str, time_str = line.strip().split()
            current_datetime = datetime.strptime(date_str + ' ' + time_str, '%Y-%m-%d %H:%M:%S')
            times.append(current_datetime)

    # Calculate the time differences and create the task_colors list
    if len(times) > 1:
        time_diffs = [(times[i] - times[i - 1]).total_seconds() / 60 for i in range(1, len(times))]

        global_avg_time = sum(time_diffs) / len(time_diffs)

        # Calculate the standard deviation of time_diffs
        std_deviation = np.std(time_diffs)

        # Scale deviations
        scaled_deviations = [(time_diff - global_avg_time) / (std_deviation) for time_diff in time_diffs]

        # Normalize scaled deviations between 0 and 1
        min_deviation = min(scaled_deviations)
        max_deviation = max(scaled_deviations)
        normalized_deviations = [(deviation - min_deviation) / (max_deviation - min_deviation) for deviation in scaled_deviations]

        # Calculate the color points based on data distribution
        percentile_25 = np.percentile(normalized_deviations, 5)
        percentile_75 = np.percentile(normalized_deviations, 95)

        # Calculate the new color points
        color_point_low = min(normalized_deviations)
        color_point_mid = (percentile_25 + percentile_75) / 2
        color_point_high = max(normalized_deviations)

        # Define color points and corresponding colors
        color_points = [color_point_low, color_point_mid, color_point_high]

        # Create a custom colormap using LinearSegmentedColormap
        custom_colormap = mcolors.LinearSegmentedColormap.from_list("Custom", list(zip(color_points, [color_l, color_m, color_h])))

        # Create a list of unique dates
        unique_dates = sorted(set([time.date() for time in times]))

        # Plot tasks with color-coded gradients
        for i, time in enumerate(times[1:]):  # Start from the second task
            date = time.date()
            y_level = unique_dates.index(date)  # Adjusted the y-level calculation

            # Calculate the x-position in hours
            x_position = (time - datetime.combine(date, datetime.min.time())).total_seconds() / 3600

            plt.scatter(x_position, y_level, c=[custom_colormap(normalized_deviations[i])], marker='D', edgecolors='none')

        # Set the plot title with the file name minus the '.TAP' extension
        file_name = file_path.split("/")[-1].split(".TAP")[0]
        plt.title(file_name)
        plt.gcf().set_facecolor('lightgrey')
        ax = plt.gca()
        ax.set_facecolor('lightgrey')

        # Label the axes and adjust the y-axis
        plt.xlabel('Time of Day')
        plt.ylabel('Day')
        plt.xticks(range(0, 25), [f'{int(x)}:{int((x % 1) * 60):02d}' for x in range(0, 25)])
        plt.yticks(range(len(unique_dates)), [date.strftime('%Y-%m-%d') for date in unique_dates])
        plt.grid(True)
        plt.gca().format_coord = lambda x, y: f'Time: {unique_dates[int(y)].strftime("%Y-%m-%d")} {int(x)}:{int((x % 1) * 60):02d}'

        # Display the global average time
        plt.text(0.5, -0.1, f"Average Time Between events: {int(global_avg_time)} minutes", transform=ax.transAxes, fontsize=12, ha='center', va='center', color='blue')

    else:
        plt.text(0.5, -0.1, "No tasks recorded.", transform=ax.transAxes, fontsize=12, ha='center', va='center', color='blue')

    plt.show()
