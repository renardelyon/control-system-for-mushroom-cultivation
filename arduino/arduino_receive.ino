#include <Wire.h>

#define SLAVE_ADDRESS 0x7

int data[2];

//digital pin number
int gate[] = {10, 12};

void receiveData(int bytecount){
  //Receiving data from master and passed it to
  //actuatorControl function
  int numOfBytes = Wire.available();
  byte b = Wire.read();
  for(int i=0; i<numOfBytes-1; i++){
    data[i] = Wire.read();
    Serial.println(data[i]);
    actuatorControl(data[i], gate[i]);
  }
}

void actuatorControl(int data, int GATE){
  //Open or close MOSFET gate based on the data 
  //that had been sent from Raspberry Pi
  Serial.println(data);
  if(data==0){
    Serial.println("LOW");
    digitalWrite(GATE, LOW);
    }
  else if(data==1){
     Serial.println("HIGH");
     digitalWrite(GATE, HIGH);
    }
  else{
    Serial.println("data is out of range");
  }
}

void end_program(){
  //end arduino process if char '!' passed to Serial window
  char ch;
  if(Serial.available()){
    ch = Serial.read();
    if(ch == '!'){
      digitalWrite(gate[0], LOW);
      digitalWrite(gate[1], LOW);
      Serial.println("Stopped") ;
    }
  }
}

void setup(){
  Serial.begin(9600);
  
  pinMode(gate[0], OUTPUT);
  pinMode(gate[1], OUTPUT);
  
  digitalWrite(gate[0], LOW);
  digitalWrite(gate[1], LOW);

  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
}

void loop(){
  delay(100);
  end_program();
}
