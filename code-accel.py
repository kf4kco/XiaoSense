import time
import board
import neopixel
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
import busio
from digitalio import DigitalInOut, Direction

# Initialize the GPIO pin to power the IMU
imu_power = DigitalInOut(board.IMU_PWR)  # Change to an appropriate available pin
imu_power.direction = Direction.OUTPUT
imu_power.value = True

# Short delay to ensure the IMU has power before I2C initialization
time.sleep(0.1)

# Initialize I2C connection
i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)

# Initialize the LSM6DS3 sensor
sensor = LSM6DS3(i2c)

# Define the number of LEDs and the pin they're connected to
NUM_LEDS = 10
LED_PIN = board.D4

# Initialize the NeoPixel strip
strip = neopixel.NeoPixel(LED_PIN, NUM_LEDS, auto_write=False)

# Function to map sensor data to color values (0-255)
def map_value(value, from_min, from_max, to_min, to_max):
    from_span = from_max - from_min
    to_span = to_max - to_min
    value_scaled = float(value - from_min) / float(from_span)
    return int(to_min + (value_scaled * to_span))

while True:
    # Read accelerometer data
    accel_x, accel_y, accel_z = sensor.acceleration

    # Print X, Y, Z values to the serial monitor
    print(f"X: {accel_x:.2f}, Y: {accel_y:.2f}, Z: {accel_z:.2f}")

    # Map accelerometer data to color values (0-255)
    red = map_value(accel_x, -9.8, 9.8, 0, 255)
    green = map_value(accel_y, -9.8, 9.8, 0, 255)
    blue = map_value(accel_z, -9.8, 9.8, 0, 255)

    # Set all LEDs to the calculated color
    color = (red, green, blue)
    for i in range(NUM_LEDS):
        strip[i] = color
    strip.show()

    # Delay for 250ms
    time.sleep(0.25)
