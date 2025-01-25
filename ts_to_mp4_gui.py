import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import threading

current_process = None  # Global variable to hold the current subprocess
stop_flag = False  # Global flag to stop conversion

# Function to ensure unique output file name
def ensure_unique_filename(output_path):
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base}({counter}){ext}"
        counter += 1
    return output_path

# Function to convert a single .ts to .mp4 with size limit
def convert_ts_to_mp4_with_limit(input_path, output_base, progress_bar, status_label, size_limit, unit):
    global stop_flag, current_process
    try:
        part_number = 1
        start_time = 0  # Start time in seconds
        # Convert size limit to bytes based on the selected unit
        if unit == "GB":
            size_limit_bytes = size_limit * 1024 * 1024 * 1024
        elif unit == "MB":
            size_limit_bytes = size_limit * 1024 * 1024

        # Update status label to show current file being converted
        status_label.config(text=f"Converting: {os.path.basename(input_path)} - Part {part_number}")

        while True:
            output_path = f"{output_base}-part{part_number}.mp4"
            command = [
                "ffmpeg", "-ss", str(start_time), "-i", input_path, "-c:v", "copy", "-c:a", "aac",
                "-fs", str(size_limit_bytes), output_path
            ]
            current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)

            total_duration = None
            while True:
                if stop_flag:  # Handle stopping
                    current_process.terminate()
                    current_process = None
                    return

                output = current_process.stderr.readline()
                if current_process.poll() is not None:
                    break

                if output:
                    # Extract total duration from FFmpeg output
                    if "Duration" in output and total_duration is None:
                        duration_str = output.split("Duration: ")[1].split(",")[0]
                        h, m, s = map(float, duration_str.split(":"))
                        total_duration = int(h * 3600 + m * 60 + s)

                    # Extract progress information
                    if "time=" in output:
                        time_str = output.split("time=")[1].split(" ")[0]
                        h, m, s = map(float, time_str.split(":"))
                        elapsed_time = int(h * 3600 + m * 60 + s)

                        if total_duration:
                            progress = int((elapsed_time / total_duration) * 100)
                            progress_bar["value"] = progress

            if current_process.returncode == 0:  # Check if the process ended successfully
                # Get the duration of the current output file
                duration_command = [
                    "ffprobe", "-i", output_path, "-show_entries", "format=duration",
                    "-v", "quiet", "-of", "csv=p=0"
                ]
                duration_process = subprocess.run(duration_command, stdout=subprocess.PIPE, text=True)
                duration = float(duration_process.stdout.strip())
                start_time += duration  # Update start time for the next part

                # Check file size and decide whether to continue
                if os.path.getsize(output_path) >= size_limit_bytes:
                    part_number += 1
                    status_label.config(text=f"Converting: {os.path.basename(input_path)} - Part {part_number}")
                else:
                    break

    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
    finally:
        current_process = None
        status_label.config(text="")  # Clear status label after completion

# Function to handle file-by-file conversion
def convert_files():
    global stop_flag
    disable_interface()
    success_count = 0

    try:
        size_limit = float(size_limit_entry.get())  # Get size limit from entry
        unit = size_unit_var.get()  # Get selected unit (GB or MB)
    except ValueError:
        messagebox.showerror("Error", "Invalid size limit value.")
        enable_interface()
        return

    for input_file in list(file_listbox.get(0, tk.END)):
        base_name = os.path.basename(input_file).rsplit(".", 1)[0]
        timestamp = time.strftime("%Y%m%d-%H%M")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_base = os.path.join(output_dir, f"{base_name}-{timestamp}")

        progress_bar["value"] = 0
        convert_ts_to_mp4_with_limit(input_file, output_base, progress_bar, status_label, size_limit, unit)

        # Remove the processed file from the input list
        file_listbox.delete(0)

        if stop_flag:
            break

        success_count += 1

    stop_flag = False
    enable_interface()

    if not stop_flag:
        messagebox.showinfo("Done", f"All conversions completed. {success_count} files were successfully converted.")

# Function to select input files
def select_input_files():
    files = filedialog.askopenfilenames(filetypes=[("TS Files", "*.ts")])
    if files:
        file_listbox.delete(0, tk.END)
        for file in files:
            file_listbox.insert(tk.END, file)

        if len(files) == 1:
            base_name = os.path.basename(files[0]).rsplit(".", 1)[0]
            timestamp = time.strftime("%Y%m%d-%H%M")
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            default_output = os.path.join(output_dir, f"{base_name}-{timestamp}.mp4")
            output_entry.config(state=tk.NORMAL)
            output_entry.delete(0, tk.END)
            output_entry.insert(0, default_output)
        else:
            output_entry.config(state=tk.DISABLED)

# Function to remove selected files from the input list
def remove_selected_files():
    selected_indices = file_listbox.curselection()
    for index in reversed(selected_indices):
        file_listbox.delete(index)

# Function to start conversion
def start_conversion():
    global stop_flag
    stop_flag = False
    if file_listbox.size() == 0:
        messagebox.showwarning("Warning", "Please select input files.")
        return

    # Run the conversion in a separate thread
    threading.Thread(target=convert_files, daemon=True).start()

# Function to stop the current process
def stop_conversion():
    global stop_flag, current_process
    stop_flag = True
    if current_process:
        current_process.terminate()
        current_process = None

# Function to disable the interface
def disable_interface():
    file_listbox.config(state=tk.DISABLED)
    input_button.config(state=tk.DISABLED)
    remove_button.config(state=tk.DISABLED)
    convert_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

# Function to enable the interface
def enable_interface():
    file_listbox.config(state=tk.NORMAL)
    input_button.config(state=tk.NORMAL)
    remove_button.config(state=tk.NORMAL)
    convert_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("TS to MP4 Converter")
root.geometry("800x800")
root.configure(bg="#f8f9fa")

# Header
header_label = tk.Label(root, text="TS to MP4 Converter", font=("Arial", 20, "bold"), bg="#343a40", fg="#ffffff", pady=10)
header_label.pack(fill=tk.X)

# Input file selection
input_label = tk.Label(root, text="Input .ts Files:", font=("Arial", 12), bg="#f8f9fa")
input_label.pack(pady=5)

input_frame = tk.Frame(root, bg="#f8f9fa")
input_frame.pack(pady=5)

file_listbox = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, width=60, height=10, font=("Arial", 10))
file_listbox.pack(side=tk.LEFT, padx=5, pady=5)

scrollbar = tk.Scrollbar(input_frame, orient=tk.VERTICAL, command=file_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_listbox.config(yscrollcommand=scrollbar.set)

input_button = tk.Button(root, text="Browse", command=select_input_files, bg="#007bff", fg="white", font=("Arial", 10), relief="flat")
input_button.pack(pady=5)

remove_button = tk.Button(root, text="Remove Selected", command=remove_selected_files, bg="#dc3545", fg="white", font=("Arial", 10), relief="flat")
remove_button.pack(pady=5)

# Output file name (only for single file)
output_label = tk.Label(root, text="Output File Name (Single File):", font=("Arial", 12), bg="#f8f9fa")
output_label.pack(pady=5)

output_entry = tk.Entry(root, width=50, font=("Arial", 10), state=tk.DISABLED)
output_entry.pack(pady=5)

# Size limit input and unit selection
size_limit_label = tk.Label(root, text="Size Limit per Part:", font=("Arial", 12), bg="#f8f9fa")
size_limit_label.pack(pady=5)

size_limit_frame = tk.Frame(root, bg="#f8f9fa")
size_limit_frame.pack(pady=5)

size_limit_entry = tk.Entry(size_limit_frame, width=10, font=("Arial", 10))
size_limit_entry.insert(0, "1900")  # Default size limit is 1900MB
size_limit_entry.pack(side=tk.LEFT, padx=5)

size_unit_var = tk.StringVar(value="MB")
size_unit_menu = ttk.Combobox(size_limit_frame, textvariable=size_unit_var, values=["GB", "MB"], state="readonly", width=5)
size_unit_menu.pack(side=tk.LEFT)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=500)
progress_bar.pack(pady=10)

# Status label for current file
status_label = tk.Label(root, text="", font=("Arial", 12), bg="#f8f9fa", fg="#343a40")
status_label.pack(pady=5)

# Convert button
convert_button = tk.Button(root, text="Convert", command=start_conversion, bg="#28a745", fg="white", font=("Arial", 12), relief="flat", pady=5)
convert_button.pack(pady=10)

# Stop button
stop_button = tk.Button(root, text="Stop", command=stop_conversion, bg="#dc3545", fg="white", font=("Arial", 12), relief="flat", pady=5, state=tk.DISABLED)
stop_button.pack(pady=10)

# Footer
footer_label = tk.Label(root, text="Created by Ezzyloweell", font=("Arial", 8), bg="#f8f9fa", fg="#6c757d")
footer_label.pack(side=tk.BOTTOM, pady=10)

# Run the main loop
root.mainloop()
