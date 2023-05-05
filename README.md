# Folder sync script

## Assignment
Please implement a program in Python that synchronizes two folders: source and replica.
The program should maintain a full, identical copy of source folder at replica folder.

Synchronization must be one-way: after the synchronization content of the
replica folder should be modified to exactly match content of the source
folder.\
Synchronization should be performed periodically.\
File creation/copying/removal operations should be logged to a file and to the
console output.\
Folder paths, synchronization interval and log file path should be provided
using the command line arguments.\
It is undesirable to use third-party libraries that implement folder
synchronization.\
It is allowed (and recommended) to use external libraries implementing other
well-known algorithms. For example, there is no point in implementing yet
another function that calculates MD5 if you need it for the task - it is
perfectly acceptable to use a third-party (or built-in) library.

## Usage:
To use this program , you can run the script from the command line with the following arguments:

python main.py --log_file log_file_path [--log_level log_level] source_folder_path replica_folder_path interval

### Where:

source_folder_path - is the path to the source folder that you want to synchronize.\
replica_folder_path - is the path to the replica folder that you want to synchronize with the source folder.\
interval - is the number of seconds between synchronizations.\
log_file_path - is the path to the log file that you want to write to.\
log_level (optional) - is the level of logging to use (e.g. DEBUG, INFO, WARNING, ERROR). If not specified, the default log level is INFO.

### For example:

To synchronize the contents of a source folder /path/to/source/folder with a replica folder /path/to/replica/folder every 60 seconds, with log output written to /path/to/logfile.log, you can run:

python main.py /path/to/source/folder /path/to/replica/folder 60 /path/to/logfile.log

## Requirements:

This program requires Python 3.6 or higher, and the following Python packages:

os\
hashlib\
logging\
argparse\
time
