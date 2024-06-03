import os


def rename_files_sequentially(directory_path):
    """Renames all files in a directory to a sequential number."""

    for index, filename in enumerate(os.listdir(directory_path)):
        # Check if it's a file (not a directory)
        if os.path.isfile(os.path.join(directory_path, filename)):
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"{index + 1}{file_extension}"
            os.rename(
                os.path.join(directory_path, filename),
                os.path.join(directory_path, new_filename),
            )


if __name__ == "__main__":
    # Get the directory path from the user
    directory_path = input("Enter the directory path: ")

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print("Error: Invalid directory path.")
    else:
        rename_files_sequentially(directory_path)
        print("Files renamed to sequential numbers successfully.")
