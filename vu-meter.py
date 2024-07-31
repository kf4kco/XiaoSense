import board
import audiobusio
import neopixel
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.color import AMBER, BLUE, MAGENTA, BLACK, GREEN, RED, PINK
import array
import math
import time
import digitalio

# Setup Neopixel strip
pixel_pin = board.D1
num_pixels = 20
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

# Setup Neopixel matrix (5x5)
matrix_pin = board.D3
matrix_width = 5
matrix_height = 5
matrix = neopixel.NeoPixel(matrix_pin, matrix_width * matrix_height, brightness=0.5, auto_write=False)

# Power up the PDM microphone
mic_power = digitalio.DigitalInOut(board.MIC_PWR)
mic_power.direction = digitalio.Direction.OUTPUT
mic_power.value = True
time.sleep(1)  # Wait for the mic to power up

# Initialize PDM Microphone
mic = audiobusio.PDMIn(board.PDM_CLK, board.PDM_DATA, sample_rate=16000, bit_depth=16)

# Helper function to get scaled sound level
def sound_level(samples):
    normalized_samples = [(sample - 32768) / 32768 for sample in samples]
    rms = math.sqrt(sum(sample * sample for sample in normalized_samples) / len(normalized_samples))
    scaled_rms = int(rms * 10000)  # Scaling factor set to 10,000
    return scaled_rms

# Define Animations
chase_amber = Chase(pixels, speed=0.1, color=AMBER, size=3)
chase_magenta = Chase(pixels, speed=0.1, color=MAGENTA, size=3)
rainbow = Rainbow(pixels, speed=0.1)
comet = Comet(pixels, speed=0.1, color=BLUE, tail_length=10, bounce=True)

# Sound Thresholds
low_threshold = 30      # Adjust these thresholds as needed

# Previous sound level for transition detection
previous_level = None
max_observed_level = 0
decay_factor = 0.99  # Decay factor for the ambient max level

samples = array.array('H', [0] * 160)

# Helper function to update the VU meter
def update_vu_meter(level, max_level):
    # Normalize the level to the matrix height
    num_lights = int((level / max_level) * matrix_height)
    
    for y in range(matrix_height):
        color = PINK if y >= matrix_height - num_lights else BLACK
        for x in range(matrix_width):
            matrix[y * matrix_width + x] = color
    
    matrix.show()

while True:
    mic.record(samples, len(samples))
    level = sound_level(samples)
    print("Scaled RMS Level:", level)

    # Update max observed level with decay
    max_observed_level = max(max_observed_level * decay_factor, level)

    # Update VU meter
    update_vu_meter(level, max_observed_level)

    # Determine if a threshold was crossed
    threshold_crossed = (previous_level is not None and
                         ((level < low_threshold <= previous_level) or
                          (level > max_observed_level >= previous_level) or
                          (level > low_threshold and previous_level <= low_threshold) or
                          (level < max_observed_level and previous_level >= max_observed_level)))

    if threshold_crossed:
        # Turn off all LEDs for the transition
        pixels.fill(BLACK)
        pixels.show()
        time.sleep(0.01)  # Duration of the transition

    # Select animation based on sound level
    if level < low_threshold:
        chase_amber.animate()
    elif level > max_observed_level:
        chase_magenta.animate()
    else:
        rainbow.animate()

    # Update previous sound level
    previous_level = level
