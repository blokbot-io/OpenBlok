#include <Wire.h>
#include <AccelStepper.h>

#define L1dirPin 5    // Layer 1 Direction Pin
#define L1stepPin 2   // Layer 1 Step Pin
#define L1posSensor 9 // Layer 1 Position Sensor

#define L2dirPin 6     // Layer 2 Direction Pin
#define L2stepPin 3    // Layer 2 Step Pin
#define L2posSensor 10 // Layer 2 Position Sensor

#define stepperEnable 8      // Stepper Driver Enable Pin
#define motorInterfaceType 1 // Motor Interface Type

AccelStepper stepperL1 = AccelStepper(motorInterfaceType, L1stepPin, L1dirPin);
AccelStepper stepperL2 = AccelStepper(motorInterfaceType, L2stepPin, L2dirPin);

long L1stepsPerRevolution = 0;
long L2stepsPerRevolution = 0;

long L1stepsPerCup = 0;
long L2stepsPerCup = 0;

int incomingWire = 0;

bool homed = false;

int cupNumber = 1;

int L1cupNumber = 37;
long L1targetPosition;

int L2cupNumber = 49;
long L2targetPosition;

void setup()
{
  Wire.begin(1);
  Wire.onReceive(receiveEvent); // register event

  // Serial.begin(9600);
  // Serial.println("Starting blokbot | Carousel");

  pinMode(L1posSensor, INPUT);
  pinMode(L2posSensor, INPUT);

  pinMode(stepperEnable, OUTPUT);
  digitalWrite(stepperEnable, LOW);

  // Set the maximum speed and acceleration:
  stepperL1.setMaxSpeed(20000);    // Max Steps per second
  stepperL1.setAcceleration(6000); // Acceleration Limit

  stepperL2.setMaxSpeed(20000);    // Max Steps per second
  stepperL2.setAcceleration(6000); // Acceleration Limit
}

void loop()
{

  if (!homed)
  {
    homeLayers();
  }

  if ((Serial.available() != 0) || (incomingWire != 0))
  {
    // Wait for serial input

    if (Serial.available() != 0)
    {
      cupNumber = Serial.parseInt();
    }

    if (incomingWire != 0)
    {
      cupNumber = incomingWire;
      incomingWire = 0;
    }

    // Serial.println(cupNumber);

    if ((37 <= cupNumber) && (cupNumber <= 48))
    {
      L1cupNumber = cupNumber;
      L2cupNumber = 49;
    }

    if ((49 <= cupNumber) && (cupNumber <= 60))
    {
      L1cupNumber = 37;
      L2cupNumber = cupNumber;
    }

    if (cupNumber < 37)
    {
      L1cupNumber = 37;
      L2cupNumber = 49;
    }

    L1targetPosition = map(L1cupNumber, 37, 48, 0, L1stepsPerRevolution - L1stepsPerCup);
    stepperL1.runToNewPosition(L1targetPosition);

    L2targetPosition = map(L2cupNumber, 49, 60, 0, L2stepsPerRevolution - L2stepsPerCup);
    stepperL2.runToNewPosition(L2targetPosition);
  }
}

void receiveEvent(int howMany)
{
  while (1 < Wire.available()) // loop through all but the last
  {
    char c = Wire.read(); // receive byte as a character
    // Serial.print(c);      // print the character
  }
  int x = Wire.read(); // receive byte as an integer
  incomingWire = x;
}

void homeLayers()
{
  bool L1sensorState = digitalRead(L1posSensor);
  bool L2sensorState = digitalRead(L2posSensor);

  // Serial.print("L1 Sensor State: ");
  // Serial.println(L1sensorState);

  // Serial.print("L2 Sensor State: ");
  // Serial.println(L2sensorState);

  // Serial.println("Finding Home");
  stepperL1.setSpeed(1000);
  stepperL2.setSpeed(1000);

  delay(100);

  L1sensorState = digitalRead(L1posSensor);
  L2sensorState = digitalRead(L2posSensor);
  while (L1sensorState || L2sensorState)
  {
    L1sensorState = digitalRead(L1posSensor);
    L2sensorState = digitalRead(L2posSensor);

    if (!L1sensorState)
    {
      stepperL1.stop();
    }
    else
    {
      stepperL1.runSpeed();
    }

    if (!L2sensorState)
    {
      stepperL2.stop();
    }
    else
    {
      stepperL2.runSpeed();
    }

    if (!L1sensorState && !L2sensorState)
    {
      delay(10);
      L1sensorState = digitalRead(L1posSensor);
      L2sensorState = digitalRead(L2posSensor);
    }
  }

  // Serial.print("L1 Sensor State: ");
  // Serial.println(digitalRead(L1posSensor));

  // Serial.print("L2 Sensor State: ");
  // Serial.println(digitalRead(L2posSensor));

  stepperL1.setCurrentPosition(0); // Set the current position to 0:
  stepperL2.setCurrentPosition(0); // Set the layer 2 current position to 0:

  // Serial.println("L1 Pin Found");

  // Go right past the pin
  stepperL1.setSpeed(300); // Set the speed in steps per second
  stepperL2.setSpeed(300); // Set the speed in steps per second

  while (!L1sensorState || !L2sensorState)
  {
    L1sensorState = digitalRead(L1posSensor);
    L2sensorState = digitalRead(L2posSensor);

    if (L1sensorState)
    {
      stepperL1.stop();
    }
    else
    {
      stepperL1.runSpeed();
    }

    if (L2sensorState)
    {
      stepperL2.stop();
    }
    else
    {
      stepperL2.runSpeed();
    }

    if (L1sensorState && L2sensorState)
    {
      delay(10);
      L1sensorState = digitalRead(L1posSensor);
      L2sensorState = digitalRead(L2posSensor);
    }
  }

  // Serial.println("L1 Counting steps per revolution");
  stepperL1.setSpeed(1000); // Set the speed in steps per second
  stepperL2.setSpeed(1000); // Set the speed in steps per second

  while (L1sensorState || L2sensorState)
  {
    L1sensorState = digitalRead(L1posSensor);
    L2sensorState = digitalRead(L2posSensor);

    if (!L1sensorState)
    {
      stepperL1.stop();
    }
    else
    {
      stepperL1.runSpeed();
    }

    if (!L2sensorState)
    {
      stepperL2.stop();
    }
    else
    {
      stepperL2.runSpeed();
    }

    if (!L1sensorState && !L2sensorState)
    {
      delay(10);
      L1sensorState = digitalRead(L1posSensor);
      L2sensorState = digitalRead(L2posSensor);
    }
  }

  L1stepsPerRevolution = stepperL1.currentPosition(); // Stores the total steps needed for one revolution
  L1stepsPerCup = L1stepsPerRevolution / 12;
  // Serial.print("L1 Steps per revolution: ");
  // Serial.println(L1stepsPerRevolution);

  L2stepsPerRevolution = stepperL2.currentPosition(); // Stores the total steps needed for one revolution
  L2stepsPerCup = L2stepsPerRevolution / 12;
  // Serial.print("L2 Steps per revolution: ");
  // Serial.println(L2stepsPerRevolution);

  stepperL1.setCurrentPosition(0); // Set the current position to 0:
  stepperL2.setCurrentPosition(0); // Set the current position to 0:

  homed = true;
}
