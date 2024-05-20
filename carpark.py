from bluepy import btle
import RPi.GPIO as GPIO
import time
import threading

# Configure GPIO settings
LED_PIN = 17  # Corresponds to GPIO pin 11
BUZZER_PIN = 18  # Corresponds to GPIO pin 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Global variable to store the latest interval
current_interval = 0

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        global current_interval
        distance_str = data.decode('utf-8').strip()
        print(f"Received distance: {distance_str} cm")
        
        try:
            distance = float(distance_str)
            interval = 0  # Default interval for distances over 100 cm

            if (0 < distance <= 20):
                interval = 0.2
            elif distance <= 30:
                interval = 0.3
            elif distance <= 50:
                interval = 0.5
            elif distance <= 100:
                interval = 1
            
            if interval != current_interval:
                current_interval = interval
                print(f"Current interval: {current_interval} seconds")
        except ValueError:
            print(f"Invalid distance value: {distance_str}")

def control_led_buzzer():
    global current_interval
    led_state = False
    buzzer_state = False
    
    while True:
        if current_interval > 0:
            led_state = not led_state
            buzzer_state = not buzzer_state
            GPIO.output(LED_PIN, led_state)
            GPIO.output(BUZZER_PIN, buzzer_state)
            time.sleep(current_interval)
        else:
            GPIO.output(LED_PIN, False)
            GPIO.output(BUZZER_PIN, False)
            time.sleep(1)  # Polling interval

# Connect to the Arduino Nano 33 IoT
peripheral = btle.Peripheral("EC:62:60:81:68:DE")  
peripheral.setDelegate(MyDelegate())

# Enable notifications
svc = peripheral.getServiceByUUID("180D")
char = svc.getCharacteristics("2A37")[0]
peripheral.writeCharacteristic(char.getHandle() + 1, b"\x01\x00")

# Start a separate thread to control the LED and buzzer
control_thread = threading.Thread(target=control_led_buzzer)
control_thread.daemon = True
control_thread.start()

try:
    print("Connected to the Arduino Nano 33 IoT")
    while True:
        if peripheral.waitForNotifications(1.0):
            continue
        print("Waiting for notifications...")
except KeyboardInterrupt:
    print("Exiting program")
finally:
    peripheral.disconnect()
    GPIO.cleanup()
    print("Disconnected and GPIO cleaned up")
