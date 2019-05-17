#include <stdio.h>
#include <wiringPi.h>

#define SIGNAL_PIN      0 // physical pin #11 (+3.3v)
#define ON              1 
#define OFF             0
#define PULSE_WIDTH     200 // send voltage for PULSE_WIDTH ms

int main(void)
{
    if (wiringPiSetup() == -1) {
        puts("setup failed");
        return 1;
    }
    
    pinMode(SIGNAL_PIN, OUTPUT);
    digitalWrite(SIGNAL_PIN, SIGNAL_ON);
    delay(PULSE_WIDTH);
    digitalWrite(SIGNAL_PIN, SIGNAL_OFF);
    return 0;
}