import json

def signal_position(file_path, char_width=8, char_height=16, y_offset=5):
    signals = []
    signal_count = 1  # To track the signal names (e.g., Signal_1, Signal_2, etc.)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for row, line in enumerate(lines):
            for col in range(len(line.rstrip('\n')) - 1):  # Avoid out-of-bounds access for the next char
                char = line[col]
                next_char = line[col + 1]  # Get the next character
                prev_char = line[col - 1] if col > 0 else ''  # Get the previous character (safe check)
                
                # Check for conditions based on the character and its neighboring characters
                if char == 'à' and next_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row + 1) * char_height + y_offset  # Adjusted y with the offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "manual",
                        "signal_orientation": "left",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1

                elif char == 'â' and next_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row - 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15 + 2*char_height
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "manual",
                        "signal_orientation": "left",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1

                elif char == 'ø' and next_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row + 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "auto",
                        "signal_orientation": "left",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1
                
                elif char == 'ã' and prev_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row - 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15 + 2*char_height
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "manual",
                        "signal_orientation": "right",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1

                elif char == 'á' and prev_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row + 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "manual",
                        "signal_orientation": "right",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1

                elif char == 'û' and prev_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row - 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15 + 2*char_height
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "auto",
                        "signal_orientation": "right",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1
                elif char == 'ù' and prev_char in ['r', 'q','s']:
                    pixel_x = col * char_width
                    pixel_y = (row + 1) * char_height + y_offset
                    lamp_x = pixel_x + 8
                    lamp_y = pixel_y - 15
                    signal_data = {
                        "signal_name": f"Signal_{signal_count}",
                        "signal_position": [pixel_x, pixel_y],
                        "lamp_position": [lamp_x, lamp_y],
                        "signal_type": "auto",
                        "signal_orientation": "right",
                        "next_signal_names": None,
                        "conflicting_signals": None
                    }
                    signals.append(signal_data)
                    signal_count += 1

    # After determining signal orientation, adjust lamp position for "right" orientation
    for signal in signals:
        if signal["signal_orientation"] == "right":
            # Adjust lamp position: subtract 16 from x position
            signal["lamp_position"][0] -= 16

    # Save the data to output.json
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=4)

    print("Output saved to output.json")

# Example usage
signal_position("input.txt")
