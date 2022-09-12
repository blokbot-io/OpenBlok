#include <AccelStepper.h>

#define L1dirPin 5    // Layer 1 Direction Pin
#define L1stepPin 2   // Layer 1 Step Pin
#define L1posSensor 9 // Layer 1 Position Sensor

#define stepperEnable 8 // Stepper Driver Enable Pin
#define motorInterfaceType 1 // Motor Interface Type

AccelStepper stepperL1 = AccelStepper(motorInterfaceType, L1stepPin, L1dirPin);

void setup()
{
    Serial.begin(9600);
    Serial.println("Starting blokbot | Carousel");

    pinMode(L1posSensor, INPUT);
    pinMode(stepperEnable, OUTPUT);

    // Set the maximum speed and acceleration:
    stepperL1.setMaxSpeed(1000); // Max Steps per second
    stepperL1.setAcceleration(600);    // Acceleration Limit
}

void loop()
{
    digitalWrite(stepperEnable, LOW);
  
    bool L1sensorState = digitalRead(L1posSensor);
    Serial.print("L1 Sensor State: ");
    Serial.println(L1sensorState);

    Serial.println("L1 Finding Home");
    stepperL1.setSpeed(1000);

    while (true)
    {
        L1sensorState = digitalRead(L1posSensor);
        stepperL1.runSpeed();
    }

    stepperL1.stop();
    stepperL1.setCurrentPosition(0); // Set the current position to 0:
    Serial.println("L1 Pin Found");

    // Go right past the pin
    stepperL1.setSpeed(300); // Set the speed in steps per second
    while (!L1sensorState)
    {
        L1sensorState = digitalRead(L1posSensor);
        stepperL1.runSpeed();
    }

    stepperL1.stop();

    Serial.println("L1 Counting steps per revolution");
    stepperL1.setSpeed(1000); // Set the speed in steps per second
    while (L1sensorState)
    {
        L1sensorState = digitalRead(L1posSensor);
        stepperL1.runSpeed();
    }

    stepperL1.stop();

    long L1stepsPerRevolution = stepperL1.currentPosition(); // Stores the total steps needed for one revolution
    long L1stepsPerCup = L1stepsPerRevolution / 12;
    Serial.print("L1 Steps per revolution: ");
    Serial.println(L1stepsPerRevolution);

    stepperL1.setCurrentPosition(0); // Set the current position to 0:

    int L1cupNumber = 1;
    long L1targetPosition;

    while (true)
    {
        while (Serial.available() == 0)
        {
            // Wait for serial input
        }

        L1cupNumber = Serial.parseInt();
        L1targetPosition = map(L1cupNumber, 1, 12, 0, L1stepsPerRevolution - L1stepsPerCup);

        stepperL1.moveTo(L1targetPosition);
    }
}
