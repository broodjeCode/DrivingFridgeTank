## Import used python libraries
import sys
import os
import RPi.GPIO as GPIO
import time
import math
from array import *
from multiprocessing import Process

## Main class Ultrasoneto
class Ultrasone(Process):
	def __init__(self, args):
		self.distance=([0,0,0]) ## Empty array for L, F, R sensors
		self.loopCompletedTime=1
                self.debug=args["sdebug"]

        ## Ultrasone init from source: https://www.modmypi.com/blog/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi

		GPIO.setmode(GPIO.BOARD)
		#if left !exist


		## Ultrasone pins
		# Ultrasone LEFT
		self.TRIG1 = 7
		self.ECHO1 = 12

		# Ultrasone RIGHT
		self.TRIG2 = 15
		self.ECHO2 = 16

		# Ultrasone FRONT
                self.TRIG3 = 0
                self.ECHO3 = 0


		## Setup the GPIO pins
		# LEFT
		GPIO.setup(self.TRIG1, GPIO.OUT)
		GPIO.setup(self.ECHO1, GPIO.IN)
		GPIO.output(self.TRIG1, 0)

		# RIGHT
		GPIO.setup(self.TRIG2, GPIO.OUT)
		GPIO.setup(self.ECHO2, GPIO.IN)
		GPIO.output(self.TRIG2, 0)

		# FRONT (commented for now as we don't have a third sensor yet)
                #GPIO.setup(self.TRIG3, GPIO.OUT)
                #GPIO.setup(self.ECHO3, GPIO.IN)
                #GPIO.output(self.TRIG3, 0)


## The loop function that is started from the parent
	def run(self, UltrasoneDataOut): # This function is called from Robot.py to start the Ultrasone thread.
		while True:
			self.loopStartTime=time.time() ## save loop time for speed
			self.distance[0]=self.PrivGetDist(self.ECHO1, self.TRIG1, self.distance[0]) # get sensor 1 distance
			self.distance[1]=self.PrivGetDist(self.ECHO2, self.TRIG2, self.distance[1]) # get sensor 2 distance
			#self.distance[2]=self.PrivGetDist(self.ECHO3, self.TRIG3, self.distance[2]) # get sensor 3 distance
			if self.debug:
				print "Distance: %s cm" % str(self.distance)

			UltrasoneDataOut[0]=self.distance[0]	#float(self.distance)
			UltrasoneDataOut[1]=25.44			# Hardcoded for now, I only have two sensors now. This will use self.distance[2] in the future
			UltrasoneDataOut[2]=self.distance[1]  	# Right sensor
			self.loopCompletedTime=(time.time() - self.loopStartTime) ## calculate loop speed for debugging and calculating how many samples per second we took.
			UltrasoneDataOut[3]=self.loopCompletedTime	# Store the looptime





## (private) function to fetch the ultrasone pulse and calculate the distance. If the distance is invalid, it will use the previous recorded value. This function is called with ECHO and TRIG as variables to choose the sensor (multisensor capable, ofcourse).
	def PrivGetDist(self, ECHO, TRIG, previousValue):
		
		i=0
		results = [] # Array for storing results.

		# Take three measurements to improve accuracy.
		while i<3:
			time.sleep(0.001) # limit the speed of this loop to make sure it won't use a core completely.
                        i=i+1
			var = self.getRawData(ECHO, TRIG) # Read raw sensor values and store these in var.
			if (var >=0 ): # && niet buitengewoon groot of klein na vorige meting?
				results.append(var) # append results to results array

		fResults=[float(i) for i in results] # convert values to a nice float
		avgRaw = sum(fResults) / float(len(fResults)) # Calculate average
		avgCM = avgRaw * 17000 # (avgRaw * 17000) = distance to environment in cm.

		if (self.debug): # If sensor debugging is enabled (args["sdebug") print results to console
			for i in results:
				print(i),
				print(str(results)),

		if avgCM >= 0: # If avgCM is a negative value than return the previous value, if the sensor returns a negative value it means there was an error, don't use it.
			return avgCM # Return calculated value
		else:
			return previousValue # Return previous value




## This function is used to activate the trigger and then use get_pulse_time to get the time it took to receive the echo, including a timeout to recover from a failed reading.
	def getRawData(self, ECHO, TRIG): # ECHO and TRIG pins are dynamic to allow multiple readings from multiple sensors with one function.
                GPIO.output(TRIG, 1) # Reset the Ultrasone sensor.
       		time.sleep(0.00001) # wait a very short time to let it stabilize
        	GPIO.output(TRIG, 0) # Now, FIRE the TRIGGER pin of Ultrasone
       		pulse_time = self.get_pulse_time(ECHO, 1, 0.010) # Get the time it took for the pulse to echo on the surrounding area.

		return str(pulse_time) # Return the data from Ultrasone.




	## https://github.com/rsc1975/micropython-hcsr04/blob/master/hcsr04.py
	## https://github.com/micropython/micropython/blob/f2d732f4596064b3257abe571dc14ab61e02dec9/extmod/machine_pulse.c
 
## This function is responsible for reading the results after a pulse to the Ultrasone sensor but keeps a timeout so that the program won't stall, this happened with the first experiments with the Ultrasone sensor. Code from micropython was used as inspiration for the timeout issues we had during testing.
	def get_pulse_time(self, pin, pinLevel, timeout):
		# Log start time, used for comparing timeout
                start=time.time()

		# check if the gpio pin changes level from initial pinLevel. Try until timeout (us) is reached.
                while GPIO.input(pin) != pinLevel:
                        if (time.time() - start) >= timeout:
                                return -2 # Ok, timeout reached, exit function with -2 returncode.
                start=time.time() # Ok, so we detected a change in the pinLevel, log start time and continue

		# check if the gpio pin changes level to the opposite of the function above. Try until timeout (us) is reached.
                while GPIO.input(pin) == pinLevel:
                        if (time.time() - start) >= timeout:
                                return -1 # Ok, timeout reached, exit function with -1 returncode.
                return (time.time() - start) # return (time.time() - start), this is the time it took to receive a valid response from the sensor and is used to calculate the distance.