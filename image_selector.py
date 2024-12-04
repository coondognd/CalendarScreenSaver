from datetime import datetime, timedelta
import random
import shutil
import os
import glob

ALL_IMG_DIR = "./all_images"
RAW_DIR = "./raw_images"
METADATA_FILE = "./metadata.txt"
IMAGE_COUNT = 20

def read_tab_delimited_file_to_dict(input_file):
    """
    Reads a tab-delimited text file and reconstructs the dictionary.

    :param input_file: The path to the tab-delimited text file.
    :return: A dictionary where keys are filenames and values are dates.
    """
    reconstructed_dict = {}
    
    try:
        with open(input_file, 'r') as file:
            # Skip the header row
            #next(file)
            
            # Read each line and split by tab to reconstruct the dictionary
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) == 2:  # Ensure there are exactly two columns
                    filename, date = parts
                    reconstructed_dict[filename] = date
        
        print(f"Data successfully reconstructed from {input_file}")
    except FileNotFoundError:
        print(f"The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    
    return reconstructed_dict



# Example usage:
# reconstructed_data = read_tab_delimited_file_to_dict("output.txt")
# print(reconstructed_data)


def sort_dict_by_date_desc(data):

    # Sort by parsed date, with invalid dates treated as the oldest
    sorted_items = sorted(data.items(), key=lambda item: item[1], reverse=True)

    # Convert back to a dictionary
    return dict(sorted_items)

# Example usage:
# reconstructed_data = read_tab_delimited_file_to_dict("output.txt")
# sorted_data = sort_dict_by_date_desc(reconstructed_data)
# print(sorted_data)


def main():
    images_and_dates = read_tab_delimited_file_to_dict(METADATA_FILE)
    print("There are " + str(len(images_and_dates)) + " images")
    if len(images_and_dates) == 0:
        print("No images found")
        exit
    sorted_images = sort_dict_by_date_desc(images_and_dates)

    num_recent_images = 4
    if len(sorted_images) < 4:
        num_recent_images = len(sorted_images)
    print("Looking for " + str(num_recent_images) + " recent images")
    recent_images = list(sorted_images)[0:(num_recent_images-1)]
    print("Grabbed " + str(len(recent_images)) + " recent ones")

    seasonal_images = []
    future_date = datetime.now() + timedelta(days=30)
    past_date = datetime.now() - timedelta(days=15)
    future = future_date.strftime("%m-%d")
    past = past_date.strftime('%m-%d')
    print("Looking for images from " + past + " to " + future)

    wraparound = False
    if (future < past):
        wraparound = True
    
    for image in sorted_images:
        photo_date = sorted_images[image][5:9]
        if not wraparound and photo_date > past and photo_date < future:
            print ("No rap.  Adding an image")
            seasonal_images.append(image)
        elif wraparound and photo_date > past or photo_date < future:
            print ("Wrap.  Adding an image")
            seasonal_images.append(image)
    random.shuffle(seasonal_images)

    # Combine recent images with seasonal images
    images_to_use = recent_images + seasonal_images
    images_to_use = list(dict.fromkeys(images_to_use)) # deduplicate

    if len(images_to_use) < IMAGE_COUNT:
        print ("Padding out the images")
        # If not enough, add more
        # Note this could add duplicates
        additional_photos = list(sorted_images)
        random.shuffle(additional_photos)
        images_to_use += additional_photos[0:IMAGE_COUNT-len(images_to_use)]
    elif len(images_to_use) > IMAGE_COUNT:
        print ("Cutting down the images")
        # If too many, remove some
        images_to_use = images_to_use[0:(IMAGE_COUNT-1)] 

    # Clear out the last crop
    print ("Deleting old ones")
    files = glob.glob(RAW_DIR + '/*')
    for f in files:
        os.remove(f)

    print ("Saving new ones")
    # Put in the new ones
    for image in images_to_use:
        shutil.copy2(ALL_IMG_DIR  + "/" + image, RAW_DIR + "/" + image)  


if __name__ == "__main__":
  main()