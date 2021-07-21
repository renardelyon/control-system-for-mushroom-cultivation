#include <Wire.h>

#define GATE 10
#define SLAVE_ADDRESS 0x7

int data;
int block_data[4];

void receiveData(int byteCount){
  while(Wire.available()){
    data = Wire.read();
  }
    if(data>0){
      Serial.println(data);
      if(data<60){
        Serial.println("LOW");
        digitalWrite(GATE, LOW);
      }
      else{
        Serial.println("HIGH");
        digitalWrite(GATE, HIGH);
      }
  }
}

void receiveBlockData(int byteCount){
  int numOfBytes = Wire.available();
  Serial.print("len:");
  Serial.print(numOfBytes);
  Serial.println(" ");
  
  byte b = Wire.read();
  Serial.print("var:");
  Serial.print(b);
  Serial.println(" ");

  for(int i=0; i<numOfBytes-1; i++){
    block_data[i] = Wire.read();
    Serial.println(block_data[i]);
  }
}
 
void setup() {
  Serial.begin(9600);
  
  pinMode(GATE, OUTPUT);
  digitalWrite(GATE, LOW);
  
  Wire.begin(SLAVE_ADDRESS);
  //Wire.onReceive(receiveData);
  Wire.onReceive(receiveBlockData);
}

void loop() {  
  delay(100);
}
