#!/usr/bin/env python3
import pygame
import os
import time
from PIL import Image
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import calendar

load_dotenv()

EVENT_FILE = os.environ.get('ALL_EVENTS_FILE', "./events.json")

FONT_FILE = os.environ.get('FONT_FILE', "/usr/share/fonts/truetype/freefont/FreeSans.ttf")

# TODO:  Only read photo images once per day.  Read planner once per hour

def load_image(path):
    pil_image = Image.open(path)
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

def render_calendar(events_by_day, width=1000, height=800):

    today = datetime.now().date()
    year, month = today.year, today.month
    cal = calendar.Calendar(firstweekday=6)  # Sunday start

    # Fonts
    header_font_size = 32
    day_font_size = 18
    event_font_size = 14
    header_font = pygame.font.SysFont("DejaVuSans", header_font_size, bold=True)
    day_font = pygame.font.SysFont("DejaVuSans", day_font_size, bold=True)
    event_font = pygame.font.SysFont("DejaVuSans", event_font_size)
    
    BACKGROUND_COLOR = (0,0,0)  # Semi-transparent white
    TODAY_BACKGROUND_COLOR = (60, 60, 50)  # Highlight color for today
    TEXT_COLOR = (255, 255, 255)
    LINE_COLOR = (200, 200, 200)

    # Layout
    weeks = list(cal.monthdatescalendar(year, month))
    n_rows = len(weeks)
    n_cols = 7
    cell_width = width // n_cols
    cell_height = (height - header_font_size - 10) // n_rows

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(BACKGROUND_COLOR)
    #pygame.draw.rect(surface, LINE_COLOR, (0, 0, width, height), 1)

    # Month header
    month_name = today.strftime("%B %Y")
    header_surface = header_font.render(month_name, True, TEXT_COLOR)
    surface.blit(header_surface, ((width - header_surface.get_width()) // 2, 2))

    # Day names
    for i, day_name in enumerate(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']):
        dn_surface = day_font.render(day_name, True, TEXT_COLOR)
        x = i * cell_width + (cell_width - dn_surface.get_width()) // 2
        y = header_font_size + 5
        surface.blit(dn_surface, (x, y))

    # Calendar grid and events
    for row_idx, week in enumerate(weeks):
        for col_idx, day in enumerate(week):
            x = col_idx * cell_width
            y = header_font_size + 10 + day_font_size + row_idx * cell_height

            # Highlight today
            if day == today:
                pygame.draw.rect(surface, TODAY_BACKGROUND_COLOR, (x, y, cell_width, cell_height), 0)

            # Dim days not in current month
            day_color = TEXT_COLOR if day.month == month else (160, 160, 160)
            day_surface = day_font.render(str(day.day), True, day_color)
            surface.blit(day_surface, (x + 4, y + 2))

            # Events
            events = events_by_day.get(day, [])
            for i in range(min(3, len(events))):
                if len(events[i]) > 15:
                    events[i] = events[i][:12] + '...'
                event_surface = event_font.render(events[i], True, TEXT_COLOR)
                surface.blit(event_surface, (x + 8, y + 24 + i * (event_font_size + 2)))
            if len(events) > 4:
                dots_surface = event_font.render("...", True, TEXT_COLOR)
                surface.blit(dots_surface, (x + 8, y + 24 + 3 * (event_font_size + 2)))

            # Cell border
            pygame.draw.rect(surface, LINE_COLOR, (x, y, cell_width, cell_height), 1)

    return surface

def get_most_recent_sunday(date):
    return date - timedelta(days=date.weekday() + 1) if date.weekday() != 6 else date


def render_events(events_by_day, width=1000, height=1400):

    header_font_size = 24
    event_font_size = 14
    line_padding = 3
    # Font setup
    header_font = pygame.font.SysFont("DejaVuSans", header_font_size, bold=True)
    event_font = pygame.font.SysFont("DejaVuSans", event_font_size)

    BACKGROUND_COLOR = (255, 255, 255, 128)  # Semi-transparent white
    TEXT_COLOR = (0, 0, 0)
    LINE_COLOR = TEXT_COLOR

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(BACKGROUND_COLOR)  # Semi-transparent white background
    # Draw calendar layout
    today = datetime.now().date()
    start_sunday = get_most_recent_sunday(today)

    # Layout: 2 columns (weeks), 7 rows (days)
    col_width = width // 2
    row_height = height // 7

    for week in range(2):
        for day_idx in range(7):
            day = start_sunday + timedelta(days=week * 7 + day_idx)
            
            x0 = week * col_width
            y0 = day_idx * row_height

             # Highlight today
            if day == today:
                pygame.draw.rect(surface, (255, 255, 200), (x0, y0, col_width, row_height), 0)


            # Header: "Jun 8 - Sunday"
            header_text = f"{day.strftime('%b')} {day.day} - {day.strftime('%A')}"
            header_surface = header_font.render(header_text, True, TEXT_COLOR)
            surface.blit(header_surface, (x0 + 5, y0 + 4))

            # Events
            events = events_by_day.get(day, [])
            for j, event in enumerate(events):
                event_surface = event_font.render(f"- {event}", True, TEXT_COLOR)
                surface.blit(event_surface, (x0 + 20, y0 + 4 + (header_font_size + line_padding) + j * (event_font_size + line_padding)))

            # Separator line
            if day_idx < 6:
                pygame.draw.line(surface, LINE_COLOR, (0, y0 + row_height - 1), (width, y0 + row_height - 1), 1)
        
        # Draw vertical separator between weeks
        if week == 0:
            pygame.draw.line(surface, LINE_COLOR, (col_width - 1, 0), (col_width - 1, height), 2)

    return surface


def run_slideshow(display_time=5):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    image_dir = "./raw_images"
    #planner_image = "./planner.png"

    PORTRAIT = 0
    LANDSCAPE = 1
    ASPECT = PORTRAIT
    screen_width, screen_height = (0, 0)
    if ASPECT == LANDSCAPE:
        screen_width, screen_height = screen.get_size()
    else:
        screen_height, screen_width = screen.get_size()

    #half_width = screen_width // 2
    margin = 10
    # Prepare events grouped by day

    # Open and read the JSON file of events
    events_dict = []
    with open(EVENT_FILE, 'r') as file:
        events_dict = json.load(file)

    # Organize events by day
    events_by_day = {}
    for dt_str, events in events_dict.items():
        dt = datetime.fromisoformat(dt_str)
        day_key = dt.date()
        events_by_day.setdefault(day_key, []).extend(events)

    # Create the event surface
    if ASPECT == LANDSCAPE:
        event_area_height = screen_height - (2 * margin)
        event_area_width = screen_width / 2 - (2 * margin)
        event_area_x = margin
        event_area_y = margin
        photo_area_width = screen_width / 2 - (2 * margin)
        photo_area_height = screen_height - (2 * margin)
        photo_area_x = screen_width / 2
        photo_area_y = 0
        event_surface = render_events(events_by_day, event_area_width, event_area_height)
    else:
        event_area_width = screen_width - (2 * margin)
        event_area_height = screen_height / 2 - (2 * margin)
        event_area_x = screen_height / 2
        event_area_y = margin
        photo_area_width = screen_width - (2 * margin)
        photo_area_height = screen_height / 2 - (2 * margin)
        photo_area_x = margin
        photo_area_y = margin
        event_surface = render_calendar(events_by_day, event_area_width, event_area_height)
        event_surface = pygame.transform.rotate(event_surface, 90)
    # planner = load_image(planner_image)
    # planner_scale = screen_height / planner.get_height()
    # planner_scaled_h = screen_height - (2 * margin)
    # planner_scaled_w = int(planner.get_width() * planner_scale)
    # planner_scaled = pygame.transform.smoothscale(planner, (planner_scaled_w, planner_scaled_h))
    #planner_x = margin
    #planner_y = margin


 
    image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    while True:

        for image_path in image_paths:
            image = load_image(image_path)
            img_aspect = image.get_width() / image.get_height()
            # Scale the image to fit the right side of the screen
            photo_target_w, photo_target_h = photo_area_width, photo_area_height
            if photo_target_w / photo_target_h > img_aspect:
                scaled_h = photo_target_h
                scaled_w = int(scaled_h * img_aspect)
            else:
                scaled_w = photo_target_w
                scaled_h = int(scaled_w / img_aspect)
            image_scaled = pygame.transform.smoothscale(image, (scaled_w, scaled_h))
            # Center the image
            image_x = photo_area_x + (photo_area_width - scaled_w) // 2
            image_y = photo_area_y + (photo_area_height - scaled_h) // 2

            if ASPECT == PORTRAIT:
                image_y = photo_area_y + (photo_area_width - scaled_w) // 2
                image_x = photo_area_x + (photo_area_height - scaled_h) // 2
                image_scaled = pygame.transform.rotate(image_scaled, 90)
            # Display the event surface and image
            screen.fill((0, 0, 0))
            screen.blit(event_surface, (event_area_x, event_area_y))
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
