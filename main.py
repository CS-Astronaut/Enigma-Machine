import tkinter as tk
from tkinter import ttk, font
import math
import time
import random
import os

class EnigmaRotor:
    # Historical Enigma rotor wirings
    HISTORICAL_ROTORS = {
        'I': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ',
        'II': 'AJDKSIRUXBLHWTMCQGZNPYFVOE',
        'III': 'BDFHJLCPRTXVZNYEIWGAKMUSQO',
        'IV': 'ESOVPZJAYQUIRHXLNFTGKDCMWB',
        'V': 'VZBRGITYUPSDNHLXAWMJQOFECK',
        'VI': 'JPGVOUMFYQBENHZRDKASXLICTW',
        'VII': 'NZJHGRCXMYSWBOUFAIVLPEKQDT',
        'VIII': 'FKQHTLXOCBJSPDZRAMEWNIUYGV',
        'Beta': 'LEYJVCNIXWPBQMDRTAKZGFUHOS',
        'Gamma': 'FSOKANUERHMBTIYCWLQPZXVGJD'
    }
    
    # Historical rotor notch positions
    NOTCH_POSITIONS = {
        'I': 'Q',        # Notch at position 16 (Q)
        'II': 'E',       # Notch at position 4 (E)
        'III': 'V',      # Notch at position 21 (V)
        'IV': 'J',       # Notch at position 9 (J)
        'V': 'Z',        # Notch at position 25 (Z)
        'VI': 'ZM',      # Notches at positions 25 (Z) and 12 (M)
        'VII': 'ZM',     # Notches at positions 25 (Z) and 12 (M)
        'VIII': 'ZM',    # Notches at positions 25 (Z) and 12 (M)
        'Beta': '',      # No notches on Beta rotor
        'Gamma': ''      # No notches on Gamma rotor
    }
    
    def __init__(self, rotor_type, ring_setting=0, initial_position='A'):
        self.rotor_type = rotor_type
        self.wiring = self.HISTORICAL_ROTORS[rotor_type]
        self.notches = self.NOTCH_POSITIONS[rotor_type]
        self.ring_setting = ord(ring_setting) - ord('A') if isinstance(ring_setting, str) else ring_setting
        self.position = ord(initial_position) - ord('A') if isinstance(initial_position, str) else initial_position
        
        
    def forward_mapping(self, input_char):
        # Convert character to index (0-25)
        char_idx = ord(input_char) - ord('A')
        
        # Apply position and ring setting offset
        offset_idx = (char_idx + self.position - self.ring_setting) % 26
        
        # Find the mapped character in the wiring
        mapped_char = self.wiring[offset_idx]
        
        # Apply position and ring setting offset in reverse
        output_idx = (ord(mapped_char) - ord('A') - self.position + self.ring_setting) % 26
        
        # Convert back to character
        return chr(output_idx + ord('A'))
    
    def backward_mapping(self, input_char):
        # Convert character to index (0-25)
        char_idx = ord(input_char) - ord('A')
        
        # Apply position and ring setting offset
        offset_idx = (char_idx + self.position - self.ring_setting) % 26
        
        # Find the position of the input character in the wiring
        mapped_idx = self.wiring.index(chr(offset_idx + ord('A')))
        
        # Apply position and ring setting offset in reverse
        output_idx = (mapped_idx - self.position + self.ring_setting) % 26
        
        # Convert back to character
        return chr(output_idx + ord('A'))
    
    def rotate(self):
        self.position = (self.position + 1) % 26
        return self.is_at_notch()
    
    def is_at_notch(self):
        return chr(self.position + ord('A')) in self.notches
    
    def get_display_letter(self):
        return chr((self.position) % 26 + ord('A'))

class EnigmaReflector:
    # Historical Enigma reflector wirings
    HISTORICAL_REFLECTORS = {
        'A': 'EJMZALYXVBWFCRQUONTSPIKHGD',
        'B': 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
        'C': 'FVPJIAOYEDRZXWGCTKUQSBNMHL',
        'BThin': 'ENKQAUYWJICOPBLMDXZVFTHRGS',
        'CThin': 'RDOBJNTKVEHMLFCWZAXGYIPSUQ'
    }
    
    def __init__(self, reflector_type):
        self.reflector_type = reflector_type
        self.wiring = self.HISTORICAL_REFLECTORS[reflector_type]
    
    def reflect(self, input_char):
        # Convert character to index (0-25)
        char_idx = ord(input_char) - ord('A')
        
        # Find the mapped character in the wiring
        mapped_char = self.wiring[char_idx]
        
        return mapped_char

class EnigmaPlugboard:
    def __init__(self):
        self.connections = {}
    
    def add_connection(self, char1, char2):
        self.connections[char1] = char2
        self.connections[char2] = char1
    
    def process(self, input_char):
        return self.connections.get(input_char, input_char)

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard=None):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard if plugboard else EnigmaPlugboard()
        self.keyboard = "QWERTZUIOASDFGHJKPYXCVBNML"
        self.last_key = None
        self.last_lamp = None
        self.signal_path = []
    
    def process_letter(self, letter):
        if not letter.isalpha():
            return letter
            
        upper_letter = letter.upper()
        self.signal_path = []
        
        # Track signal path
        current_letter = upper_letter
        self.signal_path.append(('input', current_letter))
        
        # Step 1: Rotate rotors
        self._rotate_rotors()
        
        # Step 2: Pass through plugboard
        current_letter = self.plugboard.process(current_letter)
        self.signal_path.append(('plugboard', current_letter))
        
        # Step 3: Pass through rotors (forward)
        for i, rotor in enumerate(reversed(self.rotors)):
            current_letter = rotor.forward_mapping(current_letter)
            self.signal_path.append((f'rotor_{len(self.rotors) - i} forward', current_letter))
        
        # Step 4: Pass through reflector
        current_letter = self.reflector.reflect(current_letter)
        self.signal_path.append(('reflector', current_letter))
        
        # Step 5: Pass back through rotors (backward)
        for i, rotor in enumerate(self.rotors):
            current_letter = rotor.backward_mapping(current_letter)
            self.signal_path.append((f'rotor_{i+1} backward', current_letter))
        
        # Step 6: Pass back through plugboard
        current_letter = self.plugboard.process(current_letter)
        self.signal_path.append(('plugboard out', current_letter))
        
        self.last_key = upper_letter
        self.last_lamp = current_letter
        
        return current_letter
    
    def _rotate_rotors(self):
        # Implement the correct Enigma stepping mechanism with double-stepping
        
        # Check if middle rotor is at notch position (double-stepping)
        middle_at_notch = False
        if len(self.rotors) > 1:
            middle_at_notch = self.rotors[1].is_at_notch()
        
        # Check if rightmost (fast) rotor is at notch position
        rightmost_at_notch = self.rotors[-1].is_at_notch()
        
        # Determine which rotors should turn
        rotate_leftmost = middle_at_notch and len(self.rotors) > 2
        rotate_middle = rightmost_at_notch or middle_at_notch
        rotate_rightmost = True  # The rightmost rotor always rotates
        
        # Rotate the rotors as needed
        if rotate_leftmost:
            self.rotors[0].rotate()
        if rotate_middle and len(self.rotors) > 1:
            self.rotors[1].rotate()
        if rotate_rightmost and len(self.rotors) > 0:
            self.rotors[-1].rotate()
    
    def encrypt_message(self, message):
        encrypted = []
        for char in message:
            encrypted.append(self.process_letter(char))
        return ''.join(encrypted)
    
    def get_rotor_positions(self):
        return [rotor.get_display_letter() for rotor in self.rotors]
    
    def get_signal_path(self):
        return self.signal_path
    
    def get_keyboard_layout(self):
        return self.keyboard



class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg='#8B7D6B', **kwargs):
        super().__init__(container, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)


        self.scrollable_frame = tk.Frame(self.canvas, bg=bg,padx=20, pady=30)

        # Update the scroll region when the size of the scrollable_frame changes.
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create a window window inside the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Add mouse wheel support  
        self.canvas.bind("<Enter>", self._activate_scroll)
        self.canvas.bind("<Leave>", self._deactivate_scroll)


        # Link the scrollbar and the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Make sure the inner frame's width tracks the canvas's width
        self.bind("<Configure>", self._on_parent_configure)

    def _activate_scroll(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _deactivate_scroll(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # FIXED Complete the frame configuration handler
    def _on_parent_configure(self, event):
        """Update the scrollable frame's width to match parent"""
        if self.scrollable_frame.winfo_reqwidth() != event.width:
            self.canvas.itemconfig(self.canvas_window, width=event.width)


class EnigmaSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enigma Machine Simulator")
        self.root.configure(bg='#8B7D6B')
        self.root.geometry("1250x1000")
        
        # Set up custom fonts
        self.enigma_font = font.Font(family='Courier', size=14, weight='bold')
        self.rotor_font = font.Font(family='Courier', size=12, weight='bold')
        self.lamp_font = font.Font(family='Courier', size=16, weight='bold')
        self.title_font = font.Font(family='Times', size=24, weight='bold')
        
        # Available rotors and reflectors
        self.available_rotors = list(EnigmaRotor.HISTORICAL_ROTORS.keys())
        self.available_reflectors = list(EnigmaReflector.HISTORICAL_REFLECTORS.keys())
        
        # Initialize Enigma machine with default configuration
        rotors = [
            EnigmaRotor('I', 'A', 'A'),
            EnigmaRotor('II', 'A', 'A'),
            EnigmaRotor('III', 'A', 'A')
        ]
        reflector = EnigmaReflector('B')
        plugboard = EnigmaPlugboard()
        self.enigma = EnigmaMachine(rotors, reflector, plugboard)
        
        # Input and output text
        self.input_text = ""
        self.output_text = ""
        
        # Animation state
        self.animation_in_progress = False
        self.signal_path_idx = 0
        self.animation_speed = 500  # milliseconds

        # Add scrollbar styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
            background='#666666',
            troughcolor='#8B7D6B',
            bordercolor='#5D5D5D',
            arrowcolor='#FFFFFF',
            gripcount=0,
            width=16
        )

        self.setup_ui()



    def input_key_handler(self, event):
        # Only process key events if the input widget has focus.
        if self.input_display != self.root.focus_get():
            return "break"

        # Block keys such as BackSpace, Delete, and arrow keys if needed.
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down"):
            return "break"

        # If a printable character is pressed, append it to the input.
        if event.char and event.char.isprintable():
            ch = event.char.upper()  # Convert to uppercase
            self.input_display.config(state='normal')
            self.input_display.insert("end", ch)
            self.input_display.config(state='disabled')
            # After a short delay (200 ms here), process the key
            self.root.after(200, lambda: self.process_key(ch))
        return "break"
    
    def setup_ui(self):
        # Replace your existing main_frame initialization with the following:
        scroll_frame = ScrollableFrame(self.root, bg='#8B7D6B')
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        main_frame = scroll_frame.scrollable_frame  # Use this as your new main_frame



        
        # Title
        title_label = tk.Label(main_frame, text="ENIGMA MACHINE", font=self.title_font, 
                              bg='#8B7D6B', fg='#2F2F2F')
        credit_label = tk.Label(main_frame, text="By CS-Astronaut", font=self.enigma_font, 
                              bg='#8B7D6B', fg='#2F2F2F')

        title_label.pack(pady=(0, 20))
        credit_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = tk.Frame(main_frame, bg='#8B7D6B', relief=tk.RIDGE, bd=5)
        settings_frame.pack(fill=tk.X, pady=(0, 20))

        
        # Setup rotor selection
        rotor_frame = tk.Frame(settings_frame, bg='#8B7D6B')
        rotor_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(rotor_frame, text="Rotor Selection", font=self.rotor_font, 
                bg='#8B7D6B', fg='#2F2F2F').pack()
        
        # Rotor selection dropdowns
        self.rotor_vars = []
        self.rotor_pos_vars = []
        self.rotor_ring_vars = []
        
        for i in range(3):
            rotor_row = tk.Frame(rotor_frame, bg='#8B7D6B')
            rotor_row.pack(anchor=tk.W, pady=5)
            
            tk.Label(rotor_row, text=f"Rotor {i+1}:", bg='#8B7D6B', fg='#2F2F2F', 
                    width=8, anchor=tk.W).pack(side=tk.LEFT)
            
            rotor_var = tk.StringVar(value=self.enigma.rotors[i].rotor_type)
            rotor_dropdown = ttk.Combobox(rotor_row, textvariable=rotor_var, values=self.available_rotors, width=5)
            rotor_dropdown.pack(side=tk.LEFT, padx=5)
            self.rotor_vars.append(rotor_var)
            
            tk.Label(rotor_row, text="Position:", bg='#8B7D6B', fg='#2F2F2F').pack(side=tk.LEFT, padx=(10, 0))
            pos_var = tk.StringVar(value=self.enigma.rotors[i].get_display_letter())
            pos_dropdown = ttk.Combobox(rotor_row, textvariable=pos_var, 
                                       values=[chr(65+j) for j in range(26)], width=2)
            pos_dropdown.pack(side=tk.LEFT, padx=5)
            self.rotor_pos_vars.append(pos_var)
            
            tk.Label(rotor_row, text="Ring:", bg='#8B7D6B', fg='#2F2F2F').pack(side=tk.LEFT, padx=(10, 0))
            ring_var = tk.StringVar(value=chr(self.enigma.rotors[i].ring_setting + ord('A')))
            ring_dropdown = ttk.Combobox(rotor_row, textvariable=ring_var, 
                                        values=[chr(65+j) for j in range(26)], width=2)
            ring_dropdown.pack(side=tk.LEFT, padx=5)
            self.rotor_ring_vars.append(ring_var)
        
        # Reflector selection
        reflector_frame = tk.Frame(settings_frame, bg='#8B7D6B')
        reflector_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(reflector_frame, text="Reflector", font=self.rotor_font, 
                bg='#8B7D6B', fg='#2F2F2F').pack()
        
        reflector_row = tk.Frame(reflector_frame, bg='#8B7D6B')
        reflector_row.pack(pady=5)
        
        tk.Label(reflector_row, text="Type:", bg='#8B7D6B', fg='#2F2F2F', 
                width=6, anchor=tk.W).pack(side=tk.LEFT)
        
        self.reflector_var = tk.StringVar(value=self.enigma.reflector.reflector_type)
        reflector_dropdown = ttk.Combobox(reflector_row, textvariable=self.reflector_var, 
                                        values=self.available_reflectors, width=5)
        reflector_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Plugboard
        plugboard_frame = tk.Frame(settings_frame, bg='#8B7D6B')
        plugboard_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(plugboard_frame, text="Plugboard", font=self.rotor_font, 
                bg='#8B7D6B', fg='#2F2F2F').pack()
        
        self.plugboard_var = tk.StringVar(value="")
        plugboard_entry = tk.Entry(plugboard_frame, textvariable=self.plugboard_var, width=20)
        plugboard_entry.pack(pady=5)
        tk.Label(plugboard_frame, text="Format: AB CD EF...", bg='#8B7D6B', fg='#2F2F2F').pack()



        # Mode Selection: Fast Mode or Learning Mode
        mode_frame = tk.Frame(settings_frame, bg='#8B7D6B')
        mode_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(mode_frame, text="Mode:", font=self.rotor_font, 
                 bg='#8B7D6B', fg='#2F2F2F').pack()

        self.mode_var = tk.StringVar(value="fast")  # Default: Learning mode

        learning_mode_rb = tk.Radiobutton(mode_frame, text="Learning", variable=self.mode_var, value="learning",
                                          bg='#8B7D6B', fg='#2F2F2F', selectcolor='#8B7D6B')
        learning_mode_rb.pack(anchor="w")  # Stacks vertically, left-aligned

        fast_mode_rb = tk.Radiobutton(mode_frame, text="Fast", variable=self.mode_var, value="fast",
                                      bg='#8B7D6B', fg='#2F2F2F', selectcolor='#8B7D6B')
        fast_mode_rb.pack(anchor="w")  # Stacks below the first button, left-aligned



        
        # Apply settings button
        apply_button = tk.Button(settings_frame, text="Apply Settings", command=self.apply_settings, 
                               bg='#4A4A4A', fg='white', font=self.rotor_font, padx=10)
        apply_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Reset button
        reset_button = tk.Button(settings_frame, text="Reset", command=self.reset_machine, 
                               bg='#4A4A4A', fg='white', font=self.rotor_font, padx=10)
        reset_button.pack(side=tk.LEFT, padx=0, pady=10)



        
        # Display frame for rotor visualization
        self.display_frame = tk.Frame(main_frame, bg='#5D5D5D', relief=tk.RIDGE, bd=5)
        self.display_frame.pack(fill=tk.BOTH, pady=(0, 20), ipady=10)
        
        # Rotor display
        rotor_display = tk.Frame(self.display_frame, bg='#5D5D5D')
        rotor_display.pack(fill=tk.Y, padx=20, pady=10)
        
        # Create canvases for rotors
        self.rotor_canvases = []
        
        # First create reflector display
        reflector_frame = tk.Frame(rotor_display, bg='#5D5D5D')
        reflector_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(reflector_frame, text="Reflector", font=self.rotor_font, 
                bg='#5D5D5D', fg='white').pack()
        
        self.reflector_canvas = tk.Canvas(reflector_frame, width=100, height=300, 
                                         bg='#3A3A3A', highlightthickness=0)
        self.reflector_canvas.pack()
        
        # Create frames for each rotor
        for i in range(3):
            rotor_frame = tk.Frame(rotor_display, bg='#5D5D5D')
            rotor_frame.pack(side=tk.LEFT, padx=10)
            
            tk.Label(rotor_frame, text=f"Rotor {i+1}", font=self.rotor_font, 
                    bg='#5D5D5D', fg='white').pack()
            
            canvas = tk.Canvas(rotor_frame, width=100, height=350, bg='#3A3A3A', highlightthickness=0)
            canvas.pack()
            self.rotor_canvases.append(canvas)
        
        # Plugboard display
        plugboard_frame = tk.Frame(rotor_display, bg='#5D5D5D')
        plugboard_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(plugboard_frame, text="Plugboard", font=self.rotor_font, 
                bg='#5D5D5D', fg='white').pack()
        
        self.plugboard_canvas = tk.Canvas(plugboard_frame, width=120, height=300, 
                                         bg='#3A3A3A', highlightthickness=0)
        self.plugboard_canvas.pack()
        
        # Signal flow canvas
        signal_frame = tk.Frame(self.display_frame, bg='#5D5D5D')
        signal_frame.pack(fill=tk.X, pady=10)
        
        self.signal_canvas = tk.Canvas(signal_frame, height=100, bg='#3A3A3A', highlightthickness=0)
        self.signal_canvas.pack(fill=tk.X, padx=20)
        
        # Text area for input/output display
        text_frame = tk.Frame(main_frame, bg='#5D5D5D', relief=tk.RIDGE, bd=5)
        text_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_frame = tk.Frame(text_frame, bg='#5D5D5D', pady=10)
        input_frame.pack(fill=tk.X)
        tk.Label(input_frame, text="Input Text:", font=self.enigma_font, 
                bg='#5D5D5D', fg='white').pack(side=tk.LEFT, padx=10)

        # Use a Text widget instead of a Label so the text can be selected and copied.
        self.input_display = tk.Text(input_frame, font=self.enigma_font, 
                                    bg='#3A3A3A', fg='white', width=50, height=2, wrap="word",
                                    padx=10, pady=5, relief=tk.SUNKEN)
        self.input_display.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Bind focus events
        self.input_display.bind("<FocusIn>", self.on_focus)
        self.input_display.bind("<FocusOut>", self.on_unfocus)
        
        self.input_display.focus_set()
        self.input_display.bind("<Key>", self.input_key_handler)
        
        
        output_frame = tk.Frame(text_frame, bg='#5D5D5D', pady=10)
        output_frame.pack(fill=tk.X)
        tk.Label(output_frame, text="Output Text:", font=self.enigma_font, 
                 bg='#5D5D5D', fg='white').pack(side=tk.LEFT, padx=10)

        # Use a Text widget for the output, set to read-only so users can select/copy but not edit.
        self.output_display = tk.Text(output_frame, font=self.enigma_font, 
                                      bg='#3A3A3A', fg='white', width=50, height=2, wrap="word",
                                      padx=10, pady=5, relief=tk.SUNKEN)
        self.output_display.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # Disable editing while allowing selection:
        self.output_display.config(state='disabled')


        
        # Lampboard
        lampboard_frame = tk.Frame(main_frame, bg='#5D5D5D', relief=tk.RIDGE, bd=5)
        lampboard_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create lampboard display
        self.create_lampboard(lampboard_frame)
        
        # Keyboard
        keyboard_frame = tk.Frame(main_frame, bg='#5D5D5D', relief=tk.RIDGE, bd=5)
        keyboard_frame.pack(fill=tk.X)
        
        # Create keyboard
        self.create_keyboard(keyboard_frame)
        
        # Bind keys
        ##self.root.bind("<Key>", self.handle_key_press)
        
        # Draw initial rotors
        self.draw_rotors()
        self.draw_reflector()
        self.draw_plugboard()

    def on_focus(self, event):
        """Change input frame background to orange when focused."""
        event.widget.master.config(bg="#FFA500")  # Use your original orange color
    
    def on_unfocus(self, event):
        """Reset input frame background when focus is lost."""
        event.widget.master.config(bg="#5D5D5D")  # Restore the original background
    
    
    def create_lampboard(self, parent):
        lampboard = tk.Frame(parent, bg='#5D5D5D', padx=20, pady=10)
        lampboard.pack()
        
        tk.Label(lampboard, text="LAMPBOARD", font=self.enigma_font, 
                bg='#5D5D5D', fg='white').pack(pady=(0, 10))
        
        self.lamps = {}
        
        # Use the keyboard layout from the Enigma machine
        keyboard_layout = [
            "QWERTZUIO",
            "ASDFGHJK",
            "PYXCVBNML"
        ]
        
        for row_idx, row in enumerate(keyboard_layout):
            lamp_row = tk.Frame(lampboard, bg='#5D5D5D')
            lamp_row.pack(pady=5)
            
            for char in row:
                lamp_frame = tk.Frame(lamp_row, width=50, height=50, relief=tk.RAISED,
                                     bg='#3A3A3A', bd=3)
                lamp_frame.pack_propagate(False)  # Prevent widgets inside from changing the frame size
                lamp_frame.pack(side=tk.LEFT, padx=5)
                
                lamp_label = tk.Label(lamp_frame, text=char, font=self.lamp_font, fg='white', bg='#3A3A3A')
                lamp_label.pack(expand=True)
                self.lamps[char] = lamp_label
    
    def create_keyboard(self, parent):
        keyboard = tk.Frame(parent, bg='#5D5D5D', padx=20, pady=10)
        keyboard.pack()
        
        tk.Label(keyboard, text="KEYBOARD", font=self.enigma_font, 
                bg='#5D5D5D', fg='white').pack(pady=(0, 10))
        
        self.keys = {}
        
        # Use the keyboard layout from the Enigma machine
        keyboard_layout = [
            "QWERTZUIO",
            "ASDFGHJK",
            "PYXCVBNML"
        ]
        
        for row_idx, row in enumerate(keyboard_layout):
            key_row = tk.Frame(keyboard, bg='#5D5D5D')
            key_row.pack(pady=5)
            
            for char in row:
                key_frame = tk.Frame(key_row, width=50, height=50, relief=tk.RAISED,
                                    bg='#4A4A4A', bd=3)
                key_frame.pack_propagate(False)  # Prevent widgets inside from changing the frame size
                key_frame.pack(side=tk.LEFT, padx=5)
                
                key_label = tk.Label(key_frame, text=char, font=self.lamp_font, fg='white', bg='#4A4A4A')
                key_label.pack(expand=True)
                
                # Make it clickable
                key_frame.bind("<Button-1>", lambda e, char=char: self.process_key(char))
                key_label.bind("<Button-1>", lambda e, char=char: self.process_key(char))
                
                self.keys[char] = key_frame
    
    def handle_key_press(self, event):
        key = event.char.upper()
        if key.isalpha():
            self.process_key(key)
    
    def process_key(self, key):
        if self.animation_in_progress:
            return
        
        # Press key animation
        if key in self.keys:
            self.keys[key].config(relief=tk.SUNKEN)
            self.root.after(100, lambda: self.keys[key].config(relief=tk.RAISED))
        
        # Update text
        self.input_text += key
        output_char = self.enigma.process_letter(key)
        self.output_text += output_char
        
        # Update displays
        self.output_display.config(state='normal')
        self.output_display.delete("1.0", tk.END)   
        self.output_display.insert("1.0", self.output_text)
        self.output_display.config(state='disabled')
        
        # Update rotor positions
        self.draw_rotors()
        
        # Light up the lamp
        if output_char in self.lamps:
            # Start animation
            self.animation_in_progress = True
            self.signal_path_idx = 0
            self.animate_signal_flow()
    
    def animate_signal_flow(self):
        if self.signal_path_idx >= len(self.enigma.get_signal_path()):
            # Animation complete - light final lamp
            final_char = self.enigma.last_lamp
            if final_char in self.lamps:
                self.lamps[final_char].config(bg='#FFA500', fg='black')  # Light up in orange

                if self.mode_var.get() == "fast":  # Fast mode: Show all fast
                    self.root.after(200, lambda: self.lamps[final_char].config(bg='#3A3A3A', fg='white'))  # Turn off
                else:
                    self.root.after(self.animation_speed, lambda: self.lamps[final_char].config(bg='#3A3A3A', fg='white'))  # Turn off                    
            
            self.animation_in_progress = False
            return
        
        # Draw current state of signal flow
        self.draw_signal_flow(self.signal_path_idx)
        
        # Increment and schedule next frame
        self.signal_path_idx += 1
        
        if self.mode_var.get() == "fast":  # Fast mode: Show all fast
            self.animation_speed = 20
        else: self.animation_speed = 400

        self.root.after(self.animation_speed, self.animate_signal_flow)
    



    def draw_signal_flow(self, idx):
        # Clear signal canvas
        self.signal_canvas.delete("all")
        
        signal_path = self.enigma.get_signal_path()
        if idx < len(signal_path):
            stage, char = signal_path[idx]
            
            # Draw a representation of the current stage
            width = self.signal_canvas.winfo_width()
            height = self.signal_canvas.winfo_height()
            
            # Create a flow diagram showing the letter traveling through components
            stages = ["input", "plugboard", "rotor_3 forward", "rotor_2 forward", 
                     "rotor_1 forward", "reflector", "rotor_1 backward", 
                     "rotor_2 backward", "rotor_3 backward", "plugboard out"]
            
            stage_positions = {}
            for i, s in enumerate(stages):
                stage_positions[s] = (width * (i + 1) / (len(stages) + 1), height / 2)
            
            # Draw all stages
            for i, s in enumerate(stages):
                x, y = stage_positions[s]
                self.signal_canvas.create_oval(x-15, y-15, x+15, y+15, fill="#2F2F2F")
                self.signal_canvas.create_text(x, y+25, text=s.split(" ")[0], fill="white")
            
            # Find position of current stage
            current_stage = stage
            if "rotor" in current_stage:
                parts = current_stage.split(" ")
                if len(parts) > 1:
                    # Normalize the stage name to match our stages list
                    current_stage = parts[0] + " " + parts[1]
            
            # Find the closest stage in our pre-defined list
            closest_stage = None
            for s in stages:
                if current_stage in s:
                    closest_stage = s
                    break
            
            if closest_stage:
                x, y = stage_positions[closest_stage]
                # Highlight current stage
                self.signal_canvas.create_oval(x-20, y-20, x+20, y+20, outline="#FFA500", width=3)
                # Display current character
                self.signal_canvas.create_text(x, y, text=char, fill="white", font=self.enigma_font)
                
                # Draw arrows between stages

            # Draw arrows between stages
                for i in range(len(stages) - 1):
                    x1, y1 = stage_positions[stages[i]]
                    x2, y2 = stage_positions[stages[i+1]]
                    
                    # Determine arrow color
                    arrow_color = "#555555"  # Default color
                    if i < stages.index(closest_stage):
                        arrow_color = "#AAAAAA"  # Passed stages
                    
                    # Draw the arrow
                    self.signal_canvas.create_line(x1+15, y1, x2-15, y2, fill=arrow_color, arrow=tk.LAST)


    def draw_rotors(self):
        # For each rotor, draw a visual representation
        for i, rotor in enumerate(self.enigma.rotors):
            canvas = self.rotor_canvases[i]
            canvas.delete("all")
            
            # Draw rotor cylinder
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Draw rotor body
            canvas.create_rectangle(10, 50, width-10, height-50, fill='#6B5B45', outline='#2F2F2F', width=2)
            
            # Get current rotor wiring
            rotor_type = rotor.rotor_type
            wiring = EnigmaRotor.HISTORICAL_ROTORS[rotor_type]
            
            # Rotor type display
            canvas.create_text(width/2, 20, text=f"Type {rotor_type}", font=self.rotor_font, fill='white')
            
            # Display current position
            position_letter = rotor.get_display_letter()
            canvas.create_rectangle(width/2-15, 75, width/2+15, 105, fill='white', outline='black')
            canvas.create_text(width/2, 90, text=position_letter, font=self.rotor_font, fill='black')
            
            # Indicate notch positions
            notches = EnigmaRotor.NOTCH_POSITIONS[rotor_type]
            
            canvas.create_text(width/2, height-30, text=f"Notch: {notches}", font=self.rotor_font, fill='white')
            
            # Show wiring visualization (simplified)
            start_y = 120
            spacing = 15
            
            # Show a few letters and their mappings
            display_count = min(10, len(wiring))
            for j in range(display_count):
                # Input letter
                input_letter = chr(j + ord('A'))
                
                # Apply the rotor's forward mapping to this letter
                output_idx = (wiring.find(input_letter) - rotor.position + rotor.ring_setting) % 26
                output_letter = chr(output_idx + ord('A'))
                
                # Draw the mapping
                canvas.create_text(width/2-20, start_y + j*spacing, text=input_letter, font=self.rotor_font, fill='white')
                canvas.create_text(width/2+20, start_y + j*spacing, text=output_letter, font=self.rotor_font, fill='white')
                canvas.create_line(width/2-15, start_y + j*spacing, width/2+15, start_y + j*spacing, fill='white')
    
    def draw_reflector(self):
        # Draw reflector visualization
        canvas = self.reflector_canvas
        canvas.delete("all")
        
        # Get dimensions
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Draw reflector body
        canvas.create_rectangle(10, 50, width-10, height-50, fill='#696969', outline='#2F2F2F', width=2)
        
        # Get reflector type
        reflector_type = self.enigma.reflector.reflector_type
        canvas.create_text(width/2, 20, text=f"Type {reflector_type}", font=self.rotor_font, fill='white')
        
        # Show some reflector mappings
        wiring = EnigmaReflector.HISTORICAL_REFLECTORS[reflector_type]
        
        start_y = 80
        spacing = 15
        
        # Show a few mappings
        display_count = min(10, len(wiring)//2)
        for j in range(display_count):
            # Input letter
            input_letter = chr(j + ord('A'))
            
            # Get output letter from reflector
            output_letter = wiring[j]
            
            # Draw the mapping
            canvas.create_text(width/2-20, start_y + j*spacing, text=input_letter, font=self.rotor_font, fill='white')
            canvas.create_text(width/2+20, start_y + j*spacing, text=output_letter, font=self.rotor_font, fill='white')
            
            # Draw connecting line
            canvas.create_line(width/2-15, start_y + j*spacing, width/2+15, start_y + j*spacing, 
                             fill='white', arrow=tk.BOTH)
    
    def draw_plugboard(self):
        # Visualize the plugboard connections
        canvas = self.plugboard_canvas
        canvas.delete("all")
        
        # Get dimensions
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Draw plugboard body
        canvas.create_rectangle(10, 50, width-10, height-50, fill='#4A4A4A', outline='#2F2F2F', width=2)
        
        # Draw title
        canvas.create_text(width/2, 20, text="Connections", font=self.rotor_font, fill='white')
        
        # Get connections
        connections = self.enigma.plugboard.connections
        
        # Draw connections
        start_y = 80
        spacing = 20
        drawn_pairs = set()
        
        # Draw each connection pair (but only once)
        row = 0
        for char1, char2 in connections.items():
            if (char1, char2) not in drawn_pairs and (char2, char1) not in drawn_pairs:
                drawn_pairs.add((char1, char2))
                
                canvas.create_text(width/2-15, start_y + row*spacing, text=char1, font=self.rotor_font, fill='white')
                canvas.create_text(width/2+15, start_y + row*spacing, text=char2, font=self.rotor_font, fill='white')
                
                # Draw connecting line
                canvas.create_line(width/2-10, start_y + row*spacing, width/2+10, start_y + row*spacing, 
                                 fill='white', width=2)
                
                row += 1
                if row >= 10:  # Maximum display
                    break
    
    def apply_settings(self):
        # Create new rotors based on settings
        new_rotors = []
        for i in range(3):
            rotor_type = self.rotor_vars[i].get()
            position = self.rotor_pos_vars[i].get()
            ring_setting = self.rotor_ring_vars[i].get()
            
            new_rotors.append(EnigmaRotor(rotor_type, ring_setting, position))
        
        # Create new reflector
        reflector_type = self.reflector_var.get()
        new_reflector = EnigmaReflector(reflector_type)
        
        # Create new plugboard
        new_plugboard = EnigmaPlugboard()
        plugboard_text = self.plugboard_var.get().upper()
        pairs = plugboard_text.split()
        
        for pair in pairs:
            if len(pair) == 2 and pair[0].isalpha() and pair[1].isalpha():
                new_plugboard.add_connection(pair[0], pair[1])
        
        # Create new Enigma machine
        self.enigma = EnigmaMachine(new_rotors, new_reflector, new_plugboard)
        
        # Reset text
        self.input_text = ""
        self.output_text = ""

        self.input_display.config(state='normal')  # Enable editing temporarily
        self.input_display.delete("1.0", tk.END)     # Clear all text
        self.input_display.config(state='disabled')  # Disable editing if needed
        
        self.output_display.config(state='normal')  # Enable editing temporarily
        self.output_display.delete("1.0", tk.END)     # Clear all text from the widget
        self.output_display.config(state='disabled')  # Re-disable editing if needed
        
        # Update displays
        self.draw_rotors()
        self.draw_reflector()
        self.draw_plugboard()

        # Set focus for entry on input frame
        self.input_display.focus_set()

    
    def reset_machine(self):
        # Reset the initial rotors
        rotors = [
            EnigmaRotor('I', 'A', 'A'),
            EnigmaRotor('II', 'A', 'A'),
            EnigmaRotor('III', 'A', 'A')
        ]
        reflector = EnigmaReflector('B')
        plugboard = EnigmaPlugboard()
        
        # Reset the Enigma machine
        self.enigma = EnigmaMachine(rotors, reflector, plugboard)
        
        # Reset variables
        for i in range(3):
            self.rotor_vars[i].set(rotors[i].rotor_type)
            self.rotor_pos_vars[i].set(rotors[i].get_display_letter())
            self.rotor_ring_vars[i].set('A')
        
        self.reflector_var.set('B')
        self.plugboard_var.set('')
        
        # Reset text
        self.input_text = ""
        self.output_text = ""

        self.input_display.config(state='normal')  # Enable editing temporarily
        self.input_display.delete("1.0", tk.END)     # Clear all text
        self.input_display.config(state='disabled')  # Disable editing if needed
        
        self.output_display.config(state='normal')  # Enable editing temporarily
        self.output_display.delete("1.0", tk.END)     # Clear all text from the widget
        self.output_display.config(state='disabled')  # Re-disable editing if needed

        # Update displays
        self.draw_rotors()
        self.draw_reflector()
        self.draw_plugboard()

class EnigmaApp:
    def __init__(self):
        # Create the main window
        root = tk.Tk()
        root.title("Enigma Machine Simulator")
        
        # Set window icon if available

        icon_path = os.path.join("icons","Enigma-logo.png")
        try:
            img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, img)
        except:
            pass

        # Set initial size
        root.geometry("1200x800")
        
        # Apply vintage aesthetics
        self.apply_vintage_style()

        # Create simulator instance
        self.simulator = EnigmaSimulatorApp(root)
        root.update_idletasks()

        self.simulator.reset_machine()

        # Start main loop
        root.mainloop()
   
    def apply_vintage_style(self):
        # Apply a vintage, military-era look to the application
        style = ttk.Style()
        
        # Configure vintage colors and fonts for widgets
        style.configure("TButton", 
                     font=('Courier', 10, 'bold'),
                     background='#4A4A4A', 
                     foreground='white')
        
        style.configure("TCombobox",
                      font=('Courier', 10),
                      background='#4A4A4A')
        
        style.map("TButton",
               background=[('active', '#5D5D5D')],
               foreground=[('active', 'white')])

# Run the application
if __name__ == "__main__":
    EnigmaApp()
