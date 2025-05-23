import json
import tkinter as tk
from PIL import Image, ImageTk
import time
import random


# constant
SIGNAL_DETAILS_FILENAME = "zone_F/zone_F_signal_details.json"
ROUTES_MAPPING_FILENAME = "zone_F/zone_F_routes_mapping.json"
BACKDROP_PATH_FILENAME = "zone_F/zone_F_beauty_pass.bmp"  # Use beauty_pass.bmp as the backdrop
CHANCE = 1/4
STANDARD_SIGNAL_DWELL_TIME = 5
TRTS_TIME_BEFORE_DEPARTURE = 5
CONFLICT_DURATION = 3
MAX_TRAIN_NUMBER = 15
PERIODIC_TRAIN_SPAWNING_SIGNALS = ["Signal_106"]

class Drawer:
    def __init__(self, game):
        self.canvas = None
        self.game = game

    def set_after(self, delay, func, *args):
        self.canvas.after(delay, func, *args)

    def set_signal_color(self,signal,popup,color):
        if signal.signal_type == "manual" and color in signal.signal_can_be:
            signal.color = color
            signal.set_by_machine = False  # Set by human
            self.delete("signal")  # Redraw signals
            self.draw_signals(self.game.get_signal_details())
            signal.queue = ""
        else:
            signal.queue = "yellow"
        popup.destroy()  # Close the popup after setting the color

    def set_last_signal_color(self,popup,signal):
        if signal.signal_type == "manual" and signal.signal_can_be:
            if signal.signal_can_be == ["red"]:
                self.set_signal_color(signal,popup,"green")
            else:
                self.set_signal_color(signal,popup,signal.signal_can_be[-1])

    def close_popup(self, popup, event=None):
        if popup.winfo_exists():  # Check if the popup still exists
            popup.destroy()

    def create_popup_text(self,popup,signal):
        state_mapping = {"red": "D", "yellow": "C", "green": "P"}
        all_states = ["red", "yellow", "green"]
        signal_states_display = ""

        for state in all_states:
            code = state_mapping[state]
            if signal.signal_can_be:
                in_can_be = state in signal.signal_can_be
            else:
                in_can_be = False
            is_queue = state == signal.queue

            if in_can_be and is_queue:
                code = f"[{code}*]"  # in can_be and is queue
            elif in_can_be:
                code = f"[{code}]"   # only in can_be
            elif is_queue:
                code = f"{code}*"    # only in queue

            signal_states_display += code + " "

        signal_states_display = signal_states_display.strip()

        rollback_status = "Rollback On" if signal.rollback else "Rollback Off"

        label_text = (
            f"Signal: {signal.signal_name}\n"
            f"{signal_states_display}\n"
            f"{rollback_status}"
        )

        label = tk.Label(popup, text=label_text)
        label.pack(pady=10)        

    def on_signal_click(self, event):
        """Handle clicks on signal lamps."""
        # Adjust the click coordinates based on the canvas scroll position
        adjusted_x = self.canvas.canvasx(event.x)
        adjusted_y = self.canvas.canvasy(event.y)
        # Find the clicked signal based on the adjusted mouse position
        for signal in self.game.get_signal_details():
            x, y = signal.lamp_position
            radius = 10  # Set to 10 for easier clicking
            if (x - radius <= adjusted_x <= x + radius) and (y - radius <= adjusted_y <= y + radius):
                # Show a popup menu with the signal name
                popup = tk.Toplevel()
                popup.title("Signal Menu")
                popup.geometry(f"200x100+{event.x_root}+{event.y_root}")
                self.create_popup_text(popup,signal)
                popup.bind("1", lambda e: self.set_signal_color(signal,popup,"red"))
                popup.bind("2", lambda e: self.set_signal_color(signal,popup,"yellow"))
                popup.bind("3", lambda e: self.set_last_signal_color(popup,signal))  # Bind 3 to the last element in signal_can_be
                popup.bind("r", lambda e: self.game.toggle_rollback(signal,popup))
                # Close the popup on any left-click
                # Bind a global click event to close the popup
                self.canvas.bind_all("<Button-1>", lambda event: self.close_popup(popup))

                # Ensure the popup is focused and closes on losing focus
                popup.focus_force()
                popup.protocol("WM_DELETE_WINDOW", lambda: self.close_popup(popup))  # Handle the close button
                return  # Exit after finding the clicked signal

    def config_canvas(self, canvas_width, canvas_height, backdrop_photo, root, frame):
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

        # Enable scrolling with the mouse wheel (vertical and horizontal)
        def _on_mousewheel(event):
            if event.state & 0x0001:  # Shift key is pressed
                self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")  # Vertical scrolling
            else:
                self.canvas.xview_scroll(-1 * int(event.delta / 120), "units")  # Horizontal scrolling

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bind mouse clicks to the canvas
        self.canvas.bind("<Button-1>", self.on_signal_click)  # Add this line

    def create_signal_number(self,signal,radius,x,y):
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
            self.canvas.create_text(
                text_x,
                text_y,
                text=display_name,  # Display the extracted part of the signal name
                fill="light blue",  # Set text color to light blue
                font=("Arial", 8, "bold"),  # Use a bold font to make it "fatter"
                anchor="w",
                tags="signal"
            )

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
            self.create_signal_number(signal,radius,x,y)

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
        for signal in signal_details:
            if signal.signal_name == signal_name:
                x, y = signal.lamp_position  # Use the lamp position for drawing
                x += 3.5  # Adjust position slightly
                y += 2
                if signal.signal_orientation == "left":
                    x += 15
                else:
                    x -= 15
                radius = 3.5  # Keep the radius as set
                # Draw the signal circle (no border)
                self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius, fill=color, outline="", tags="TRTS"
                )

    def draw_train(self, train_position, train_text, signal_orientation):
        """Draw the train as a red rectangle with bold black text."""
        x, y = train_position
        width, height = 30, 6  # Dimensions of the train rectangle (height is 6)

        # Adjust x1 if the signal position is "left"
        if signal_orientation == "left":
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

    def delete(self,tag):
        self.canvas.delete(tag)

class Game:
    def __init__(self, json_file, backdrop_path):
        self.json_file = json_file
        self.backdrop_path = backdrop_path
        self.signal_details = []
        self.trains = []
        self.drawer = None  # Drawer instance for handling drawing

    def toggle_rollback(self,signal,popup):
        if signal.signal_type == "manual":
            signal.rollback = not signal.rollback
            # self.drawer.delete("signal")  # Redraw signals
            # self.drawer.draw_signals(self.signal_details)
        popup.destroy()  # Close the popup after toggling rollback

    def load_signal_details_from_json(self):
        """Load signal details from a JSON file and return a list of SignalDetails objects."""
        with open(self.json_file, "r") as file:
            data = json.load(file)
        self.signal_details = []
        for item in data:
            item["next_signals_in_same_block"] = item.get("next_signals_in_same_block", False)
            self.signal_details.append(SignalDetails(**item))

    def convert_values(self,obj):
        if isinstance(obj, list):
            return [self.convert_values(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_values(value) for key, value in obj.items()}
        else:
            return obj

    def get_spawning_signal(self, spawning_signal_name):
        for signal in self.signal_details:
            if signal.signal_name == spawning_signal_name:
                return signal

    def select_route_and_headcode(self, spawning_signal_name, trains):
        with open(ROUTES_MAPPING_FILENAME, 'r') as f:
            raw_data = json.load(f)
        routes_mapping = self.convert_values(raw_data)
        valid_routes = []
        for i,data in enumerate(routes_mapping):
            # print(data)
            if spawning_signal_name in data["spawning_signals"]:
                headcode_prefix = data["headcode_prefix"]
                valid_routes.extend([(headcode_prefix, route) for route in data["routes"]])
        if len(valid_routes) == 0:
            raise ValueError(f"No valid routes found for the spawning signal {spawning_signal_name}.")
        headcode_prefix, selected_route = random.choice(valid_routes)
        existing_suffixes = {train.train_id[-2:] for train in trains}
        # Generate all possible 2-digit strings
        available_suffixes = [f"{i:02d}" for i in range(100) if f"{i:02d}" not in existing_suffixes]
        if not available_suffixes:
            raise ValueError("No available headcode suffixes left.")
        headcode_suffix = random.choice(available_suffixes)
        full_headcode = headcode_prefix + headcode_suffix
        return selected_route, full_headcode

    def spawn_train(self, spawning_signal_name,trains):
        """Spawn a train at the specified signal."""
        spawning_signal = self.get_spawning_signal(spawning_signal_name)
        if spawning_signal is None or spawning_signal.train_at_signal is not None:
            return  # Skip if the signal is not found or is occupied
        selected_route, full_headcode = self.select_route_and_headcode(spawning_signal_name, trains)
        #Update the first signal of the train's route in case there are multiple choices
        if len(selected_route[0]) == 2:
            selected_route[0][0] = spawning_signal_name
        else:
            selected_route[0] = [spawning_signal_name]
        # Create the new train
        new_train = Train(
            train_id=full_headcode,
            position=spawning_signal.signal_position,
            signal_orientation=spawning_signal.signal_orientation,
            route=selected_route,
            previous_signal_list=selected_route[0],  # Set the previous signal to the spawning signal
            game=self  # Pass the Game instance
        )
        self.trains.append(new_train)
        # Mark the spawning signal as occupied
        spawning_signal.train_at_signal = new_train  # Mark the signal as occupied by the new train
        # Draw the train on the canvas
        # self.drawer.draw_train(new_train.position, new_train.train_id, spawning_signal.signal_orientation)

    def remove_train(self,train):
        self.trains.remove(train)

    def update_signals(self):
        """Update all signals."""
        current_time = time.time()
        for signal in self.signal_details:
            signal.update(self.signal_details, current_time)
            signal.check_queue()

    def update_trains(self):
        """Update all trains."""
        for train in self.trains[:]:  # Use a copy of the list to avoid modification during iteration
            train.move(self.signal_details, self.trains, self.drawer)

    def main_loop(self):
        """Main loop to update all trains and signals."""
        self.update_trains()
        self.update_signals()

        # Redraw the signals and trains
        self.drawer.delete("signal")  # Remove previous signals
        self.drawer.draw_signals(self.signal_details)
        self.drawer.delete("train")  # Remove previous trains
        for train in self.trains:
            self.drawer.draw_train(train.position, train.train_id, train.signal_orientation)

        # Schedule the next iteration of the loop
        self.drawer.set_after(500, self.main_loop)

    def periodic_train_spawning(self, spawning_signal_name, interval=1000, chance=1):
        """Periodically check if a train should spawn at the specified signal."""
        #stop spawning trains after 20
        if len(self.trains) < MAX_TRAIN_NUMBER:
            r = random.random()
            if r < chance:  # Check if a train should spawn
                self.spawn_train(spawning_signal_name, self.trains)

        # Schedule the next check
        self.drawer.set_after(interval, self.periodic_train_spawning, spawning_signal_name, interval, chance)

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
                # Load signal details
        self.load_signal_details_from_json()
        self.drawer = Drawer(self)
        self.drawer.config_canvas(canvas_width, canvas_height,backdrop_photo, root, frame)
        # Draw signals
        self.drawer.draw_signals(self.signal_details)
        # Start periodic train spawning
        for signal_name in PERIODIC_TRAIN_SPAWNING_SIGNALS:
            self.periodic_train_spawning(signal_name, 10000, CHANCE)  # Spawn trains at Signal_1 every 5 seconds with a 1/2 chance
        # Start the main loop
        self.main_loop()

        # Start the GUI event loop
        root.mainloop()

    def get_signal_details(self):
        return self.signal_details    

class SignalDetails:
    def __init__(self,signal_name,signal_position,lamp_position,signal_type,signal_orientation,next_signal_names,conflicting_signals = None,next_signals_in_same_block = None):
        self.signal_name = signal_name
        self.signal_position = signal_position
        self.lamp_position = lamp_position
        self.signal_type = signal_type
        self.signal_orientation = signal_orientation
        self.next_signal_names = next_signal_names
        self.conflicting_signals = conflicting_signals
        self.color = "green"
        self.signal_can_be = None
        self.train_at_signal = None
        self.conflict_timer = 0
        self.last_conflict_state = None
        self.rollback = False
        self.set_by_machine = False
        self.next_signals_in_same_block = next_signals_in_same_block
        self.queue = ""

    def get_signal_object_from_named_list(self, signal_details, signal_name_list):
        result = []
        for signal_name in signal_name_list:
            for signal in signal_details:
                if signal_name == signal.signal_name:
                    result.append(signal)
        return result
    
    def set_signal_color(self, color):
        if self.signal_type == "manual":
            signal_can_be_list = ["red", "yellow", "green"]
            #get index of signal_can_be that color is
            index = signal_can_be_list.index(color)
            #set self.signal_can_be to be everything left and including index
            self.signal_can_be = signal_can_be_list[:(index+1)]
            if (signal_can_be_list.index(self.color) > index) or (self.rollback is True and self.set_by_machine is True):
                self.color = color
                self.set_by_machine = True
        else:
            self.color = color

    def check_conflicting_signals(self, signal_details, current_time):
        if self.conflicting_signals:
            # Find all conflicting signals
            # Get the current train_at_signal state of conflicting signals
            current_conflict_state = [signal.train_at_signal for signal in  self.get_signal_object_from_named_list(signal_details, self.conflicting_signals)]
            # Check if the state is all False
            if all(state==None for state in current_conflict_state):
                # Reset the conflict timer and state if all are False
                self.conflict_timer = 0
                self.last_conflict_state = current_conflict_state

            elif self.last_conflict_state != current_conflict_state:
                # If the state has changed, start the timer
                self.conflict_timer = current_time
                self.set_signal_color("red")
                self.last_conflict_state = current_conflict_state
    

            # Check if the conflict duration has passed
            elif self.conflict_timer > 0 and current_time - self.conflict_timer >= CONFLICT_DURATION:
                # Reset the conflict timer
                self.conflict_timer = 0

    def get_signals_in_same_block(self, signal_name, signals_in_same_block):
        for group in signals_in_same_block:
            if signal_name in group:
                return [s for s in group if s != signal_name]
        return []

    def update(self, signal_details, current_time):
        """Update the signal's state based on its next and conflicting signals."""
        if not self.next_signal_names:  # Skip if next_signals is empty
            return
        # Handle conflicting signals
        self.check_conflicting_signals(signal_details, current_time)
        # Handle auto signals
        if self.conflict_timer != 0:
            return
        next_signals = self.get_signal_object_from_named_list(signal_details, self.next_signal_names)
        if any(next_signal.train_at_signal is not None for next_signal in next_signals):
            if self.train_at_signal is None:
                train_route_next_signal_names = []
            else:
                train_route_next_signal_names = self.train_at_signal.get_next_route_element_name()
            #add next_signals_in_same_block to train_route_next_signal_names
            if self.next_signals_in_same_block:
                train_route_next_signals = self.get_signal_object_from_named_list(signal_details, train_route_next_signal_names)
                for signal in train_route_next_signals:
                    train_route_next_signal_names.extend(self.get_signals_in_same_block(signal.signal_name, self.next_signals_in_same_block))
            available_signals = [signal.signal_name for signal in next_signals if signal.train_at_signal is None]
            if len(set(available_signals).intersection(set(train_route_next_signal_names))) > 0 and (not self.next_signals_in_same_block):
                self.set_signal_color("yellow")
            else:
                self.set_signal_color("red")
        elif any(next_signal.color == "red" for next_signal in next_signals):
            self.set_signal_color("yellow")
        else:
            self.set_signal_color("green")

    def check_queue(self):
        if self.queue != "" and self.queue in self.signal_can_be:
            self.color = self.queue
            self.queue = ""

class Train:
    def __init__(self, train_id, position, route, signal_orientation = "right", previous_signal_list = None, game=None):
        self.train_id = train_id
        self.position = position
        self.route = route
        self.current_index = 0
        self.last_move_time = time.time()
        self.signal_orientation = signal_orientation
        self.previous_signal_list = previous_signal_list
        self.previous_signal_name = ""
        self.game = game

    def update_TRTS(self, current_time, signal_details, drawer):
        dwell_time = self.get_dwell_time()
        if ((current_time - self.last_move_time) >= (dwell_time - TRTS_TIME_BEFORE_DEPARTURE)) and dwell_time != STANDARD_SIGNAL_DWELL_TIME:
            self.flash_TRTS(signal_details, current_time, drawer)

    def get_dwell_time(self):
        if self.previous_signal_list and len(self.previous_signal_list) == 2:
            dwell_time = self.previous_signal_list[1]
        else:
            dwell_time = STANDARD_SIGNAL_DWELL_TIME
        return dwell_time
    
    def get_next_route_element_name(self):
        next_route_element_name = self.route[self.current_index]
        return next_route_element_name[0]  # Get the signal name from the tuple
    
    def time_pass_more_than_dwell_time(self):
        return time.time() - self.last_move_time >= self.get_dwell_time()

    def spawn_train(self, trains):
        if self.game:  # Use the passed Game instance
            self.game.spawn_train(self.previous_signal_name,trains)  # Spawn a train at the previous signal

    def delete_train(self, signal_details, drawer):
        if self.previous_signal_name:
            previous_signal = self.get_signal_object_by_name(signal_details, self.previous_signal_name)  # Ensure there is a previous signal
            if previous_signal:
                previous_signal.train_at_signal = None
                drawer.draw_TRTS(signal_details, self.previous_signal_name, "black")
        self.game.remove_train(self)  # Remove the train from the list of trains

    def get_signal_object_by_name(self, signal_list, signal_name):
        for signal in signal_list:
            if signal.signal_name == signal_name:
                return signal
        return None        
    
    def flash_TRTS(self, signal_details, current_time, drawer):
        if int(str(round(current_time-self.get_dwell_time(),1))[-1]) >= 5:
            drawer.draw_TRTS(signal_details, self.previous_signal_name, "white")
        else:
            drawer.draw_TRTS(signal_details, self.previous_signal_name, "black")
                        
    def move(self, signal_details, trains, drawer):
        """Move the train to the next signal in its route if 1 second has passed and the previous signal is not red."""
        current_time = time.time()
        self.update_TRTS(current_time, signal_details, drawer)

        if not self.time_pass_more_than_dwell_time() or self.current_index >= len(self.route):
            return
        
        # Get the current signal details
        if type(self.get_next_route_element_name()) == list:  # Handle multiple platforms
            # Find all signals in the list
            next_route_signals = []
            for signal_name in self.get_next_route_element_name():
                next_route_signals.append(self.get_signal_object_by_name(signal_details, signal_name))

            # Filter out None values and signals with train_at_signal == True
            available_signals = [signal for signal in next_route_signals if signal and signal.train_at_signal is None]
            if not available_signals:
                return  # Do not move if all platforms are occupied
            # Randomly select a platform if more than one is available
            else:
                selected_signal = random.choice(available_signals)
        else:
            selected_signal = self.get_signal_object_by_name(signal_details, self.get_next_route_element_name())

        # Check if the train has reached the "delete_and_spawn_train" signal
        if self.get_next_route_element_name() == "delete_and_spawn_train":
            self.delete_train(signal_details, drawer)
            self.spawn_train(trains)
            return

        # Check if the train has reached the "delete" signal
        if self.get_next_route_element_name() == "delete":
            self.delete_train(signal_details, drawer)
            return

        # Check the previous signal's color
        if self.previous_signal_name:  # Ensure there is a previous signal
            previous_signal = self.get_signal_object_by_name(signal_details, self.previous_signal_name)
            if previous_signal and previous_signal.color == "red":
                if self.get_dwell_time() != STANDARD_SIGNAL_DWELL_TIME:
                    self.flash_TRTS(signal_details, current_time, drawer)
                return  # Do not move if the previous signal is red

        # Set the previous signal's train_at_signal to False
        if self.previous_signal_name:
            if previous_signal := self.get_signal_object_by_name(signal_details, self.previous_signal_name):
                drawer.draw_TRTS(signal_details, self.previous_signal_name, "black")
                previous_signal.train_at_signal = None

        # Set the next signal's train_at_signal to True
        if selected_signal:
            selected_signal.train_at_signal = self
            self.position = selected_signal.signal_position  # Update train position
            self.signal_orientation = selected_signal.signal_orientation  # Update signal position (left or right)

        # Update the previous signal name and move to the next signal
        next_route_signal_list = self.route[self.current_index]
        if len(next_route_signal_list) == 2:
            self.previous_signal_list = next_route_signal_list
        else:
            self.previous_signal_list = None  # Reset the previous signal tuple
        self.previous_signal_name = selected_signal.signal_name
        self.last_move_time = current_time
        self.current_index += 1

def main():
    Game(SIGNAL_DETAILS_FILENAME, BACKDROP_PATH_FILENAME).run()

if __name__ == "__main__":
    main()