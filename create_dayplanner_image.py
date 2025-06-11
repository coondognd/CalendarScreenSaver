import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ExifTags
from dotenv import load_dotenv
import json

from datetime import datetime, timedelta

load_dotenv()

EVENT_FILE = os.environ.get('ALL_EVENTS_FILE', "./events.json")
FONT_FILE = os.environ.get('FONT_FILE', "/usr/share/fonts/truetype/freefont/FreeSans.ttf")
CALENDAR_IMAGE_FILE = os.environ.get('CALENDAR_IMAGE_FILE', "./planner.png")
FONT_FILE = os.environ.get('FONT_FILE', "/usr/share/fonts/truetype/freefont/FreeSans.ttf")


import os

def get_most_recent_sunday(date):
    return date - timedelta(days=date.weekday() + 1) if date.weekday() != 6 else date

def create_calendar_image(events_dict, output_filename):
    # Image setup
    width, height = 500, 748
    image = Image.new("RGBA", (width, height), (255, 255, 255, 128))
    draw = ImageDraw.Draw(image)

    # Font setup
    try:
        header_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        event_font = ImageFont.truetype("DejaVuSans.ttf", 22)
    except:
        header_font = ImageFont.load_default(20)
        event_font = ImageFont.load_default(14)

    # Prepare and sort events by date
    events_by_day = {}
    for dt_str, events in events_dict.items():
        dt = datetime.fromisoformat(dt_str)
        day_key = dt.date()
        events_by_day.setdefault(day_key, []).extend(events)

    # Find most recent Sunday (or today if Sunday)
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
            x1 = x0 + col_width
            y1 = y0 + row_height

            # Highlight today
            if day == today:
                draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 200, 128))

            # Header text: "Jun 8 - Saturday"
            header_text = f"{day.strftime('%b')} {day.day} - {day.strftime('%A')}"
            draw.text((x0 + 11, y0 + 5), header_text, fill="black", font=header_font)

            # Draw events (if any)
            events = events_by_day.get(day, [])
            for j, event in enumerate(events):
                draw.text((x0 + 22, y0 + 35 + j * 18), f"- {event}", fill="black", font=event_font)

            # Draw separator line (horizontal)
            if day_idx < 6:
                draw.line([(x0, y1 - 1), (x1, y1 - 1)], fill="black", width=1)
        # Draw vertical separator between weeks
        if week == 0:
            draw.line([(col_width - 1, 0), (col_width - 1, height)], fill="black", width=2)

    image.save(output_filename)
    print(f"Calendar image saved to {output_filename}")

# def create_calendar_image(events_dict, output_filename):
#     # Image setup
#     width, height = 1000, 1400
#     image = Image.new("RGB", (width, height), "white")
#     draw = ImageDraw.Draw(image)

#     # Font setup
#     try:
#         header_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
#         event_font = ImageFont.truetype("DejaVuSans.ttf", 24)
#     except:
#         # Fallback fonts if DejaVuSans is not available
#         header_font = ImageFont.load_default()
#         event_font = ImageFont.load_default()

#     # Prepare and sort events by date
#     events_by_day = {}
#     for dt_str, events in events_dict.items():
#         dt = datetime.fromisoformat(dt_str)
#         day_key = dt.date()
#         events_by_day.setdefault(day_key, []).extend(events)

#     # Draw 7-day planner starting today
#     today = datetime.now().date()
#     section_height = height // 7

#     for i in range(7):
#         day = today + timedelta(days=i)
#         y_offset = i * section_height

#         # Header text: "Jun 8 - Saturday"
#         header_text = f"{day.strftime('%b')} {day.day} - {day.strftime('%A')}"
#         draw.text((20, y_offset + 10), header_text, fill="black", font=header_font)

#         # Draw events (if any)
#         events = events_by_day.get(day, [])
#         for j, event in enumerate(events):
#             draw.text((40, y_offset + 60 + j * 30), f"- {event}", fill="black", font=event_font)

#         # Draw separator line (except after last section)
#         if i < 6:
#             draw.line([(0, y_offset + section_height - 1), (width, y_offset + section_height - 1)], fill="black", width=1)

#     # Save image
#     image.save(output_filename)
#     print(f"Calendar image saved to {output_filename}")

# Example usage:
# events = {
#     "2025-06-08T19:30:00-04:00": ["Dinner with John"],
#     "2025-06-09T09:00:00-04:00": ["Meeting with team"],
#     "2025-06-10T14:00:00-04:00": ["Doctor appointment", "Pick up prescription"],
# }
# create_calendar_image(events, "calendar_output.png")


def main():

    # TODO: Stop screensaver if it's currently showing

    # Delete output directory contents
    output_file_path = "planner.png"
    if os.path.isfile(output_file_path):
        os.remove(output_file_path)

    # Get events 

    # Open and read the JSON file
    data = []
    with open(EVENT_FILE, 'r') as file:
        data = json.load(file)

    create_calendar_image(data, CALENDAR_IMAGE_FILE)

    # Re-enable or reload screensaver if needed
    print("Done creating planner image")

if __name__ == "__main__":
  main()