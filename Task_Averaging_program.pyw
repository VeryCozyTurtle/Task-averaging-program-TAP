import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timedelta
import os

class TimeLogger:
    def __init__(self, root):
        self.window = root
        self.log_filename = self.select_file()

        self.window.title("T.A.P")

        self.log_button = tk.Button(self.window, text=f"{os.path.basename(self.log_filename).replace('.TAP', '')}", command=self.log_time)
        self.log_button.pack()

        self.prev_time = None
        self.total_time = 0
        self.num_presses = 0

        self.average_label = tk.Label(self.window, text="Average: N/A")
        self.average_label.pack()

        self.elapsed_time_var = tk.StringVar()
        self.elapsed_time_label = tk.Label(self.window, textvariable=self.elapsed_time_var)
        self.elapsed_time_label.pack()

        # Load an existing log file if it exists
        self.load_existing_log()
        self.update_elapsed_time()  # Initialize the elapsed time


    def select_file(self):
        log_filename = filedialog.askopenfilename(defaultextension=".TAP", filetypes=[("Text Files", "*.TAP")])
        if not log_filename:
            log_filename = "log.TAP"
        return log_filename

    def load_existing_log(self):
        try:
            with open(self.log_filename, 'r') as log_file:
                lines = log_file.readlines()
                if lines:
                    self.num_presses = len(lines)
                    start_time = datetime.strptime(lines[0].strip(), "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.strptime(lines[-1].strip(), "%Y-%m-%d %H:%M:%S")
                    self.total_time = (end_time - start_time).total_seconds()
                    average_time = self.total_time / self.num_presses
                    average_time_str = str(datetime.utcfromtimestamp(average_time).strftime('%H:%M:%S'))
                    self.average_label.config(text=f"Average: {average_time_str}")
        except FileNotFoundError:
            pass

    def update_elapsed_time(self):
        current_time = datetime.now()
        elapsed_time = current_time - (self.prev_time if self.prev_time else current_time)
        elapsed_time_str = str(elapsed_time).split('.')[0]  # Remove microseconds
        self.elapsed_time_var.set(elapsed_time_str)
        self.window.after(1000, self.update_elapsed_time)  # Update elapsed time every second

    def log_time(self):
        current_time = datetime.now()
        if self.prev_time:
            time_diff = current_time - self.prev_time
            self.total_time += time_diff.total_seconds()
            self.num_presses += 1
            average_time = self.total_time / self.num_presses

            # Format the average_time as 'hh:mm:ss'
            average_time_str = str(datetime.utcfromtimestamp(average_time).strftime('%H:%M:%S'))
            self.average_label.config(text=f"Running Average: {average_time_str}")

        self.prev_time = current_time
        self.update_elapsed_time()  # Update the elapsed time
        self.elapsed_time_var.set("00:00:00")  # Reset elapsed time

        with open(self.log_filename, 'a') as log_file:
            log_file.write(current_time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    root.attributes('-topmost', True)  # Keep the window on top
    logger = TimeLogger(root)
    logger.run()