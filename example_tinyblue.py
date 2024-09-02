"""
TinyBlue for Raspberry Pi Pico is licensed under the MLT License.
Created by Saranomy 2024.
"""

from machine import Pin, I2C
from machine_i2c_lcd import I2cLcd
from tinyblue import TinyBlue, Screen, Item
import time, gc

# led
led_pin = Pin("LED", Pin.OUT)
led_pin_value = 0
led_pin.off()

# temperature
def get_temp():
    adc = machine.ADC(4)
    raw_value = adc.read_u16()
    voltage = raw_value * 3.3 / 65535
    celsius = 27 - (voltage - 0.706) / 0.001721
    return "Temp {:.2f}C".format(celsius)

# ram usage
def get_ram():
    return "Free {0:d}KB".format(gc.mem_free() // 1024)

# setup display and pins
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 400000)
i2c_devices = i2c.scan()
lcd = I2cLcd(i2c, i2c_devices[0], 2, 16)

scroll = Pin(6, Pin.IN, Pin.PULL_UP)
select = Pin(13, Pin.IN, Pin.PULL_UP)

if __name__=='__main__':
    
    # initialize TinyBlue
    num_lines = 2
    num_columns = 16
    tm = TinyBlue(lcd, num_lines, num_columns)

    # led screen
    item_led_back = Item('Back / LED: ON', is_back_button = True)
    def on_click_toggle_led():
        global led_pin_value
        led_pin_value = (led_pin_value + 1) % 2
        led_pin.toggle()
        if led_pin_value:
            item_led_back.set_text('Back / LED ON')
        else:
            item_led_back.set_text('Back / LED OFF')

    led_screen = Screen([
        item_led_back,
        Item('Toggle', on_click = on_click_toggle_led)
    ])
    tm.add_screen('/led', led_screen)
    
    # about screen
    about_screen = Screen([
        Item('Back', is_back_button = True),
        Item('GitHub/Saranomy'),
        Item('Tiny1602Menu')
    ])
    tm.add_screen('/about', about_screen)
    
    # main screen
    def on_click_led():
        tm.open_screen('/led')
        
    def on_click_about():
        tm.open_screen('/about')
        
    item_led = Item('LED', on_click = on_click_led)
    item_temp = Item(get_temp())
    item_ram = Item(get_ram())
    main_screen = Screen([
        item_led,
        item_temp,
        item_ram,
        Item('About', on_click = on_click_about)
    ])
    tm.add_screen('/', main_screen)

    # interrupt buttons
    prevent_spam = -1
    def interrupt_scroll(pin):
        global prevent_spam
        if pin.value() == 0 and (prevent_spam == -1 or time.ticks_ms() - prevent_spam > 100):
            tm.scroll()
        prevent_spam = time.ticks_ms()
    scroll.irq(trigger=Pin.IRQ_FALLING, handler=interrupt_scroll)

    def interrupt_select(pin):
        global prevent_spam
        if pin.value() == 0 and (prevent_spam == -1 or time.ticks_ms() - prevent_spam > 100):
            tm.select()
        prevent_spam = time.ticks_ms()
    select.irq(trigger=Pin.IRQ_FALLING, handler=interrupt_select)

    # update loop
    while True:
        tm.render()
        item_temp.set_text(get_temp())
        item_ram.set_text(get_ram())
        time.sleep(1)