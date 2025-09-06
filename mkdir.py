import os

def create_folders(folder_names):
    """
    To make multiple directories.

    Parameters:
    folder_names (list): The list of directories we need.
    """
    for name in folder_names:
        # Create the full path
        path = str(name)
        try:
            # Create the directory, exist_ok=True means already have one
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created successfully.")
        except Exception as e:
            print(f"Failed to create directory '{path}'. Reason: {str(e)}")

