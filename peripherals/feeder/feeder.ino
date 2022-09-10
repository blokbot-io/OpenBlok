/* Controls the hopper and vibratory feeder. */

// Hopper
#define pwm 9
#define pot A0

// Vibratory Feeder
#define IRSENSORPIN 2
#define RELAYPIN 3
#define ledpin 13 // led on arduino pin 13 to visualize beam breaking

int sensorState = 0, lastState = 0; // variable for reading the breakbeam status

void setup()
{
    pinMode(pwm, OUTPUT);
    pinMode(pot, INPUT);

    analogWrite(pwm, 0); // safety speed reset of the motor

    // initialize the relay pins as an output:
    pinMode(RELAYPIN, OUTPUT);

    pinMode(ledpin, OUTPUT);
    pinMode(IRSENSORPIN, INPUT);     // initialize the sensor pin as an input:
    digitalWrite(IRSENSORPIN, HIGH); // turn on the pullup
}

void loop()
{
    // Hopper
    float val = analogRead(pot);
    float duty = map(val, 0, 1023, 0, 255);
    analogWrite(pwm, duty);

    // Vibratory Feeder
    sensorState = digitalRead(IRSENSORPIN); // read the state of the IR sensor value

    // check if the sensor beam is broken
    // if it is, the sensorState is LOW:
    if (sensorState == LOW)
    {
        // turn both relays  on, opening the circuits:
        digitalWrite(RELAYPIN, HIGH);
        digitalWrite(ledpin, HIGH);
        analogWrite(pwm, 0);
        delay(1000);
        ;
    }
    else
    {
        digitalWrite(RELAYPIN, LOW); // keep relays off
    }
}
