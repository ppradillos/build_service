import os
import shutil
import requests
import subprocess
import time
from git import Repo

# Only HTTP and HTTPS accepted, so far
def check_url_exists(url):
    try:
        response = requests.head(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        return False
    
    
def clone_repository(repo_url, repo_dir, timeout=10):
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            Repo.clone_from(repo_url, repo_dir)
            return True
        except Exception as e:
            time.sleep(1)  # wait for 1 second before retrying

    return False
    

def clear_folder(folder_path):
    """
    Clear the content of a folder (remove all files and subdirectories).

    Parameters:
    - folder_path (str): Path to the folder to be cleared.
    """
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error clearing {file_path}: {e}")