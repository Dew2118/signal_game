from dataclasses import dataclass, asdict
import json
import tkinter as tk
from PIL import Image, ImageTk
import time
import random

class Drawer:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_signals(self, signal_details):
        """Draw signals with their colors and positions on the canvas."""
        for signal in signal_details:
            x, y = signal.lamp_position  # Use the lamp position for drawing
            x += 3.5  # Adjust position slightly
            y += 2
            radius = 3.5  # Keep the radius as set
            color = signal.color  # Use the color from the dataclass
            if signal.color == "green":
                color = "lime"
            # Draw the signal circle (no border)
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, fill=color, outline="", tags="signal"
            )

            # Extract and display the appropriate part of the signal name
            if len(signal.signal_name) <= len("Signal_9"):  # If the name is as long as "Signal_9"
                display_name = signal.signal_name[-1]  # Get the last character
            elif len(signal.signal_name) == len("Signal_19"):  # If the name is as long as "Signal_19" or longer
                display_name = signal.signal_name[-2:]  # Get the last two characters
            else:
                display_name = signal.signal_name[-3:]  # Get the last three character

            # Position the text slightly to the right of the circle
            text_x = x + radius + 10
            text_y = y - radius // 2
            # self.canvas.create_text(
            #     text_x,
            #     text_y,
            #     text=display_name,  # Display the extracted part of the signal name
            #     fill="light blue",  # Set text color to light blue
            #     font=("Arial", 8, "bold"),  # Use a bold font to make it "fatter"
            #     anchor="w",
            #     tags="signal"
            # )

            # Draw a small light blue dot at the signal position (with +2 to the y-coordinate) if rollback is True
            if signal.rollback:
                signal_x, signal_y = signal.signal_position  # Use the signal position for the dot
                dot_radius = 2  # Radius of the rollback indicator
                self.canvas.create_oval(
                    signal_x - dot_radius, (signal_y + 2) - dot_radius,
                    signal_x + dot_radius, (signal_y + 2) + dot_radius,
                    fill="light blue", outline="", tags="signal"
                )

    def draw_TRTS(self, signal_details,signal_name, color):
        #get the signal from signal_names by looping through signal_details
        print(signal_name,color)
        for signal in signal_details:
            if signal.signal_name == signal_name:
                x, y = signal.lamp_position  # Use the lamp position for drawing
                x += 3.5  # Adjust position slightly
                y += 2
                if signal.position == "l":
                    x -= 15
                else:
                    x += 15
                radius = 3.5  # Keep the radius as set
                # Draw the signal circle (no border)
                print(x,y,radius)
                self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius, fill=color, outline="", tags="TRTS"
                )

    def draw_train(self, train_position, train_text, signal_position):
        """Draw the train as a red rectangle with bold black text."""
        x, y = train_position
        width, height = 30, 6  # Dimensions of the train rectangle (height is 6)

        # Adjust x1 if the signal position is "left"
        if signal_position == "left":
            x = x - width  # Shift the rectangle to the left so the top-right aligns with the signal position

        # Draw the train rectangle
        self.canvas.create_rectangle(x, y-3, x + width, y + height+3, fill="#ff0000", outline="", tags="train")

        # Draw the train text with a black background
        text_x = x + width / 2
        text_y = y + height / 2
        for offset in [-1, 0]:  # Simulate a "fatter" font with slight horizontal offsets
            self.canvas.create_text(
                text_x + offset,  # Horizontal offset
                text_y,
                text=train_text,
                fill="white",  # Set text color to white
                font=("Arial", 10, "bold"),  # Use a bold font
                tags="train"
            )

class Game:
    def __init__(self, json_file, backdrop_path):
        self.json_file = json_file
        self.backdrop_path = backdrop_path
        self.signal_details = []
        self.trains = []
        self.canvas = None
        self.drawer = None  # Drawer instance for handling drawing

    def on_signal_click(self, event):
        """Handle clicks on signal lamps."""
        # Adjust the click coordinates based on the canvas scroll position
        adjusted_x = self.canvas.canvasx(event.x)
        adjusted_y = self.canvas.canvasy(event.y)

        # Find the clicked signal based on the adjusted mouse position
        for signal in self.signal_details:
            x, y = signal.lamp_position
            radius = 10  # Set to 10 for easier clicking
            if (x - radius <= adjusted_x <= x + radius) and (y - radius <= adjusted_y <= y + radius):
                # Show a popup menu with the signal name
                popup = tk.Toplevel()
                popup.title("Signal Menu")
                popup.geometry(f"200x100+{event.x_root}+{event.y_root}")

                # Map signal states to their corresponding letters
                state_mapping = {"red": "D", "yellow": "C", "green": "P"}
                signal_states = " ".join(state_mapping[state] for state in signal.signal_can_be) if signal.signal_can_be else "N/A"

                # Determine rollback status
                rollback_status = "Rollback On" if signal.rollback else "Rollback Off"

                # Display the signal name, signal_can_be, and rollback status
                label = tk.Label(
                    popup,
                    text=f"Signal: {signal.signal_name}\nAllowed States: {signal_states}\n{rollback_status}"
                )
                label.pack(pady=10)

                # Add key bindings for 1 (red), 2 (yellow), 3 (last element in signal_can_be), and r (toggle rollback)
                def set_signal_color(color):
                    if signal.signal_type == "manual" and color in signal.signal_can_be:
                        signal.color = color
                        signal.set_by_machine = False  # Set by human
                        self.canvas.delete("signal")  # Redraw signals
                        self.drawer.draw_signals(self.signal_details)
                    popup.destroy()  # Close the popup after setting the color

                def set_last_signal_color():
                    if signal.signal_type == "manual" and signal.signal_can_be:
                        set_signal_color(signal.signal_can_be[-1])  # Set to the last element in signal_can_be

                def toggle_rollback():
                    if signal.signal_type == "manual":
                        signal.rollback = not signal.rollback
                        self.canvas.delete("signal")  # Redraw signals
                        self.drawer.draw_signals(self.signal_details)
                    popup.destroy()  # Close the popup after toggling rollback

                popup.bind("1", lambda e: set_signal_color("red"))
                popup.bind("2", lambda e: set_signal_color("yellow"))
                popup.bind("3", lambda e: set_last_signal_color())  # Bind 3 to the last element in signal_can_be
                popup.bind("r", lambda e: toggle_rollback())

                # Close the popup on any left-click
                def close_popup(event=None):
                    if popup.winfo_exists():  # Check if the popup still exists
                        popup.destroy()

                # Bind a global click event to close the popup
                self.canvas.bind_all("<Button-1>", close_popup)

                # Ensure the popup is focused and closes on losing focus
                popup.focus_force()
                popup.protocol("WM_DELETE_WINDOW", lambda: close_popup())  # Handle the close button
                return  # Exit after finding the clicked signal

    def load_signal_details_from_json(self):
        """Load signal details from a JSON file and return a list of SignalDetails objects."""
        with open(self.json_file, "r") as file:
            data = json.load(file)
        self.signal_details = []
        for item in data:
            # Set default color to "red" for manual signals
            if item["signal_type"] == "manual":
                item["color"] = "red"
                item["signal_can_be"] = ["red", "yellow", "green"]  # Default for manual signals
            else:
                item["signal_can_be"] = None  # Default for auto signals

            # Set original_lamp_position to the same value as lamp_position
            item["original_lamp_position"] = item["lamp_position"]

            # Ensure next_signals_in_same_block is loaded or defaults to False
            item["next_signals_in_same_block"] = item.get("next_signals_in_same_block", False)

            self.signal_details.append(SignalDetails(**item))

    def convert_tuples(self,obj):
        if isinstance(obj, list):
            # Convert ["__tuple__", "Signal_15", 20] -> ("Signal_15", 20)
            if len(obj) > 0 and obj[0] == "__tuple__":
                return tuple(obj[1:])
            else:
                return [self.convert_tuples(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_tuples(value) for key, value in obj.items()}
        else:
            return obj

    

    def spawn_train(self, spawning_signal_name,trains):
        """Spawn a train at the specified signal."""
        with open('routes_mapping.json', 'r') as f:
            raw_data = json.load(f)
        routes_mapping = self.convert_tuples(raw_data)
        # Find the spawning signal
        spawning_signal = next(
            (signal for signal in self.signal_details if signal.signal_name == spawning_signal_name),
            None
        )
        if spawning_signal is None or spawning_signal.train_at_signal:
            return  # Skip if the signal is not found or is occupied

        # Find all routes associated with this spawning signal
        valid_routes = []
        for headcode_prefix, data in routes_mapping.items():
            if spawning_signal_name in data["spawning_signals"]:
                valid_routes.extend([(headcode_prefix, route) for route in data["routes"]])

        if not valid_routes:
            return  # Skip if no valid routes are found

        # Randomly select a route and generate a headcode
        headcode_prefix, selected_route = random.choice(valid_routes)
        existing_suffixes = {train.train_id[-2:] for train in trains}

        # Generate all possible 2-digit strings
        available_suffixes = [f"{i:02d}" for i in range(100) if f"{i:02d}" not in existing_suffixes]

        if not available_suffixes:
            raise ValueError("No available headcode suffixes left.")

        headcode_suffix = random.choice(available_suffixes)
        full_headcode = headcode_prefix + headcode_suffix
        first_stop = selected_route[0]
        if type(first_stop) == tuple:
            dwell_time = first_stop[1]
            selected_route[0] = (spawning_signal.signal_name, dwell_time)
        else:
            selected_route[0] = spawning_signal.signal_name
        # Create the new train
        new_train = Train(
            train_id=full_headcode,
            position=spawning_signal.signal_position,
            original_position=spawning_signal.signal_position,  # Set original_position to the initial position
            signal_position=spawning_signal.position,
            route=selected_route,
            previous_signal_tuple=spawning_signal_name,  # Set the previous signal to the spawning signal
            game=self  # Pass the Game instance
        )
        self.trains.append(new_train)

        # Mark the spawning signal as occupied
        spawning_signal.train_at_signal = True

        # Draw the train on the canvas
        self.drawer.draw_train(new_train.position, new_train.train_id, spawning_signal.position)

    def update_signals(self, conflict_duration=5):
        """Update all signals."""
        current_time = time.time()
        for signal in self.signal_details:
            signal.update(self.signal_details, conflict_duration, current_time)

    def update_trains(self):
        """Update all trains."""
        for train in self.trains[:]:  # Use a copy of the list to avoid modification during iteration
            train.move(self.signal_details, self.trains, self.drawer)

    def main_loop(self):
        """Main loop to update all trains and signals."""
        self.update_trains()
        self.update_signals()

        # Redraw the signals and trains
        self.canvas.delete("signal")  # Remove previous signals
        self.drawer.draw_signals(self.signal_details)
        self.canvas.delete("train")  # Remove previous trains
        for train in self.trains:
            self.drawer.draw_train(train.position, train.train_id, train.signal_position)

        # Schedule the next iteration of the loop
        self.canvas.after(100, self.main_loop)

    def periodic_train_spawning(self, spawning_signal_name, interval=1000, chance=1):
        """Periodically check if a train should spawn at the specified signal."""
        r = random.random()
        # print(r)
        if r < chance:  # Check if a train should spawn
            self.spawn_train(spawning_signal_name, self.trains)

        # Schedule the next check
        self.canvas.after(interval, self.periodic_train_spawning, spawning_signal_name, interval, chance)

    def run(self):
        """Run the game."""
        # Create the GUI window
        root = tk.Tk()
        root.title("Signal Game")

        # Load the backdrop image
        backdrop_image = Image.open(self.backdrop_path)
        backdrop_photo = ImageTk.PhotoImage(backdrop_image)

        # Get the dimensions of the backdrop image
        canvas_width, canvas_height = backdrop_image.size

        # Create a frame to hold the canvas and scrollbars
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for drawing
        self.canvas = tk.Canvas(
            frame,
            width=min(canvas_width, root.winfo_screenwidth()),
            height=min(canvas_height, root.winfo_screenheight()),
            bg="black"  # Set the background color to black
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add horizontal and vertical scrollbars
        h_scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to work with the scrollbars
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Set the scrollable region to the size of the image
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

        # Add the backdrop image to the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=backdrop_photo)

        # Initialize the Drawer instance
        self.drawer = Drawer(self.canvas)

        # Load signal details
        self.load_signal_details_from_json()

        # Draw signals
        self.drawer.draw_signals(self.signal_details)

        # Enable scrolling with the mouse wheel (vertical and horizontal)
        def _on_mousewheel(event):
            if event.state & 0x0001:  # Shift key is pressed
                self.canvas.xview_scroll(-1 * int(event.delta / 120), "units")  # Horizontal scrolling
            else:
                self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")  # Vertical scrolling

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bind mouse clicks to the canvas
        self.canvas.bind("<Button-1>", self.on_signal_click)  # Add this line

        # Start periodic train spawning
        self.periodic_train_spawning("Signal_220", 10000, 1)  # Spawn trains at Signal_1 every 5 seconds with a 1/2 chance
        # self.periodic_train_spawning("Signal_183", 10000, 1) 
        # Start the main loop
        self.main_loop()

        # Start the GUI event loop
        root.mainloop()

@dataclass
class SignalDetails:
    signal_name: str
    signal_position: tuple
    lamp_position: tuple
    original_lamp_position: tuple  # Store the original lamp position
    signal_type: str
    position: str
    next_signals: list  # List of next signals
    conflicting_signals: list = None  # List of conflicting signals (default to None)
    color: str = "green"  # Default color
    train_at_signal: bool = False  # Default train presence
    signal_can_be: list = None  # Default to None for auto signals, list for manual signals
    conflict_timer: float = 0  # Timer to track the red condition for conflicting signals
    last_conflict_state: list = None  # Last state of train_at_signal for conflicting signals
    rollback: bool = False  # Default to False, only for manual signals
    set_by_machine: bool = False  # Default to False, indicates if the signal was set by the system
    next_signals_in_same_block: bool = False  # If both next signals are in the same block which would change signal logic

    def update(self, signal_details, conflict_duration, current_time):
        """Update the signal's state based on its next and conflicting signals."""
        if not self.next_signals:  # Skip if next_signals is empty
            return

        # Handle conflicting signals
        if self.conflicting_signals:
            # Find all conflicting signals
            conflicting_signals = [
                next((s for s in signal_details if s.signal_name == conflict_name), None)
                for conflict_name in self.conflicting_signals
            ]
            # Filter out None values
            conflicting_signals = [s for s in conflicting_signals if s is not None]

            # Get the current train_at_signal state of conflicting signals
            current_conflict_state = [conflict.train_at_signal for conflict in conflicting_signals]

            # Check if the state is all False
            if all(not state for state in current_conflict_state):
                # Reset the conflict timer and state if all are False
                self.conflict_timer = 0
                self.last_conflict_state = current_conflict_state
            else:
                # Compare with the last conflict state
                if self.last_conflict_state != current_conflict_state:
                    # If the state has changed, start the timer
                    self.conflict_timer = current_time
                    self.color = "red"
                    self.set_by_machine = True
                    if self.signal_type == "manual":
                        self.signal_can_be = ["red"]  # Only red is allowed during conflict
                    self.last_conflict_state = current_conflict_state

            # Check if the conflict duration has passed
            if self.conflict_timer > 0 and current_time - self.conflict_timer >= conflict_duration:
                # Reset the conflict timer
                print("conflict has passed")
                self.conflict_timer = 0
                if self.signal_type == "manual":
                    self.signal_can_be = ["red", "yellow", "green"]

        # Handle auto signals
        if self.signal_type == "auto" and self.conflict_timer == 0:
            next_signals = [
                next((s for s in signal_details if s.signal_name == next_signal_name), None)
                for next_signal_name in self.next_signals
            ]
            next_signals = [s for s in next_signals if s is not None]


            if any(next_signal.train_at_signal for next_signal in next_signals):
                if any(not next_signal.train_at_signal for next_signal in next_signals) and (not self.next_signals_in_same_block):
                    self.color = "yellow"
                else:
                    self.color = "red"
            elif any(next_signal.color == "red" for next_signal in next_signals):
                self.color = "yellow"
            else:
                self.color = "green"
        # Handle manual signals
        elif self.signal_type == "manual" and self.conflict_timer == 0:
            next_signals = [
                next((s for s in signal_details if s.signal_name == next_signal_name), None)
                for next_signal_name in self.next_signals
            ]
            next_signals = [s for s in next_signals if s is not None]
            if any(next_signal.train_at_signal for next_signal in next_signals):
                if any(not next_signal.train_at_signal for next_signal in next_signals) and (not self.next_signals_in_same_block):
                    if self.color == "green":
                        self.color = "yellow"
                    self.signal_can_be = ["red", "yellow"]
                    # for next_signal in next_signals:
                        # print(next_signal.signal_name, next_signal.train_at_signal)
                else:
                    self.color = "red"
                    self.signal_can_be = ["red"]
                    self.set_by_machine = True
            elif any(next_signal.color == "red" for next_signal in next_signals):
                if self.color == "green" or (self.rollback is True and self.set_by_machine is True):
                    self.color = "yellow"
                self.signal_can_be = ["red", "yellow"]
                self.signal_can_be = ["red", "yellow", "green"]
                if self.rollback is True and self.set_by_machine is True:
                    self.color = self.signal_can_be[-1]  # Default to the last element in signal_can_be

@dataclass
class Train:
    train_id: str
    position: tuple  # Current position of the train
    original_position: tuple  # Store the original position
    route: list  # List of signal names the train will follow
    current_index: int = 0  # Current index in the route
    last_move_time: float = time.time()  # Timestamp of the last move
    signal_position: str = "right"  # Default signal position (left or right)
    previous_signal_tuple: tuple = None  # Track the previous signal name
    previous_signal_name: str = ""
    game: object = None  # Reference to the Game instance

    def move(self, signal_details, trains, drawer):
        """Move the train to the next signal in its route if 1 second has passed and the previous signal is not red."""
        current_time = time.time()
        if type(self.previous_signal_tuple) == tuple:
            print(self.previous_signal_tuple)
            dwell_time = self.previous_signal_tuple[1]
        else:
            dwell_time = 3
        if current_time - self.last_move_time >= (dwell_time - 10) and dwell_time != 3:
            if round(current_time - self.last_move_time) % 2 == 1:
                print(round(current_time - self.last_move_time))
                drawer.draw_TRTS(signal_details, self.previous_signal_name, "white")
            else:
                drawer.draw_TRTS(signal_details, self.previous_signal_name, "black")
        if current_time - self.last_move_time >= dwell_time:  # Check if 5 seconds have passed
            
            current_signal_something = self.route[self.current_index]
            if type(current_signal_something) == tuple:
                print("found to be tuple", current_signal_something)
                current_signal_name = current_signal_something[0]  # Get the signal name from the tuple
                self.previous_signal_tuple = current_signal_something
                
            else:
                current_signal_name = current_signal_something  # Get the signal name directly
                self.previous_signal_tuple = None  # Reset the previous signal tuple
            if self.current_index >= len(self.route):
                return  # Stop if the train has reached the end of the route
            # print(self.train_id, self.previous_signal_name, current_signal_name)
            # Get the current signal details
            # print(f"current_signal_name {current_signal_name}, previous_signal_name = {previous_signal_name}")
            if isinstance(current_signal_name, list):  # Handle multiple platforms
                # Find all signals in the list
                current_signals = [
                    next((signal for signal in signal_details if signal.signal_name == signal_name), None)
                    for signal_name in current_signal_name
                ]
                # Filter out None values and signals with train_at_signal == True
                available_signals = [signal for signal in current_signals if signal and not signal.train_at_signal]
                if not available_signals:
                    return  # Do not move if all platforms are occupied
                # Randomly select a platform if more than one is available
                else:
                    current_signal = random.choice(available_signals)
                current_signal_name = current_signal.signal_name  # Update the current signal name
            else:
                current_signal = next(
                    (signal for signal in signal_details if signal.signal_name == current_signal_name),
                    None
                )

            # Check if the train has reached the "delete_and_spawn_train" signal
            if current_signal_name == "delete_and_spawn_train":
                if self.previous_signal_name:  # Ensure there is a previous signal
                    previous_signal = next(
                        (signal for signal in signal_details if signal.signal_name == self.previous_signal_name),
                        None
                    )
                    if previous_signal:
                        previous_signal.train_at_signal = False
                trains.remove(self)
                if self.game:  # Use the passed Game instance
                    self.game.spawn_train(self.previous_signal_name,trains)  # Spawn a train at the previous signal
                return

            # Check if the train has reached the "delete" signal
            if current_signal_name == "delete":
                if self.previous_signal_name:  # Ensure there is a previous signal
                    previous_signal = next(
                        (signal for signal in signal_details if signal.signal_name == self.previous_signal_name),
                        None
                    )
                    if previous_signal:
                        previous_signal.train_at_signal = False
                trains.remove(self)  # Remove the train from the list of trains
                return

            # Check the previous signal's color
            if self.previous_signal_name:  # Ensure there is a previous signal
                previous_signal = next(
                    (signal for signal in signal_details if signal.signal_name == self.previous_signal_name),
                    None
                )
                if previous_signal and previous_signal.color == "red":
                    return  # Do not move if the previous signal is red

            # Set the previous signal's train_at_signal to False
            if self.previous_signal_name:
                previous_signal = next(
                    (signal for signal in signal_details if signal.signal_name == self.previous_signal_name),
                    None
                )
                if previous_signal:
                    previous_signal.train_at_signal = False
            # Set the next signal's train_at_signal to True
            if current_signal:
                current_signal.train_at_signal = True
                self.position = current_signal.signal_position  # Update train position
                self.signal_position = current_signal.position  # Update signal position (left or right)

            # Update the previous signal name and move to the next signal
            
            self.previous_signal_name = current_signal_name
            self.last_move_time = current_time
            self.current_index += 1


def main():
    # File paths
    json_file = "signal_details.json"
    backdrop_path = "zone_A_beauty_pass.bmp"  # Use beauty_pass.bmp as the backdrop

    # Create the Game instance
    game = Game(json_file, backdrop_path)

    # Run the game
    game.run()

if __name__ == "__main__":
    main()