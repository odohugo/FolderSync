import argparse, shutil, filecmp, time, os, sys

_log_file = ""

def main():
    parser = argparse.ArgumentParser(
        prog="FolderSync",
        description="Folder syncing tool that copies everything within a source folder to a destination folder. Can sync once or periodically depending on arguments uFolderSyncsed."
        )

    parser.add_argument("source", type=str, help="Source folder path")
    parser.add_argument("destination", type=str, help="Destination folder path")
    parser.add_argument("log", type=str, help="Log file folder path")
    parser.add_argument("-timer", type=int, default=0, help="Time interval between syncing actions, in seconds. Has to be greater than or equal to 10 and smaller than or equal to 3600")
    
    args = parser.parse_args()

    handle_errors(args)
    create_log_file(args.log)

    print("")
    log_message(f"|FOLDER SYNC TOOL|")    
    log_message("--------------------------------------------------------------------------------------------")
    log_message(f"Source folder path is: {args.source}")
    log_message(f"Destination folder path is: {args.destination}")
    log_message(f"Log will be saved in: {_log_file}")
    if not args.timer == 0:
        log_message(f"Syncing interval is {args.timer} seconds.")
    log_message("--------------------------------------------------------------------------------------------")
    input("Press Enter to begin.")
    print("")

    if args.timer == 0:
        run_once(args)
    else:
        run_periodically(args)
        
    print("")
    input('Press Enter to finish.')


def run_once(args):
    clear_destination(args.source, args.destination)
    copy_files(args.source, args.destination)
    log_message("Sync finished.")


def run_periodically(args):
    try:
        while True:
            log_message(f"Syncing...")
            clear_destination(args.source, args.destination)
            copy_files(args.source, args.destination)
            log_message(f"Sync finished. Next syncing action in {args.timer} seconds")
            log_message("")
            time.sleep(args.timer)
    except KeyboardInterrupt:
        log_message("Syncing stopped")
        sys.exit(1)


# Copies all files from source folder to destination folder
def copy_files(source, destination):
    for filename in os.listdir(source):
        source_path = os.path.join(source, filename)
        destination_path = os.path.join(destination, filename)
        
        if os.path.isdir(source_path):
            newDestination = os.path.join(destination, filename)
            if not os.path.exists(newDestination):
                os.makedirs(newDestination)
                log_message(f"Created directory: {newDestination}")
            copy_files(source_path, newDestination)
        if os.path.isfile(source_path):
            # Before copying, compares if files are identical and if so does not copy
            if os.path.isfile(destination_path) and filecmp.cmp(source_path, destination_path, shallow=False):
                log_message(f"Not copying {source_path}, files are identical")
            else:
                shutil.copy2(source_path, destination)
                log_message(f"Copied file: {source_path} -> {destination}")


# Checks if any files in destination folder do not have a corresponding file in the source folder with the same name and if so, deletes them
def clear_destination(source, destination):
    for filename in os.listdir(destination):
        source_path = os.path.join(source, filename)
        destination_path = os.path.join(destination, filename)

        if os.path.isdir(destination_path):
            clear_destination(source_path, destination_path)
            if not os.path.isdir(source_path):
                os.rmdir(destination_path)
                log_message(f"Deleted directory: {destination_path}")

        if os.path.isfile(destination_path) and not os.path.isfile(source_path):
            os.remove(destination_path)
            log_message(f"Deleted file: {destination_path}")


# Error handling
def handle_errors(args):
    if not os.path.isdir(args.source):
        print("Source folder is not a valid path.")
        sys.exit(1)
    if not os.path.isdir(args.destination):
        print("Destination folder is not a valid path.")
        sys.exit(1)
    if not os.path.isdir(args.log):
        print("Destination folder is not a valid path.")
        sys.exit(1)

    if args.source == args.destination:
        print("Source and destination folders cannot be the same")
        sys.exit(1)
    if args.source == args.log:
        print("Source folder and log file location cannot be the same")
        sys.exit(1)
    if args.destination == args.log:
        print("Destination folder and log file location cannot be the same")
        sys.exit(1)

    if args.timer != 0 and (args.timer < 10 or args.timer > 3600):
        print("Timer value must be greater than or equal to 10 and smaller than or equal to 3600")
        sys.exit(1)


def create_log_file(log_folder):
    global _log_file
    log_number = 0
    while True:
        log_filename = f"{time.strftime("%Y-%m-%d")}_FolderSync_Log_{log_number:03d}.txt"
        initial_log_file = os.path.join(log_folder, log_filename)
        if os.path.isfile(initial_log_file):
            log_number += 1
        else:
            _log_file = initial_log_file
            return


def log_message(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] - {message}")
    with open(_log_file, "a") as log_file:
        log_file.write(f"[{timestamp}] - {message}\n")
    

if __name__ == "__main__":
    main()