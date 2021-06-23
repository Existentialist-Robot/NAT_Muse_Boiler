void setup() {
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(analogRead(A5)); //Determine which Arduino pin is input and write it here. Must be an ANALOG pin
  delay(1); //Delay to prevent oversaturation of data
}
