"""Please implement a program in Python that synchronizes two folders: source and replica.
The program should maintain a full, identical copy of source folder at replica folder.

Synchronization must be one-way: after the synchronization content of the
replica folder should be modified to exactly match content of the source
folder.
Synchronization should be performed periodically.
File creation/copying/removal operations should be logged to a file and to the
console output.
Folder paths, synchronization interval and log file path should be provided
using the command line arguments.
It is undesirable to use third-party libraries that implement folder
synchronization.
It is allowed (and recommended) to use external libraries implementing other
well-known algorithms. For example, there is no point in implementing yet
another function that calculates MD5 if you need it for the task - it is
perfectly acceptable to use a third-party (or built-in) library."""

import argparse
import logging
import os
import shutil
import time
import hashlib

def sync_folders(source_path, replica_path):
    """
    Synchronize the contents of the source folder with the replica folder.

    The function walks through the source folder recursively and copies any new
    files or modified files to the corresponding location in the replica folder.
    If a file is deleted from the source folder, it is also deleted from the replica folder.
    The function also logs the details of file creation, deletion or modification.

    Args:
        source_path (str): Path to the source folder.
        replica_path (str): Path to the replica folder.

    Returns:
        None.
    """
    new_files_created = False   # variable to track if new files are created during synchronization

    # Walk through the source folder recursively and copy new or modified files
    for root, dirs, files in os.walk(source_path):
        replica_root = root.replace(source_path, replica_path)
        os.makedirs(replica_root, exist_ok=True)   # create the directory in replica folder if it doesn't exist

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            # Check if the replica file doesn't exist or is older than the source file
            if not os.path.exists(replica_file) or os.stat(source_file).st_mtime - os.stat(replica_file).st_mtime > 1:
                shutil.copy2(source_file, replica_file)   # copy the file from source to replica folder
                logging.info(f"File copied: {source_file} -> {replica_file}")   # log the file creation event
                print(f"File copied: {source_file} -> {replica_file}")   # print the file creation event to console
                new_files_created = True

    # Delete the file from replica folder if it is deleted from source folder
    for replica_root, dirs, files in os.walk(replica_path):
        source_root = replica_root.replace(replica_path, source_path)
        for file in files:
            source_file = os.path.join(source_root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)   # remove the file from replica folder
                logging.info(f"File removed: {replica_file}")   # log the file deletion event
                print(f"File removed: {replica_file}")   # print the file deletion event to console

    # If new files are created during synchronization, log the synchronization completion time
    if new_files_created:
        msg = f"Sync complete at {time.strftime('%Y.%m.%d %H:%M:%S')}"
        logging.info(msg)
        print(msg)

def get_folder_hash(folder):
    """
    Calculate the MD5 hash of a folder.

    Args:
        folder (str): Path to the folder to hash.

    Returns:
        str: The MD5 hash of the folder.
    """
    # Initialize an MD5 hash object
    hash = hashlib.md5()

    # Walk the directory tree and update the hash with the contents of each file
    for root, dirs, files in os.walk(folder):
        for file in files:
            with open(os.path.join(root, file), 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    hash.update(data)

    # Return the hexadecimal representation of the MD5 hash
    return hash.hexdigest()


def check_for_events(source_path, replica_path):
    """
    Check for events in the source and replica directories and sync them if necessary.

    Args:
        source_path (str): Path to the source directory.
        replica_path (str): Path to the replica directory.

    Returns:
        None
    """
    # Initialize a dictionary to store the events
    events = {'new_file': [], 'file_modified': [], 'file_removed': []}

    # Check for new files and modified files in the source directory
    for filename in os.listdir(source_path):
        file_path = os.path.join(source_path, filename)
        if os.path.isfile(file_path):
            if filename not in os.listdir(replica_path):
                # A new file has been created in the source directory
                logging.info(f"New file created: {file_path}")
                print(f"New file created: {file_path}")
                events['new_file'].append(filename)
            else:
                # Check if the file has been modified in the source directory
                source_mtime = os.path.getmtime(file_path)
                replica_mtime = os.path.getmtime(os.path.join(replica_path, filename))
                if source_mtime > replica_mtime:
                    logging.info(f"File modified: {file_path}")
                    print(f"File modified: {file_path}")
                    events['file_modified'].append(filename)

    # Check for removed files in the replica directory
    for filename in os.listdir(replica_path):
        file_path = os.path.join(replica_path, filename)
        if os.path.isfile(file_path):
            if filename not in os.listdir(source_path):
                events['file_removed'].append(filename)

    # If there are new, modified, or removed files, sync the directories and update the hash
    if events['new_file'] or events['file_modified'] or events['file_removed']:
        sync_folders(source_path, replica_path)
        source_hash = get_folder_hash(source_path)
        logging.info(f"Source hash: {source_hash}")

if __name__ == "__main__":
    # create an ArgumentParser object to parse command line arguments
    parser = argparse.ArgumentParser(description='Synchronize two folders.')

    # add arguments to the parser
    parser.add_argument('source_path', metavar='source_path', type=str, help='path to the source folder')
    parser.add_argument('replica_path', metavar='replica_path', type=str, help='path to the replica folder')
    parser.add_argument('interval', metavar='interval', type=int, help='synchronization interval in seconds')
    parser.add_argument('--log_file', metavar='log_file', type=str, help='path to the log file')
    parser.add_argument('--log_level', metavar='log_level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='logging level')

    # parse the arguments
    args = parser.parse_args()

    # create a dictionary of logging levels
    logging_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # assign values to variables based on the parsed arguments
    source_path = args.source_path
    replica_path = args.replica_path
    interval = args.interval
    log_file = args.log_file
    log_level = args.log_level

    # configure logging with the specified log file and level
    logging.basicConfig(filename=log_file, level=logging.INFO)

    # check if the interval argument is greater than 0, raise ValueError if not
    if args.interval == 0:
        raise ValueError('Interval argument must be greater than 0.')

    # print a message to indicate that the script is running and the synchronization interval
    print(f"The script for folder sync is running. Synchronizing every {interval} seconds.")

    # start an infinite loop to synchronize folders at the specified interval
    while True:

        # check for events (new, modified, or removed files) in the source and replica folders
        check_for_events(source_path, replica_path)

        # get the hash of the source and replica folders
        source_hash = get_folder_hash(source_path)
        replica_hash = get_folder_hash(replica_path)

        # if the hashes are not equal, copy files from source to replica folder
        if source_hash != replica_hash:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    replica_file = os.path.join(replica_path, os.path.relpath(source_file, source_path))
                    if os.path.exists(replica_file):
                        os.remove(replica_file)
                    os.makedirs(os.path.dirname(replica_file), exist_ok=True)
                    shutil.copyfile(source_file, replica_file)

        # log the synchronization event with the appropriate logging level
        if log_level == 'DEBUG':
            logging.debug("Sync complete at: {}".format(time.strftime('%Y.%m.%d %H:%M:%S')))
        else:
            logging.info("Folders synchronized at {}".format(time.strftime('%Y.%m.%d %H:%M:%S')))

        # wait for the specified interval before checking for events again
        time.sleep(interval)
