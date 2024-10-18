For hardware, instead soldering, two boards were connected separately.
LEDs connected with GPIO 14 and 15.
After wifi connection, timer that has read data from thingspeak initated.
Then, in while loop, device id was checked whther it is correct.
Then data format, ODR and measure mode were set.
After getting offset and calibration, if value read from thingspeak is 'activated',
motion detection is now available and green led is lit.
If sensor detect accelartion larger than threshold, it turns red led.
If value read from thingspeak is 'deactivated', 
all leds are turned off and no measurement performed.

https://youtu.be/JPaIdZJ_6tY
