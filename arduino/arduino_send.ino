#include <Wire.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 10
#define DHTTYPE DHT22
#define SLAVE_ADDRESS 0x8
#define FLOATS_SENT 2

DHT dht(DHTPIN, DHTTYPE);

float humidity = 0.0;
float temp = 0.0;
float tempHumData[FLOATS_SENT];

bool done = false;

void setup() {
  Serial.begin(9600);

  tempHumData[0] = humidity;
  tempHumData [1] = temp;

  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendTempHumData);
   
  dht.begin();
}

void loop() {
  //Read humidity 
  float humidity = dht.readHumidity();
  //Read temperature in Celcius
  float temp = dht.readTemperature();

  if (isnan(humidity) || isnan(temp)){
    Serial.println("Failed to read temperature or humidity");
    return;
  }
  tempHumData[0] = humidity;
  tempHumData[1] = temp;
  
  end_program();
}

void end_program(){
  char ch;
  if(Serial.available()){
    ch = Serial.read();
    if(ch == '!'){
      done = true;
      Serial.println("Finished recording data") ;
    }
  }
}

void sendTempHumData(){
  //send float datatype to master
  Wire.write((byte*) &tempHumData, FLOATS_SENT*sizeof(float));;
}
