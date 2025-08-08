import os

def create_folders(folder_names):
    """
    to make multiple directories。

    parameters:
    folder_names (list): the list of directories we need。
    """
    for name in folder_names:
        # create the full path
        path = str(name)
        try:
            # create the directory，exist_ok=True means already have one
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created successfully.")
        except Exception as e:
            print(f"Failed to create directory '{path}'. Reason: {str(e)}")

