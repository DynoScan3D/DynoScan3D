//Arduino Controls for Turntable
// Define Constants
// Connections to A4988
const int dirPin = 7;  // Direction
const int stepPin = 3; // Step
const int MS1 = 4;
const int MS2 = 5;
const int MS3 = 6;
 
// Motor steps per rotation
const int STEPS_PER_REV = 3200;
volatile int angles = 0;                    //number of angles 

//delay per steps
int delaySteps = 0;
int stepsPerAngle = 0;      //number of steps per angle

//Receive input for angles from serial (https://forum.arduino.cc/index.php?topic=396450.0)
const byte numChars = 64;
char receivedChars[numChars];  //Array to store received data
boolean newData = false;
int dataNumber = 0;

//interrupt pin for killswitch
const byte interruptPin = 2;      

//pin for Operation state LED - Turntable in rotation: HIGH; Turntable not in rotation: LOW
const int LEDpin = 9;

//initial state as off 
volatile byte state = 0;

void setup() {
  
  // Setup the pins as Outputs
  // Pins on A4988
  pinMode(stepPin,OUTPUT);      
  pinMode(dirPin,OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(MS3, OUTPUT);
  
  // Sixteenth stepping
  digitalWrite(MS1,HIGH); 
  digitalWrite(MS2,HIGH); 
  digitalWrite(MS3,HIGH); 
  
  // Set motor direction clockwise
  digitalWrite(dirPin,HIGH); 

  // Interrupt set up
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), killswitch, CHANGE);         //Interrupt for killswitch
  
  Serial.begin(115200);

  //LED Pin
  pinMode(LEDpin, OUTPUT);
  digitalWrite(LEDpin, LOW);
}

void loop() {
  //Receive angles first
  if (angles == 0){
    while (!Serial.available()){        //Wait for data to arrive
      delay(500);
    }
    recvWithEndMarker();
    showNewNumber();
    angles = dataNumber;
  }

  serial_clear();
  
  while (!Serial.available()){        //Wait for data to arrive
    delay(500);
  }
  recvWithEndMarker();
  showNewNumber();
  state = dataNumber;
  
  stepsPerAngle = STEPS_PER_REV/angles;        //Number of steps per angle

  if (state == 1){
    digitalWrite(LEDpin, HIGH);         //LED to show turntable is rotating

    //If angles = 4, rotate 90 deg
    for(int x = 0; x < stepsPerAngle ; x++) {     
      if ((delaySteps > 20000) || (stepsPerAngle < (stepsPerAngle*0.25))){   //Ramping up input
        delaySteps -= 100;
      }
      else if ((delaySteps < 30000) || (stepsPerAngle > (stepsPerAngle*0.75))){ //Ramping down input
        delaySteps += 100;
      }
      else {
        delaySteps = 20000;
      }
      digitalWrite(stepPin,HIGH); 
      delayMicroseconds(delaySteps); 
      digitalWrite(stepPin,LOW); 
      delayMicroseconds(delaySteps);          
    }
      
    Serial.println("s");            //Python script starts scanning
    serial_clear();
    
    //Rotation complete. Communicate completion to software
    state = 0;
    digitalWrite(LEDpin, LOW);
    delay(500);
  }
}

void killswitch(){
  Serial.println("Killswitch activated");
  digitalWrite(LEDpin, LOW);
  state = 0;
  while (1){
    digitalWrite(stepPin,LOW);          //stop Motor. Full reboot of Arduino required.
  }
}

void serial_clear(){                   //funcion to clear serial data stored
  while (Serial.available()){
    Serial.read();
  }
}

//Check for end marker from serial com
void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;
 
  if (Serial.available() > 0) {
    rc = Serial.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
          ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

//Convert serial input to integer
void showNewNumber() {
    if (newData == true) {
        dataNumber = 0;             // new for this version
        dataNumber = atoi(receivedChars);   // new for this version
        newData = false;
    }
}
