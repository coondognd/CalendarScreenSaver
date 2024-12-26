import os
import shutil
from PIL import Image, ImageDraw, ImageFont



COOKED_DIR = os.environ.get('COOKED_DIR', "./cooked_images")
RAW_DIR = os.environ.get('RAW_DIR', "./raw_images")
EVENT_FILE = os.environ.get('EVENT_FILE', "./events.txt")

#enum constants
TODAY_MODE = 1
TOMORROW_MODE = 2

def delete_all_files_in_directory(directory):
    """
    Deletes all files in the specified directory.

    :param directory: The path to the directory.
    """
    if not os.path.isdir(directory):
        print(f"The specified path '{directory}' is not a directory.")
        return
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"All files in '{directory}' have been deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")


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

import os

def get_filenames_in_directory(directory):
    """
    Returns a list of all filenames in the specified directory.

    :param directory: The path to the directory.
    :return: A list of filenames in the directory.
    """
    if not os.path.isdir(directory):
        print(f"The specified path '{directory}' is not a directory.")
        return []

    try:
        # List all items in the directory and filter for files
        filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return filenames
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def add_text_with_background(image_filename, output_directory, text):
    """
    Adds text with a translucent black background to the upper-left corner of an image and saves the result.

    :param image_filename: Path to the input image file.
    :param output_directory: Path to the output directory.
    :param text: The text to add to the image.
    """
    LEFT_PADDING = 20
    TOP_PADDING = 20

    if not os.path.isfile(image_filename):
        print(f"The file '{image_filename}' does not exist.")
        return

    if not os.path.isdir(output_directory):
        print(f"The directory '{output_directory}' does not exist.")
        return

    try:
        # Open the image
        image = Image.open(image_filename)
        draw = ImageDraw.Draw(image)

        font_size=36
        #if (image.height > image.width):
        #    font_size = 68
        #text = str(font_size) + " " + str(image.width) + "x" + str(image.height)

        # Define font (use a default font if no .ttf file is specified)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)  # Adjust font size as needed
        except IOError:
            font = ImageFont.load_default()

        # Calculate text size
        text_l, text_t, text_r, text_b = draw.multiline_textbbox((LEFT_PADDING + 20, TOP_PADDING + 20), text, font=font)
        text_width = text_r - text_l
        text_height  = text_b - text_t

        # Define background rectangle
        padding = 20
        background_position = (LEFT_PADDING, TOP_PADDING, (2 * LEFT_PADDING) + (text_width + 2 * padding), (2 * TOP_PADDING) + (text_height + 2 * padding))
        background_color = (0, 0, 0, 96)  # RGBA - black with 50% transparency

        # Create an overlay for the background
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(background_position, fill=background_color)

        # Composite the overlay onto the image
        image = Image.alpha_composite(image.convert("RGBA"), overlay)

        # Add text over the background
        text_position = (LEFT_PADDING + padding, TOP_PADDING + padding)
        text_color = (255, 255, 255)  # White text
        draw = ImageDraw.Draw(image)
        draw.text(text_position, text, fill=text_color, font=font) # multiline_

        # Construct the output file path
        output_path = os.path.join(output_directory, os.path.basename(image_filename))

        # Save the modified image
        image.save(output_path, "PNG")
        #print(f"Image saved to: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# add_text_with_background("input.jpg", "output_directory", "Hello, World!")


def main():

    # TODO: Stop screensaver if it's currently showing

    # Delete output directory contents
    delete_all_files_in_directory(COOKED_DIR)

    # Get events 
    event_list = read_file_to_array(EVENT_FILE)
    event_string = None
    if event_list is not None and len(event_list) > 1:
        event_string = "\n".join(event_list)

    # Read images
    raw_image_filenames = get_filenames_in_directory(RAW_DIR)
    # Add events to those images
    for raw_image_filename in raw_image_filenames:
        raw_file_path = os.path.join(RAW_DIR, raw_image_filename)
        if event_string is not None:
            add_text_with_background(raw_file_path, COOKED_DIR, event_string)
        else:
            shutil.copy2(raw_file_path, COOKED_DIR + "/")  
        # Save image

    # Re-enable or reload screensaver if needed
    print("Done creating images")

if __name__ == "__main__":
  main()