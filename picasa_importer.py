import os
from PIL import Image, ExifTags
import re

PICASA_DIR = "./picasa"

def read_file_to_array(filename):
    """
    Reads the contents of a file and returns them as a list of strings.

    :param filename: The path to the file to be read.
    :return: A list of strings, where each string is a line from the file.
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        # Strip newline characters from each line
        return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []

patterns_to_skip = [
    "tailgate",
    "wedding",
    " game",
    ".mp4",
    ".mov"
]
def should_be_skipped(filename):
    filename = filename.lower()
    for pattern in patterns_to_skip:
        if filename.find(pattern) > -1:
            #print("Found " + pattern + " in " + filename)
            return True
    return False

def main():

    picasa_images = read_file_to_array("picasa.txt")

    regex = re.compile(r"[^a-zA-Z0-9\.\-_]", re.IGNORECASE)
    target_height = 1080
    # Put in the new ones
    for image_filename in picasa_images:
        if should_be_skipped(image_filename):
            #print("Skipping")
            continue
        full_image_filename = "Z:\\Pictures\\Personal\\" + image_filename
        try:
            # Open the image
            with Image.open(full_image_filename) as img:
                exif_data = img.info.get("exif")

                # Rotate the image based on EXIF orientation
                if exif_data:
                    try:
                        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
                        #print(exif)
                        orientation = exif.get("Orientation")
                        if orientation == 3:
                            #print("Rotating 3: " + full_image_filename)
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            #print("Rotating 6: " + full_image_filename)
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            #print("Rotating 8: " + full_image_filename)
                            img = img.rotate(90, expand=True)
                    except Exception as e:
                        print(f"Could not process EXIF orientation for {full_image_filename}: {e}")

                # Calculate new width while maintaining aspect ratio
                aspect_ratio = img.width / img.height
                new_width = int(target_height * aspect_ratio)

                # Resize the image
                resized_img = img.resize((new_width, target_height))

                unique_filename = image_filename
                unique_filename = unique_filename.replace("\\", "_")
                unique_filename = unique_filename.replace("/", "_")
                unique_filename = unique_filename.replace(".JPG", ".jpeg")
                unique_filename = unique_filename.replace(".jpg", ".jpeg")
                unique_filename = regex.sub("", unique_filename)
                # Save the resized image
                output_path = os.path.join(PICASA_DIR, unique_filename) # os.path.basename(image_filename))
                resized_img.save(output_path) #, exif=exif_data)
                print(f"Resized and saved: {output_path}")
        except Exception as e:
            print(f"Error processing {image_filename}: {e}")


if __name__ == "__main__":
  main()