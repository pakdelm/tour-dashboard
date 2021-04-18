import os

def create_os_independent_path(path: str) -> str:
    # First normalize the path string into a proper string for the OS.
    # Then os.sep must be safe to use as a delimiter in string function split.
    split_path = os.path.normpath(path).split(os.path.sep)
    # splat to iterate through list
    joined_path = os.path.join(*split_path)

    return joined_path