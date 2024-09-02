# TinyBlue

This project is built on top of https://github.com/dhylands/python_lcd

## UI Structure for 16x2 LCD 

![scroll](/images/scroll.gif)

*Scroll down on the list of items*

![toggle](/images/toggle.gif)

*Jump into LED menu and select Toggle 2 times, then go Back*

Try the demo simulator [here](https://wokwi.com/projects/407891756643924993)

#### Problem
Interacting with extensive live data on a 16x2 character LCD can be challenging due to limited display space.


#### Solution

TinyBlue organizes items (text and buttons), supports multiple screens, and updates live data efficiently.

## Features

#### User Interface

The interface reserves one character on the left to show the cursor position. The cursor indicates the item currently in focus, which can be clickable or a Back button.

| Character | Description |
| - | - |
| ![focus](/images/focus.png) | This item cannot be selected |
| ![selectable](/images/selectable.png) | This item can be selected |
| ![back](/images/back.png) | This item is a back button |
| ![none](/images/none.png) | The cursor is not at this item yet |


#### Item

An `Item` represents a single line of text displayed on the LCD screen.

```python
from tinyblue import Item, Screen, TinyBlue

# create an item
item_temp = Item('Temp 40C')
```

To turn an item into a clickable button, set `on_click` to a callable function:

```python
def on_update():
    print('updating')

# an update button that calls on_update() when clicked
item_update = Item('Update', on_click = on_update)
```

To create a back button, set `is_back_button` to `True`:

```python
# a back button
item_back = Item('Back', is_back_button = True)
```

Update the text of an item using `set_text(text: string)`. The text updates automatically if the item is currently displayed:

```python
# update the text
item_temp.set_text('Temp 50C')
```

#### Screen

A `Screen` contains a list of `Item` objects that users can scroll through and interact with.

```python
...
item_sound = Item('Sound: On', on_click = on_click_sound)
item_light = Item('Light: On', on_click_light)

# create a Settings screen
settings_options = Screen([
    Item('Back', is_back_button = True),
    item_sound,
    item_light
])
```

#### TinyBlue
Once items and screens are ready. Initialize `TinyBlue(lcd, num_lines, num_columns)`
- `lcd` must be the [I2cLcd](https://github.com/dhylands/python_lcd/blob/master/lcd/i2c_lcd.py) object
-  `num_lines` is how many lines vertically on LCD screens
- `num_columns` is how many characters per line

For 1602A format, num_lines = 16, num_columns = 2.

```python
...
num_lines = 2
num_columns = 16

i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 400000)
lcd = I2cLcd(i2c, i2c.scan()[0], num_lines, num_columns)

# initialize TinyBlue
tb = TinyBlue(lcd, num_lines, num_columns)
```

Add the screen objects into TinyBlue with a unique `path`. `'/'` is the root path.

```python
screen_menu = Screen([
    Item('Hello 1'),
    Item('Hello 2'),
    Item('Hello 3')
])

# add menu as a root screen to TinyBlue
tb.add_screen(path = '/', screen_menu)
```

Call `render()` to display the current screen. This will call [I2cLcd](https://github.com/dhylands/python_lcd/blob/master/lcd/i2c_lcd.py) functions.

```python
# show what is the screen
tb.render()
```

#### Input

TinyBlue is designed to navigate through screens using just 2 buttons
- Scroll down by calling `tb.scroll()`
- Select the focused item by calling `tb.select()`

```python
...
# keyA is a Pin button
if keyA.value() == 0:
    tb.scroll()

# keyB is a Pin button
if keyB.value() == 0:
    tb.select()
```

You can add 2 more buttons
- Scroll up by calling `tb.scroll(direction = -1)`
- Go back to the previous screen by calling `tb.back()`. When you set item's `is_back_button = True`, it will call this `tb.back()`

#### Open Screen

Open a screen at a specific path using `tb.open_screen(path)`

```python
# ====================== add screen a
screen_a = Screen([
    Item('Back', is_back_button = True),
    Item('Hello A')
])
tb.add_screen(path = '/a', screen_a)

# ====================== add screen b
screen_b = Screen([
    Item('Back', is_back_button = True),
    Item('Hello B')
])
tb.add_screen(path = '/a', screen_a)

# ====================== add screen main
def on_click_a():
    tb.open_screen('/a')

def on_click_b():
    tb.open_screen('/b')

screen_main = Screen([
    Item('Open A', on_click = on_click_a),
    Item('Open B', on_click = on_click_b)
])
tb.add_screen(path = '/', screen_main)
```

#### Demo
Here is a counter example showing how to implement a counter with a button

```python
...
count = 0

item_count = Item('Count: 0')
def on_click_add():
    global count
    count += 1
    item_count.set_text(f"Count: {count}")

screen_main = Screen([
    item_count,
    Item('Add', on_click = on_click_add)
])
tb.add_screen(path = '/', screen_main)
```

## Get Started
#### Hardware Requirement
- Have one of the [Raspberry Pi Pico devices](https://www.raspberrypi.com/products/raspberry-pi-pico)
- Have one of the [HD44780 compatible character LCDs](https://a.co/d/fUgs5py) connected via [L2C](https://en.wikipedia.org/wiki/I%C2%B2C)
- Have at least 2 buttons connected to Pi Pico via [GPIO](https://en.wikipedia.org/wiki/General-purpose_input/output) ports

#### Install
1. Complete the Get Started guide with the [Pi Pico](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)
2. Open [Thonny](https://thonny.org/), and connect to the Pi Pico
3. Upload `lcd_api.py` and `machine_i2c_lcd.py` from this [repository](https://github.com/dhylands/python_lcd/tree/master/lcd)
4. Upload `tinyblue.py` and `example_tinyblue.py`
5. Open `example_tinyblue.py` on Thonny and check on the pins

```python
...
# setup display and pins
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 400000)
i2c_devices = i2c.scan()
lcd = I2cLcd(i2c, i2c_devices[0], 2, 16)

scroll = Pin(6, Pin.IN, Pin.PULL_UP)
select = Pin(13, Pin.IN, Pin.PULL_UP)
...
```

6. Run it
## License

The source code for the site is licensed under the MIT license, which you can find in the LICENSE file.

All graphical assets are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0).
