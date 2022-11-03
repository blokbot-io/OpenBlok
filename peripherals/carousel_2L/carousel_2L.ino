#include <AccelStepper.h>

#define L1dirPin 5    // Layer 1 Direction Pin
#define L1stepPin 2   // Layer 1 Step Pin
#define L1posSensor 9 // Layer 1 Position Sensor

#define L2dirPin 6    // Layer 2 Direction Pin
#define L2stepPin 3   // Layer 2 Step Pin
#define L2posSensor 10 // Layer 2 Position Sensor

#define stepperEnable 8 // Stepper Driver Enable Pin
#define motorInterfaceType 1 // Motor Interface Type

AccelStepper stepperL1 = AccelStepper(motorInterfaceType, L1stepPin, L1dirPin);
AccelStepper stepperL2 = AccelStepper(motorInterfaceType, L2stepPin, L2dirPin);

void setup()
{
    Serial.begin(9600);
    Serial.println("Starting blokbot | Carousel");

    pinMode(L1posSensor, INPUT);
    pinMode(L2posSensor, INPUT);
    
    pinMode(stepperEnable, OUTPUT);

    // Set the maximum speed and acceleration:
    stepperL1.setMaxSpeed(20000); // Max Steps per second
    stepperL1.setAcceleration(6000);    // Acceleration Limit

    stepperL2.setMaxSpeed(20000); // Max Steps per second
    stepperL2.setAcceleration(6000);    // Acceleration Limit

}

void loop()
{
    digitalWrite(stepperEnable, LOW);
  
    bool L1sensorState = digitalRead(L1posSensor);
    bool L2sensorState = digitalRead(L2posSensor);
    
    Serial.print("L1 Sensor State: ");
    Serial.println(L1sensorState);

     Serial.print("L2 Sensor State: ");
    Serial.println(L2sensorState);

     Serial.print("L2 Sensor State: ");
    Serial.println(L2sensorState);

    Serial.println("L1 Finding Home");
    stepperL1.setSpeed(1000);
    stepperL2.setSpeed(1000);

   delay(100);

    L1sensorState = digitalRead(L1posSensor);
    while (L1sensorState || L2sensorState)
    {
        L1sensorState = digitalRead(L1posSensor);
        L2sensorState = digitalRead(L2posSensor);   

        if (!L1sensorState ){
          stepperL1.stop();
        }
        else{
          stepperL1.runSpeed();
        }

         if (!L2sensorState ){
          stepperL2.stop();
        }
        else{
          stepperL2.runSpeed();
        }

    }

    
    stepperL1.setCurrentPosition(0); // Set the current position to 0:
    stepperL2.setCurrentPosition(0); // Set the layer 2 current position to 0:
    
    Serial.println("L1 Pin Found");

    // Go right past the pin
    stepperL1.setSpeed(300); // Set the speed in steps per second
    stepperL2.setSpeed(300); // Set the speed in steps per second
    
    while (!L1sensorState || !L2sensorState)
    {
        L1sensorState = digitalRead(L1posSensor);
        L2sensorState = digitalRead(L2posSensor);    
        
        if (L1sensorState ){
          stepperL1.stop();
        }
        else{
          stepperL1.runSpeed();
        }

         if (L2sensorState ){
          stepperL2.stop();
        }
        else{
          stepperL2.runSpeed();
        }

    }    

    Serial.println("L1 Counting steps per revolution");
    stepperL1.setSpeed(1000); // Set the speed in steps per second
    stepperL2.setSpeed(1000); // Set the speed in steps per second
    
    while (L1sensorState || L2sensorState)
    {
        L1sensorState = digitalRead(L1posSensor);
        L2sensorState = digitalRead(L2posSensor);
        
       if (!L1sensorState ){
          stepperL1.stop();
        }
        else{
          stepperL1.runSpeed();
        }

         if (!L2sensorState ){
          stepperL2.stop();
        }
        else{
          stepperL2.runSpeed();
        }

    }

  
    long L1stepsPerRevolution = stepperL1.currentPosition(); // Stores the total steps needed for one revolution
    long L1stepsPerCup = L1stepsPerRevolution / 12;
    Serial.print("L1 Steps per revolution: ");
    Serial.println(L1stepsPerRevolution);

    long L2stepsPerRevolution = stepperL2.currentPosition(); // Stores the total steps needed for one revolution
    long L2stepsPerCup = L2stepsPerRevolution / 12;
    Serial.print("L2 Steps per revolution: ");
    Serial.println(L2stepsPerRevolution);
    

    stepperL1.setCurrentPosition(0); // Set the current position to 0:
    stepperL2.setCurrentPosition(0); // Set the current position to 0:
    

    int cupNumber = 1;

    int L1cupNumber = 1;
    long L1targetPosition;

    int L2cupNumber = 13;
    long L2targetPosition;

    while (true)
    {
        while (Serial.available() == 0)
        {
            // Wait for serial input
        }

      cupNumber = Serial.parseInt();
      Serial.println(cupNumber);


      if ((0 <= cupNumber) && (cupNumber <= 12)){   
        L1cupNumber = cupNumber;
        L2cupNumber = 13;            
      }

      if ((13 <= cupNumber) && (cupNumber <= 24)){   
        L1cupNumber = 1;
        L2cupNumber = cupNumber;            
      }

      
        L1targetPosition = map(L1cupNumber, 1, 12, 0, L1stepsPerRevolution - L1stepsPerCup);     
        stepperL1.runToNewPosition(L1targetPosition);

        L2targetPosition = map(L2cupNumber, 13, 24, 0, L2stepsPerRevolution - L2stepsPerCup);     
        stepperL2.runToNewPosition(L2targetPosition);

    }
}
