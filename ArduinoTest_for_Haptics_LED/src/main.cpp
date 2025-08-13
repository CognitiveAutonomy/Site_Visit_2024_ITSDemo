#include <Arduino.h>

const int PIN_POS_X = 10;
const int PIN_NEG_X = 9;
const int PIN_POS_Y = 6;
const int PIN_NEG_Y = 5;

// added for blinking
const int Pins[4] = {PIN_POS_X, PIN_NEG_X, PIN_POS_Y, PIN_NEG_Y};
bool ledState[4] = {false, false, false, false};
unsigned long lastToggle[4] = {0, 0, 0, 0};
uint8_t targetPWM[4] = {0, 0, 0, 0};
const float MAX_INPUT = 2.0f;

void blinkUpdate();
void blinkUpdate1();

void setup()
{
  Serial.begin(115200);
  // Serial.setTimeout(5);
  for (int i = 0; i < 4; i++)
  {
    pinMode(Pins[i], OUTPUT);
    analogWrite(Pins[i], 0); // fix bug: some will light up when the game begin
  }
  // Serial.println("Ready. Enter x,y (e.g. 1,1):");
}

void loop()
{
  if (Serial.available())
  {
    String line = Serial.readStringUntil('\n');
    line.trim();
    Serial.print("raw line = '"); Serial.print(line); Serial.println("'");
    Serial.print("length = "); Serial.println(line.length());
    int comma = line.indexOf(',');
    Serial.print("comma idx = "); Serial.println(comma);

    if (comma > 0)
    {
      float x = line.substring(0, comma).toFloat();
      float y = line.substring(comma + 1).toFloat();
      float fx = abs(x) / MAX_INPUT;
      float fy = abs(y) / MAX_INPUT;
      Serial.print("x="); Serial.print(x);
      Serial.print(", y="); Serial.println(y);
      if (fx > 1.0f)
        fx = 1.0f;
      if (fy > 1.0f)
        fy = 1.0f;

      // map to PWM
      uint8_t pwmX = uint8_t(fx * 255);
      uint8_t pwmY = uint8_t(fy * 255);

      targetPWM[0] = (x > 0) ? pwmX : 0;
      targetPWM[1] = (x < 0) ? pwmX : 0;
      targetPWM[2] = (y > 0) ? pwmY : 0;
      targetPWM[3] = (y < 0) ? pwmY : 0;
    }
  }
  blinkUpdate1();
  // analogWrite(PIN_POS_X, 64);

}
void blinkUpdate1() {
  unsigned long now = millis();
  const unsigned long MAX_PERIOD = 200; // 5Hz, if weak too strong, then turn it up
  const unsigned long MIN_PERIOD = 20; // 50Hz , if 10, then feels continuous
  const unsigned long MIN_ON  = 1;    

  for (int i = 0; i < 4; i++) {
    uint8_t t = targetPWM[i];
    if (!t) {
      analogWrite(Pins[i], 0);
      ledState[i] = false;
      lastToggle[i] = now;
      continue;
    }
    unsigned long period = map(t, 0, 255, MAX_PERIOD, MIN_PERIOD);
    if (period < MIN_PERIOD) period = MIN_PERIOD; // ensure period is not too short
    if (period > MAX_PERIOD) period = MAX_PERIOD; // ensure period is not too
    unsigned long onTime = map(t, 0, 255, MIN_ON, period - MIN_ON);
    unsigned long offTime = period - onTime;
    unsigned long elapsed = now - lastToggle[i];

    if (ledState[i]) {
      if (elapsed >= onTime) {
        ledState[i] = false;
        lastToggle[i] = now;
      }
    } else {
      if (elapsed >= offTime) {
        ledState[i] = true;
        lastToggle[i] = now;
      }
    }
    analogWrite(Pins[i], ledState[i] ? 255 : 0);
  }
}
void blinkUpdate()
{
  unsigned long now = millis();
  const unsigned long envelopeFreq = 10;
  const unsigned long period = 1000 / envelopeFreq;
  const unsigned long MIN_ON = 20;

  for (int i = 0; i < 4; i++)
  {
    uint8_t t = targetPWM[i];
    // if (t < 25)
    // {
    //   ledState[i] = false;
    //   analogWrite(Pins[i], 0);
    //   continue;
    // }
    if (t == 0) // no light
    {
      ledState[i] = false;
      analogWrite(Pins[i], 0);
      continue;
    }

    
  //   unsigned long interval = map(t, 0, 255, 400, 10);
    
  //   if (now - lastToggle[i] >= interval) // we need to wait at least "interval" time to toggle
  //   {
  //     lastToggle[i] = now;        // set the last timestamp to be now
  //     ledState[i] = !ledState[i]; // toggle on/off->off/on
  //   }
  
  //   analogWrite(Pins[i], ledState[i] ? t : 0);
  // }
    // 2nd version:
    
    unsigned long onTime = map(t, 0, 255, MIN_ON, period - MIN_ON); // map to on time
    if (onTime < MIN_ON) onTime = MIN_ON;
    unsigned long offTime = period - onTime;
    unsigned long elapsed = now - lastToggle[i];
    if (ledState[i]) {
      if (elapsed >= onTime) {
        ledState[i] = false;
        lastToggle[i] = now;
      }
    } else {
      if (elapsed >= offTime) {
        ledState[i] = true;
        lastToggle[i] = now;
      }
    }
    // unsigned long duration = ledState[i] ? onTime : offTime;

    // if (now - lastToggle[i] >= duration) // we need to wait at least "interval" time to toggle
    // {
    //   lastToggle[i] = now;        // set the last timestamp to be now
    //   ledState[i] = !ledState[i]; // toggle on/off->off/on
    // }
    if (ledState[i] && t > 0) Serial.print("PWM t = "), Serial.println(t);
    analogWrite(Pins[i], ledState[i] ? t : 0);
  }
}

