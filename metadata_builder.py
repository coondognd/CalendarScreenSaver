import os
from PIL import Image
from PIL.ExifTags import TAGS

RAW_DIR = "./raw_images"
METADATA_FILE = "./metadata.txt"

def get_photo_dates(directory):
    """
    Reads photo metadata for every image in the directory and extracts the date the photo was taken.

    :param directory: The path to the directory containing images.
    :return: A dictionary with image filenames as keys and photo dates as values, formatted as 'YYYY-MM-DD'.
    """
    if not os.path.isdir(directory):
        print(f"The specified path '{directory}' is not a directory.")
        return {}

    photo_dates = {}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if not os.path.isfile(file_path):
            continue  # Skip non-file entries

        try:
            # Open the image and check for EXIF data
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                if not exif_data:
                    photo_dates[filename] = "No EXIF data"
                    continue

                # Look for the DateTimeOriginal tag (usually tag ID 36867)
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        # Format the date
                        photo_date = value.split(" ")[0].replace(":", "-")  # Format as 'YYYY-MM-DD'
                        photo_dates[filename] = photo_date
                        break
                #else:
                #    photo_dates[filename] = "No DateTimeOriginal tag"
        except Exception as e:
            photo_dates[filename] = f"Error reading file: {e}"

    return photo_dates

# Example usage:
# directory_path = "path/to/your/directory"
# photo_metadata = get_photo_dates(directory_path)
# print(photo_metadata)


def main():
    photo_metadata = get_photo_dates(RAW_DIR)
    try:
        with open(METADATA_FILE, 'w') as file:
            
            # Write each key-value pair
            for key, value in photo_metadata.items():
                file.write(f"{key}\t{value}\n")
        
        print(f"Data written to {METADATA_FILE}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


if __name__ == "__main__":
  main()