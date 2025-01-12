import os

def find_starred_files(directory):
    """
    Recursively finds all files with a "star=yes" value in '.picasa.ini' files within the given directory
    and returns their paths relative to the top-level directory.

    :param directory: The base directory to search.
    :return: A list of paths to files with "star=yes", relative to the top-level directory.
    """
    starred_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower() == ".picasa.ini":
                picasa_path = os.path.join(root, file)
                try:
                    with open(picasa_path, "r") as f:
                        current_filename = None

                        for line in f:
                            line = line.strip()
                            # Check if the line is a header (filename in brackets)
                            if line.startswith("[") and line.endswith("]"):
                                current_filename = line[1:-1]  # Extract filename without brackets
                            # Check for a "star=yes" property
                            elif current_filename and line.startswith("star="):
                                _, value = line.split("=", 1)
                                if value.strip().lower() == "yes":
                                    # Compute the relative path to the starred file
                                    starred_file_path = os.path.relpath(
                                        os.path.join(root, current_filename), start=directory
                                    )
                                    starred_files.append(starred_file_path)
                                    current_filename = None  # Reset for the next entry
                except Exception as e:
                    print(f"Error processing {picasa_path}: {e}")

    return starred_files



# Example usage:
# directory_path = "/path/to/your/directory"
# starred_files = find_starred_files(directory_path)
# print(starred_files)

PICASA_FILE="picasa.txt"
def main():
    starred_files = find_starred_files("Z:\Pictures\Personal")
    print("Found " + str(len(starred_files)))
    try:
        with open(PICASA_FILE, 'w') as file:
            
            # Write each key-value pair
            for filename in starred_files:
                file.write(f"{filename}\n")
        
        print(f"Data written to {PICASA_FILE}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

if __name__ == "__main__":
  main()