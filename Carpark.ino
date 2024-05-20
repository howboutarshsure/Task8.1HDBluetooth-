#include <HCSR04.h>
#include <ArduinoBLE.h>

// Pin configuration
const byte trigPin = 3;
const byte echoPin = 2;

// BLE service and characteristic UUIDs
const char* SERVICE_UUID = "180D";
const char* CHARACTERISTIC_UUID = "2A37";

// Initialize BLE service and characteristic
BLEService distanceService(SERVICE_UUID);
BLEStringCharacteristic distanceCharacteristic(CHARACTERISTIC_UUID, BLERead | BLENotify, 20);

// Initialize the ultrasonic sensor
UltraSonicDistanceSensor ultrasonicSensor(trigPin, echoPin);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  // Set the local name and advertise the service
  BLE.setLocalName("Nano33IoT");
  BLE.setAdvertisedService(distanceService);

  // Add the characteristic to the service
  distanceService.addCharacteristic(distanceCharacteristic);
  BLE.addService(distanceService);

  // Start advertising
  BLE.advertise();
  Serial.println("BLE device is now active, waiting for connections...");
}

void loop() {
  // Wait for a BLE central to connect
  BLEDevice centralDevice = BLE.central();

  // If a central is connected
  if (centralDevice) {
    Serial.print("Connected to central: ");
    Serial.println(centralDevice.address());

    while (centralDevice.connected()) {
      // Measure distance
      double distance = ultrasonicSensor.measureDistanceCm();
      String distanceString = String(distance);
      Serial.print("Sending distance: ");
      Serial.println(distanceString);

      // Update characteristic with the new distance
      distanceCharacteristic.writeValue(distanceString);
      delay(1000); // Delay between notifications
    }

    Serial.print("Disconnected from central: ");
    Serial.println(centralDevice.address());
  }
}
