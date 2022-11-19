#include <AccelStepper.h>

#define dirPin 5 // Direction Pin
#define stepPin 2
#define motorInterfaceType 1
#define posSensor 9

#define stepperEnable 8 // Stepper Driver Enable Pin

AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

void setup()
{
    Serial.begin(9600);
    Serial.println("Starting blokbot - Carousel");

    pinMode(posSensor, INPUT);

  pinMode(stepperEnable, OUTPUT);

    // Set the maximum speed and acceleration:
    stepper.setMaxSpeed(20000); // Steps per second
    stepper.setAcceleration(6000);
}

void loop()
{

    bool sensorState = digitalRead(posSensor);
    Serial.print("SensorState: ");
    Serial.println(sensorState);

    Serial.println("Finding Home");
    stepper.setSpeed(1000);
    while (sensorState)
    {
        sensorState = digitalRead(posSensor);
        stepper.runSpeed();
    }
    stepper.stop();
    stepper.setCurrentPosition(0); // Set the current position to 0:
    Serial.println("Pin Found");

    // Go right past the pin
    stepper.setSpeed(300); // Set the speed in steps per second
    while (!sensorState)
    {
        sensorState = digitalRead(posSensor);
        stepper.runSpeed();
    }
    stepper.stop();

    Serial.println("Counting steps per revolution");
    stepper.setSpeed(1000); // Set the speed in steps per second
    while (sensorState)
    {
        sensorState = digitalRead(posSensor);
        stepper.runSpeed();
    }
    stepper.stop();

    long stepsPerRevolution = stepper.currentPosition(); // Stores the total steps needed for one revolution
    long stepsPerCup = stepsPerRevolution / 12;
    Serial.print("Steps per revolution: ");
    Serial.println(stepsPerRevolution);

    stepper.setCurrentPosition(0);

    int bin = 0;
    long targetPos;
    while (true)
    {

        while (Serial.available() == 0)
        {
        }

        bin = Serial.parseInt();
        // Serial.print("Going to bin #"); Serial.println(bin);
        targetPos = map(bin, 1, 12, 0, stepsPerRevolution - stepsPerCup);
        // Serial.print("Step Position: "); Serial.println(targetPos);

        stepper.runToNewPosition(targetPos);
    }
}
