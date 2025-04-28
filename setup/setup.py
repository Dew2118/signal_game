from dataclasses import dataclass, asdict
from PIL import Image, ImageDraw
import json

@dataclass  # Dataclass to store detailed information about each signal
class SignalDetails:
    signal_name: str
    signal_position: tuple
    lamp_position: tuple
    signal_type: str
    position: str
    next_signals: list = None
    conflicting_signals: list = None

def remove_near_duplicates(positions, radius):
    """Remove positions that are within a given radius of each other."""
    unique_positions = []
    for pos in positions:
        if not any(
            (pos[0] - unique_pos[0]) ** 2 + (pos[1] - unique_pos[1]) ** 2 <= radius ** 2
            for unique_pos in unique_positions
        ):
            unique_positions.append(pos)
    return unique_positions

def extract_signals_from_bitmap(image_path):
    """Extract signal and lamp positions from a bitmap image."""
    # Define the mapping of colors to signals
    color_to_signal = {
        (255, 0, 0): {"position": "right", "signal_type": "manual"},  # Red
        (255, 160, 255): {"position": "left", "signal_type": "manual"},  # Pink
        (0, 255, 255): {"position": "left", "signal_type": "auto"},  # Light Blue
        (0, 0, 255): {"position": "right", "signal_type": "auto"},  # Blue
    }
    green_color = (0, 255, 0)  # Define green color for lamps

    # Open the image
    image = Image.open(image_path)
    image = image.convert("RGB")  # Ensure the image is in RGB mode

    # Extract unique signals and their positions
    signal_positions = []
    lamp_positions = []
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            if pixel in color_to_signal:
                signal_positions.append((x, y, pixel))  # Store the position and color of the signal
            elif pixel == green_color:
                lamp_positions.append((x, y))  # Store the position of green lamps

    # Remove near duplicates
    signal_positions = remove_near_duplicates(signal_positions, radius=10)  # Adjust radius as needed
    lamp_positions = remove_near_duplicates(lamp_positions, radius=10)  # Adjust radius as needed

    return signal_positions, lamp_positions, color_to_signal

def find_closest_lamp(signal_position, lamp_positions):
    """Find the closest lamp to the given signal position."""
    x1, y1 = signal_position
    closest_lamp = None
    min_distance = float("inf")
    for lamp in lamp_positions:
        x2, y2 = lamp
        distance = (x2 - x1) ** 2 + (y2 - y1) ** 2  # Use squared distance for efficiency
        if distance < min_distance:
            min_distance = distance
            closest_lamp = lamp
    return closest_lamp

def create_signal_details(signal_positions, lamp_positions, color_to_signal):
    """Create detailed information for each signal."""
    signal_details_list = []
    for i, (x, y, color) in enumerate(signal_positions):
        closest_lamp = find_closest_lamp((x, y), lamp_positions)
        signal_info = color_to_signal[color]
        signal_details = SignalDetails(
            signal_name=f"Signal_{i + 1}",
            signal_position=(x, y),
            lamp_position=closest_lamp,
            signal_type=signal_info["signal_type"],
            position=signal_info["position"],
        )
        signal_details_list.append(signal_details)
    return signal_details_list

def save_signal_details_to_json(signal_details, output_file):
    """Save signal details to a JSON file."""
    with open(output_file, "w") as file:
        json.dump([asdict(detail) for detail in signal_details], file, indent=4)

def draw_signals_and_lamps(image_path, signal_positions, lamp_positions, output_path):
    """Draw circles around signals and lines connecting signals to lamps."""
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Draw circles around signal positions
    for x, y, _ in signal_positions:
        radius = 5  # Radius of the circle
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            outline="red", width=2  # Red circle with a width of 2
        )

    # Draw lines connecting signals to their closest lamps
    for x, y, _ in signal_positions:
        closest_lamp = find_closest_lamp((x, y), lamp_positions)
        if closest_lamp:
            lamp_x, lamp_y = closest_lamp
            draw.line(
                (x, y, lamp_x, lamp_y),
                fill="blue", width=1  # Blue line with a width of 1
            )

    # Save the output image
    image.save(output_path)
    print(f"Signals and lamps drawn and saved to {output_path}")

if __name__ == "__main__":
    # Path to the bitmap image
    bitmap_path = "zone_A_setup.bmp"
    output_path = "zone_A_with_signals_and_lamps.bmp"
    json_output_path = "signal_details.json"

    # Extract signals, their positions, and lamp positions
    signal_positions, lamp_positions, color_to_signal = extract_signals_from_bitmap(bitmap_path)

    # Create detailed signal information
    signal_details = create_signal_details(signal_positions, lamp_positions, color_to_signal)

    # Save signal details to a JSON file
    save_signal_details_to_json(signal_details, json_output_path)

    # Draw signals, lamps, and connections
    draw_signals_and_lamps(bitmap_path, signal_positions, lamp_positions, output_path)

    # Print the path to the JSON file
    print(f"Signal details saved to {json_output_path}")