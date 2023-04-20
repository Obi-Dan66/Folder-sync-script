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
    new_files_created = False
    for root, dirs, files in os.walk(source_path):
        replica_root = root.replace(source_path, replica_path)
        os.makedirs(replica_root, exist_ok=True)

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file) or os.stat(source_file).st_mtime - os.stat(replica_file).st_mtime > 1:
                shutil.copy2(source_file, replica_file)
                logging.info(f"File copied: {source_file} -> {replica_file}")
                print(f"File copied: {source_file} -> {replica_file}")
                new_files_created = True

    for replica_root, dirs, files in os.walk(replica_path):
        source_root = replica_root.replace(replica_path, source_path)
        for file in files:
            source_file = os.path.join(source_root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"File removed: {replica_file}")
                print(f"File removed: {replica_file}")

    if new_files_created:
        msg = f"Sync complete at {time.strftime('%Y.%m.%d %H:%M:%S')}"
        logging.info(msg)
        print(msg)

def get_folder_hash(folder):
    hash = hashlib.md5()
    for root, dirs, files in os.walk(folder):
        for file in files:
            with open(os.path.join(root, file), 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    hash.update(data)
    return hash.hexdigest()

def check_for_events(source_path, replica_path):
    events = {'new_file': [], 'file_modified': [], 'file_removed': []}
    for filename in os.listdir(source_path):
        file_path = os.path.join(source_path, filename)
        if os.path.isfile(file_path):
            if filename not in os.listdir(replica_path):
                logging.info(f"New file created: {file_path}")
                print(f"New file created: {file_path}")
                events['new_file'].append(filename)
            else:
                source_mtime = os.path.getmtime(file_path)
                replica_mtime = os.path.getmtime(os.path.join(replica_path, filename))
                if source_mtime > replica_mtime:
                    logging.info(f"File modified: {file_path}")
                    print(f"File modified: {file_path}")
                    events['file_modified'].append(filename)

    for filename in os.listdir(replica_path):
        file_path = os.path.join(replica_path, filename)
        if os.path.isfile(file_path):
            if filename not in os.listdir(source_path):
                events['file_removed'].append(filename)

    if events['new_file'] or events['file_modified'] or events['file_removed']:
        sync_folders(source_path, replica_path)
        source_hash = get_folder_hash(source_path)
        logging.info(f"Source hash: {source_hash}")
#  default='./source',
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('source_path', metavar='source_path', type=str, help='path to the source folder')
    parser.add_argument('replica_path', metavar='replica_path', type=str, help='path to the replica folder')
    parser.add_argument('interval', metavar='interval', type=int, help='synchronization interval in seconds')
    parser.add_argument('--log_file', metavar='log_file', type=str, help='path to the log file')
    parser.add_argument('--log_level', metavar='log_level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='logging level')
    args = parser.parse_args()

    logging_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    source_path = args.source_path
    replica_path = args.replica_path
    interval = args.interval
    log_file = args.log_file
    log_level = args.log_level

    logging.basicConfig(filename=log_file, level=logging.INFO)

    if args.interval == 0:
        raise ValueError('Interval argument must be greater than 0.')
    print(f"The script for folder sync is running. Synchronizing every {interval} seconds.")
    while True:

        check_for_events(source_path, replica_path)

        source_hash = get_folder_hash(source_path)
        replica_hash = get_folder_hash(replica_path)

        if source_hash != replica_hash:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    replica_file = os.path.join(replica_path, os.path.relpath(source_file, source_path))
                    if os.path.exists(replica_file):
                        os.remove(replica_file)
                    os.makedirs(os.path.dirname(replica_file), exist_ok=True)
                    shutil.copyfile(source_file, replica_file)

        if log_level == 'DEBUG':
            logging.debug("Sync complete at: {}".format(time.strftime('%Y.%m.%d %H:%M:%S')))
        else:
            logging.info("Folders synchronized at {}".format(time.strftime('%Y.%m.%d %H:%M:%S')))
        time.sleep(interval)