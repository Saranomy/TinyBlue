"""
TinyBlue for Raspberry Pi Pico is licensed under the MLT License.
Created by Saranomy 2024.
"""

from machine import I2C
from machine_i2c_lcd import I2cLcd

class Item:
    """
    An Item represents a single line of text displayed on the LCD screen.
    """
    def __init__(self, text: string, on_click: Callable[..., Any] = None, is_back_button: bool = False):
        """
        Create an item displayed on a screen. Can be clickable
        
        Args:
            text (string): Text to be shown on the display
            on_click (function): Call this function when item is selected
            is_back_button (bool): True if it is a back button
        """
        self.text = text
        self.on_click = on_click
        self.update = False
        self.is_back_button = is_back_button
        
    def set_text(self, text: string):
        """
        Update the text and trigger the update
        
        Args:
            text (string): Text to be shown on the display
        """
        self.text = text
        self.update = False
        
    def get_visible_text(self, num_chars: int, animate: bool = True) -> string:
        """
        (Do not need to call this)
        """
        text = self.text[0:num_chars]
        return text + ' ' * (num_chars - len(text))
    
class Screen:
    """
    A screen contains a list of Item objects that users can scroll and interact with
    """
    def __init__(self, items: array):
        """
        Create a screen with items
        
        Args:
            items (array): Array of Item objects
        """
        if not isinstance(items, list):
            raise TypeError("Items must be a list.")
        if not all(isinstance(item, Item) for item in items):
            raise TypeError("All items must be instances of Item.")
        self.items = items
        self.top_line = 0
        self.line_index = 0
    
    def scroll(self, direction: int, num_lines: int):
        """
        (Do not need to call this)
        """
        self.line_index = (self.line_index + len(self.items) + direction) % len(self.items)
        if self.line_index >= self.top_line + num_lines: # scroll down
            self.top_line = self.line_index - num_lines + 1
        elif self.line_index < self.top_line:
            self.top_line = self.line_index
        
    def render(self, num_lines: int, num_columns: int) -> array:
        """
        (Do not need to call this)
        """
        a = []
        for i in range(num_lines):
            if self.top_line + i < len(self.items):
                item = self.items[self.top_line + i]
                if self.top_line + i == self.line_index:
                    if callable(item.on_click):
                        cursor = '='
                    elif item.is_back_button:
                        cursor = '<'
                    else:
                        cursor = '>'
                else:
                    cursor = ' '
                item_text = cursor + item.get_visible_text(num_columns - 1)
            else:
                item_text = ' ' * num_columns
            a.append(item_text)
        return a
    
    def get_selected_item(self) -> Item:
        """
        (Do not need to call this)
        """
        return self.items[self.line_index]

    def reset(self):
        """
        (Do not need to call this)
        """
        self.top_line = 0
        self.line_index = 0
    
class TinyBlue:
    """
    A class to store Screen objects with their paths
    """
    def __init__(self, lcd: I2cLcd, num_lines: int = 2, num_columns: int = 16):
        """
        Create the TinyBlue object
        
        Args:
            lcd: (I2cLcd): I2cLcd object
            num_lines (int): how many lines vertically on LCD screens
            num_columns (int): how many characters per line
        """
        self.lcd = lcd
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.lcd.clear()
        # https://maxpromer.github.io/LCD-Character-Creator/
        self.lcd.custom_char(0, bytearray([0x00, 0x08, 0x04, 0x02, 0x04, 0x08, 0x00, 0x00])); # cursor for non-clickable items
        self.lcd.custom_char(1, bytearray([0x00, 0x08, 0x04, 0x1E, 0x04, 0x08, 0x00, 0x00])); # cursor for clickable items
        self.lcd.custom_char(2, bytearray([0x00, 0x04, 0x08, 0x1E, 0x08, 0x04, 0x00, 0x00])); # cursor for back button
        self.screens = {}
        self.screen_stack = []
        self.screen_root_path = '/'
        self.auto_render = True
        
    def add_screen(self, path: string, screen: Screen):
        """
        Store a Screen object
        
        Args:
            path (string): the unique path
            screen (Screen): the Screen object
        """
        self.screens[path] = screen
        if path == self.screen_root_path:
            self.screen_stack = [screen]
            
    def top_screen(self) -> Screen:
        """
        (Do not need to call this)
        """
        if len(self.screen_stack) == 0:
            raise TypeError("No screen to show. Call add_screen first")
        return self.screen_stack[len(self.screen_stack) - 1]
    
    def open_screen(self, path: string):
        """
        Open the screen associated with the path. Call this in item's on_click
        
        Args:
            path (string): the unique path
        """
        if path in self.screens:
            self.screen_stack.append(self.screens[path])
            if self.auto_render:
                self.render()
    
    def render(self):
        """
        Display the current screen to LCD
        
        """
        lines = self.top_screen().render(self.num_lines, self.num_columns)
        for y in range(len(lines)):
            line = lines[y]
            self.lcd.move_to(0, y)
            if line[0] == '>':
                self.lcd.putchar(chr(0))
            elif line[0] == '=':
                self.lcd.putchar(chr(1))
            elif line[0] == '<':
                self.lcd.putchar(chr(2))
            else:
                self.lcd.putchar(' ')
            self.lcd.putstr(lines[y][1:])
        
    def scroll(self, direction: int = 1):
        """
        Scroll through the items of the current screen
        
        Args:
            direction (int): 1 to go down, -1 to go up
        """
        self.top_screen().scroll(direction, self.num_lines)
        if self.auto_render:
            self.render()
            
    def back(self):
        """
        Go back to previous screen if possible
        """
        if len(self.screen_stack) > 1:
            self.top_screen().reset()
            self.screen_stack.pop()
            if self.auto_render:
                self.render()
        
    def select(self):
        """
        Select the focused item (where the cursor is)
        """
        item = self.top_screen().get_selected_item()
        if item.is_back_button:
            self.back()
        elif callable(item.on_click):
            item.on_click()
            if self.auto_render:
                self.render()