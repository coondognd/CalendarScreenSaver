#!/usr/bin/env python3
import pygame
import os
import time
from PIL import Image

def load_image(path):
    pil_image = Image.open(path)
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

def run_slideshow(display_time=5):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    image_dir = "./raw_images"
    planner_image = "./planner.png"

    screen_width, screen_height = screen.get_size()
    #half_width = screen_width // 2

    planner = load_image(planner_image)
    planner_scale = screen_height / planner.get_height()
    planner_scaled_h = screen_height
    planner_scaled_w = int(planner.get_width() * planner_scale)
    planner_scaled = pygame.transform.smoothscale(planner, (planner_scaled_w, planner_scaled_h))
    planner_x = 0
    planner_y = 0

    remaining_w = screen_width - planner_scaled_w
    while True:
        image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        for image_path in image_paths:
            image = load_image(image_path)
            img_aspect = image.get_width() / image.get_height()
            right_target_w, right_target_h = remaining_w, screen_height
            if right_target_w / right_target_h > img_aspect:
                scaled_h = right_target_h
                scaled_w = int(scaled_h * img_aspect)
            else:
                scaled_w = right_target_w
                scaled_h = int(scaled_w / img_aspect)
            image_scaled = pygame.transform.smoothscale(image, (scaled_w, scaled_h))
            image_x = planner_scaled_w + (remaining_w - scaled_w) // 2
            image_y = (screen_height - scaled_h) // 2

            screen.fill((0, 100, 0))
            screen.blit(planner_scaled, (planner_x, planner_y))
            screen.blit(image_scaled, (image_x, image_y))
            pygame.display.flip()
            start_time = time.time()
            while time.time() - start_time < display_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                time.sleep(0.1)

if __name__ == "__main__":
    # Replace this with your image directory logic
     run_slideshow()
