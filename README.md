TS to MP4 Converter

This project is a GUI-based tool to convert .ts video files to .mp4 format. It includes features such as multi-file selection, progress tracking, and splitting files into parts based on a specified size limit.

Features

Convert .ts files to .mp4 format.

Split output files into parts with user-defined size limits (in MB or GB).

Multi-file input support.

Progress bar and real-time status display for the current file and part being converted.

Ability to stop conversion at any time.

Option to remove selected input files before starting the conversion.

Requirements

Python 3.7 or later.

ffmpeg and ffprobe must be installed and added to your system's PATH.

The following Python libraries:

tkinter (built into Python for GUI applications)

subprocess (built into Python for handling system commands)

Installation

Clone the repository:

git clone https://github.com/bestbad77/tsToMp4-MultiConverter.git
cd ts-to-mp4-converter

Install Python dependencies:
This application does not require any additional external Python libraries to be installed. If required for extensions, you can manage dependencies via pip.

Install FFmpeg:
Download and install FFmpeg from the official website. Ensure that ffmpeg and ffprobe are added to your system's PATH.

Run the application:

python ts_to_mp4_gui.py

Usage

Add Input Files:

Click on the Browse button to select .ts files to convert.

Selected files will be displayed in a list.

Remove Files (Optional):

Use the Remove Selected button to delete files from the input list.

Set Size Limit:

Define the maximum size limit for each part of the output file in the Size Limit per Part section.

Select the unit (MB or GB) using the dropdown menu.

The default limit is 1900 MB.

Start Conversion:

Click on Convert to start the process.

The current file and part being processed will be displayed.

A progress bar will show the conversion progress.

Stop Conversion:

Click Stop to halt the ongoing process.

Output:

Converted files will be saved in an output folder in the application directory.

Files will be automatically split into parts if they exceed the specified size limit.

Building an Executable

To create a standalone executable file for the application:

Install pyinstaller:

pip install pyinstaller

Build the executable:

pyinstaller --onefile --windowed ts_to_mp4_gui.py

The generated executable will be located in the dist folder.

Notes

Ensure that ffmpeg is correctly configured and accessible via the command line.

For large files, the conversion process may take time depending on your system's performance.

License

This project is licensed under the MIT License.

Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes.