import time
import math
import board
import busio
import digitalio
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
from adafruit_led_animation.animation.sparkle import Sparkle
import neopixel

# Initialize GPIO pin to power the IMU
imu_power = digitalio.DigitalInOut(board.IMU_PWR)
imu_power.direction = digitalio.Direction.OUTPUT
imu_power.value = True  # Set to True to power the IMU

# Small delay to ensure IMU is powered up before initializing I2C
time.sleep(0.1)

# Create I2C bus
i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)

# Create LSM6DS3 instance
sensor = LSM6DS3(i2c)

# Number of samples for RMS calculation
NUM_SAMPLES = 10

# Threshold for tap detection
TAP_THRESHOLD = 2.0  # Adjust based on your requirements

# Initialize LED strip (adjust parameters based on your setup)
led_strip = neopixel.NeoPixel(board.D4, 30, auto_write=False)

# Animation modes
animation_modes = [
    Sparkle(led_strip, speed=0.1, color=(255, 0, 0)),
    Sparkle(led_strip, speed=0.1, color=(0, 255, 0)),
    Sparkle(led_strip, speed=0.1, color=(0, 0, 255)),
]

current_animation = 0

def calculate_rms(accel_values):
    # Calculate the root mean square (RMS) value
    rms = math.sqrt(sum(x ** 2 for x in accel_values) / len(accel_values))
    return rms

while True:
    # Collect acceleration values for RMS calculation
    accel_values = []
    for _ in range(NUM_SAMPLES):
        accel_x, accel_y, accel_z = sensor.acceleration
        accel_values.append(math.sqrt(accel_x**2 + accel_y**2 + accel_z**2))
        time.sleep(0.01)  # Adjust the delay based on your sampling rate

    # Calculate the RMS value
    rms_value = calculate_rms(accel_values)
    print("RMS Value:", rms_value)  # Debug: print RMS value

    # Check for a double tap
    if rms_value > TAP_THRESHOLD:
        print("First tap detected")  # Debug: print when first tap is detected
        time.sleep(0.2)  # Small delay to prevent detecting the same tap multiple times
        # Clear the previous values and collect new values for the second tap detection
        accel_values = []
        for _ in range(NUM_SAMPLES):
            accel_x, accel_y, accel_z = sensor.acceleration
            accel_values.append(math.sqrt(accel_x**2 + accel_y**2 + accel_z**2))
            time.sleep(0.01)

        # Calculate the RMS value again
        rms_value = calculate_rms(accel_values)
        print("RMS Value after delay:", rms_value)  # Debug: print RMS value after delay

        if rms_value > TAP_THRESHOLD:
            print("Second tap detected")  # Debug: print when second tap is detected
            current_animation = (current_animation + 1) % len(animation_modes)
            animation_modes[current_animation].animate()
            print("Animation changed.")

    # Delay for a short duration before reading again
    time.sleep(0.1)
