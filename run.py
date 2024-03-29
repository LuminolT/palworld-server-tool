from config import *

import os
import shutil
import datetime
import subprocess
import time
import signal
import psutil
import logging

# logging config
logging.basicConfig(
    filename='run.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def find_pid_by_name(name):
    """find pid by name

    Args:
        name (str): process name

    Returns:
        int: pid
    """
    for proc in psutil.process_iter():
        if name in proc.name():
            return proc.pid

def file_backup(save_path, backup_path):
    """file backup after server reboot

    Args:
        save_path (str): path to save folder
        backup_path (str): path to backup folder
    """
    backup_folder = os.path.join(
        backup_path, f"backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    shutil.copytree(
        os.path.join(save_path, "Players"), os.path.join(backup_folder, "Players")
    )

    shutil.copy(
        os.path.join(save_path, "Level.sav"), os.path.join(backup_folder, "Level.sav")
    )
    shutil.copy(
        os.path.join(save_path, "LevelMeta.sav"),
        os.path.join(backup_folder, "LevelMeta.sav"),
    )

    shutil.make_archive(backup_folder, "zip", backup_folder)

    shutil.rmtree(backup_folder)
    
def run(script_path):
    """run server
    
    Args:
        script_path (str): path to script folder
    """
    try:
        logging.info("Starting server.")
        process = subprocess.Popen(
                [
                    "bash",
                    "-c",
                    f"{script_path}/PalServer.sh",
                    "-useperfthreads",
                    "-NoAsyncLoadingThread",
                    "-UseMultithreadForDS",
                ]
        )

        while True:
            time.sleep(60)
            pal_pid = find_pid_by_name("PalServer-Linux")
            process_info = psutil.Process(pal_pid)
            memory_percent = process_info.memory_percent()
            logging.info(f"Memory usage: {memory_percent}")
            if memory_percent > 80.0:
                logging.info("Memory usage is too high, restarting server...")
                process.send_signal(signal.SIGINT)
                time.sleep(10)
                return
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt, exiting...")
        process.send_signal(signal.SIGINT)
        raise KeyboardInterrupt
        
def main():
    try:
        while True:
            run(SCRIPT_PATH)
            file_backup(SAVE_PATH, BACKUP_PATH)
    except KeyboardInterrupt:
        return
        
if __name__ == "__main__":
    main()