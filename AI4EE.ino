#include "BluetoothSerial.h"
#include <Wire.h>
#include "Adafruit_MCP9808.h"
#include "ClosedCube_HDC1080.h"

ClosedCube_HDC1080 hdc1080;
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

char send[10]; //For sending data over Bluetooth

void setup() {
  Serial.begin(115200);
  hdc1080.begin(0x40); //HDC1080 Address
  SerialBT.begin("Sensor198"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
  while (!Serial);
  Serial.println("MCP9808");

    // Make sure the sensor is found, you can also pass in a different i2c
  // address with tempsensor.begin(0x19) for example, also can be left in blank for default address use
  // Also there is a table with all addres possible for this sensor, you can connect multiple sensors
  // to the same i2c bus, just configure each sensor with a different address and define multiple objects for that
  //  A2 A1 A0 address
  //  0  0  0   0x18  this is the default address
  //  0  0  1   0x19
  //  0  1  0   0x1A
  //  0  1  1   0x1B
  //  1  0  0   0x1C
  //  1  0  1   0x1D
  //  1  1  0   0x1E
  //  1  1  1   0x1F
  if (!tempsensor.begin(0x18)) {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
    while (1); //Hangs up program if sensor cannot be found.
  }

   Serial.println("Found MCP9808!");

  tempsensor.setResolution(3); // sets the resolution mode of reading, the modes are defined in the table bellow:
  // Mode Resolution SampleTime
  //  0    0.5°C       30 ms
  //  1    0.25°C      65 ms
  //  2    0.125°C     130 ms
  //  3    0.0625°C    250 ms

}

void loop() {

  SerialBT.write('#');
  delay(500);
  Serial.println("wake up MCP9808.... "); // wake up MCP9808 - power consumption ~200 mikro Ampere
  tempsensor.wake();   // wake up, ready to read!

  // Read and print out the temperature, also shows the resolution mode used for reading.
  Serial.print("Resolution in mode: ");
  Serial.println (tempsensor.getResolution());
  float c = tempsensor.readTempC();
  float f = tempsensor.readTempF();
  Serial.print("Temp: ");
  Serial.print(c, 4); Serial.print("*C\t and ");
  Serial.print(f, 4); Serial.println("*F.");

  String csend = String(c,4); //Turns the temp readout float c to a string with 4 decimal places 

  csend.toCharArray(send,8); //Converts the csend array created in previous line to array temp which is 8 long

  for(int i = 0; i < 6; i++) {
    SerialBT.write(send[i]);
    Serial.println(send[i]);
    delay(200);
  }

  SerialBT.write(',');

  delay(2000);
  Serial.println("Shutdown MCP9808.... ");
  tempsensor.shutdown_wake(1); // shutdown MSP9808 - power consumption ~0.1 mikro Ampere, stops temperature sampling
  Serial.println("");
  delay(200);

  Serial.println("Wakeup HDC1080....");
  //Humidity
  float humidity = hdc1080.readHumidity();
  String hsend = String(humidity,2);
  hsend.toCharArray(send,8);

  for(int i = 0; i < 5; i++) {
    SerialBT.write(send[i]);
    Serial.println(send[i]);
    delay(200);
  }

  SerialBT.write(',');
  
  //temp
  float backupTemp = hdc1080.readTemperature();
  String backupSend = String(backupTemp,2);
  backupSend.toCharArray(send,8);

  for(int i = 0; i < 5; i++) {
    SerialBT.write(send[i]);
    Serial.println(send[i]);
    delay(200);
  }

  SerialBT.write(',');

  if (Serial.available()) {
    SerialBT.write(Serial.read());
  }
  if (SerialBT.available()) {
    Serial.write(SerialBT.read());
  }


  //Sends a '$' every ~10 seconds during the wait phase for a total of 17 seconds for keeping track of connection
  for (int i = 0; i < 17; i++) {

    SerialBT.write('$');
    delay(10000);

  }

}

/*HDC 1080 function
void printTandRH(HDC1080_MeasurementResolution humidity, HDC1080_MeasurementResolution temperature) {
  hdc1080.setResolution(humidity, temperature);

  HDC1080_Registers reg = hdc1080.readRegister();

  Serial.print("T=");
  Serial.print(hdc1080.readTemperature());
  Serial.print("C, RH=");
  Serial.print(hdc1080.readHumidity());
  Serial.println("%");
}
*/
