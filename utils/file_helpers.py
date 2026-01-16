import os

def validate_path(path: str, must_be_file: bool = False, must_be_dir: bool = False):
    """
    Validate a path. Raise helpful errors for debugging.

    Args:
        path (str): The path to validate.
        must_be_file (bool): If True, the path must be a file.
        must_be_dir (bool): If True, the path must be a directory.

    Raises:
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If expecting a folder but it's not.
        IsADirectoryError: If expecting a file but it's a folder.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if must_be_file and not os.path.isfile(path):
        raise IsADirectoryError(f"Expected a FILE, but got DIRECTORY: {path}")

    if must_be_dir and not os.path.isdir(path):
        raise NotADirectoryError(f"Expected a DIRECTORY, but got FILE: {path}")

    return True
