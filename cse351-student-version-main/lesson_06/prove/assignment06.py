"""
Course: CSE 351
Assignment: 06
Author: Jayden Pope

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def process_images_in_folder(input_queue,
                             processing_function,
                             output_queue=None,
                             input_folder=None,
                             output_folder=None,
                             barrier=None,
                             processing_args=None,
                             worker_count=None):

    while True:

        input_value = input_queue.get()
        if input_value is None:
            break
        filename, img = input_value


        try:
            if input_folder is not None:
                input_image_path = os.path.join(input_folder, filename)
                img = cv2.imread(input_image_path)

            if img is None:
                print(f"Warning: Could not read image '{filename}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            if output_queue is not None:
                output_queue.put((filename, processed_img))
            else:
                output_image_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_image_path, processed_img)

        except Exception as e:
            print(f"Error processing file '{filename}': {e}")


    if barrier is not None:
        barrier_index = barrier.wait()
        if barrier_index == 0:
            for _ in range(worker_count):
                output_queue.put(None)

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    SMOOTHING = 3
    GREYSCALE = 2
    EDGE_DETECT = 3

    smoothingQ = mp.SimpleQueue()
    greyscaleQ = mp.SimpleQueue()
    edgeQ = mp.SimpleQueue()
    
    smoothing_shield = mp.Barrier(SMOOTHING)
    grey_shield = mp.Barrier(GREYSCALE)

    create_folder_if_not_exists(STEP3_OUTPUT_FOLDER)

    smooth =[mp.Process(target=process_images_in_folder, args=(smoothingQ, task_smooth_image), kwargs={"output_queue": greyscaleQ, "input_folder": INPUT_FOLDER, "barrier": smoothing_shield, "worker_count": GREYSCALE, "processing_args": (GAUSSIAN_BLUR_KERNEL_SIZE,)}) for _ in range(SMOOTHING)]
    grey =[mp.Process(target=process_images_in_folder, args=(greyscaleQ, task_convert_to_grayscale), kwargs={"output_queue": edgeQ, "barrier": grey_shield, "worker_count": EDGE_DETECT}) for _ in range(GREYSCALE)]
    edge =[mp.Process(target=process_images_in_folder, args=(edgeQ, task_detect_edges), kwargs={"output_folder": STEP3_OUTPUT_FOLDER, "processing_args": (CANNY_THRESHOLD1, CANNY_THRESHOLD2)}) for _ in range(EDGE_DETECT)]

    print(f"\nProcessing images from '{INPUT_FOLDER}' to '{STEP3_OUTPUT_FOLDER}'...")


    [p.start() for p in smooth + grey + edge]

    for filename in os.listdir(INPUT_FOLDER):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue
        smoothingQ.put((filename, None))

    for _ in range(SMOOTHING):
        smoothingQ.put(None)

    [p.join() for p in smooth + grey + edge]

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
