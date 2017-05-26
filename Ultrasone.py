import sys
import os
import RPi.GPIO as GPIO
import time
import math
from array import *
from multiprocessing import Process

class Ultrasone(Process):
	def __init__(self, args):
		self.distance=([0,0,0]) ## Empty array for L, F, R sensors
		self.loopCompletedTime=1
                self.debug=args["sdebug"]
		GPIO.setmode(GPIO.BOARD)
		#if left !exist


		## Ultrasone pins
		self.TRIG1 = 7
		self.ECHO1 = 12

		self.TRIG2 = 15
		self.ECHO2 = 16
		#else andere pins

		## Setup GPIO
		GPIO.setup(self.TRIG1, GPIO.OUT)
		GPIO.setup(self.ECHO1, GPIO.IN)
		GPIO.output(self.TRIG1, 0)

		GPIO.setup(self.TRIG2, GPIO.OUT)
		GPIO.setup(self.ECHO2, GPIO.IN)
		GPIO.output(self.TRIG2, 0)

	def run(self, UltrasoneData):
		while True:
				self.loopStartTime=time.time()  ## save loop speed
				self.distance[0]=self.PrivGetDist(self.ECHO1, self.TRIG1, self.distance[0])
				self.distance[1]=self.PrivGetDist(self.ECHO2, self.TRIG2, self.distance[1])

				if self.debug:
					print "Distance: %s cm" % str(self.distance)
				UltrasoneData[0]=self.distance[0]  #float(self.distance)
				UltrasoneData[1]=self.distance[1]  # Right sensor
				UltrasoneData[2]=25.44
				self.loopCompletedTime=(time.time() - self.loopStartTime) ## calculate loop speed
				UltrasoneData[3]=self.loopCompletedTime



	## https://github.com/rsc1975/micropython-hcsr04/blob/master/hcsr04.py
	## https://github.com/micropython/micropython/blob/f2d732f4596064b3257abe571dc14ab61e02dec9/extmod/machine_pulse.c
        def get_pulse_time(self, pin, pinLevel, timeout):
                start=time.time()
                while GPIO.input(pin) != pinLevel:
                        if (time.time() - start) >= timeout:
                                return -2
                start=time.time()
                while GPIO.input(pin) == pinLevel:
                        if (time.time() - start) >= timeout:
                                return -1
                return (time.time() - start)


	def PrivGetDist(self, ECHO, TRIG, previousValue):
		
		i=0
		results = [] #array()
		
		while i<3:
			time.sleep(0.001)
                        i=i+1
			var = self.getRawData(ECHO, TRIG)
			if (var >=0 ): # && niet buitengewoon groot of klein na vorige meting?
				results.append(var)


		fResults=[float(i) for i in results] ## convert values to a nice float
		avgRaw = sum(fResults) / float(len(fResults))
		avgCM = avgRaw * 17000

		if (self.debug):
			for i in results:
				print(i),
				print(str(results)),

		if avgCM >= 0:
			return avgCM ## Return calculated value
		else:
			return previousValue


	def getRawData(self, ECHO, TRIG):
                GPIO.output(TRIG, 1)
       		time.sleep(0.00001)
        	GPIO.output(TRIG, 0)
       		pulse_time = self.get_pulse_time(ECHO, 1, 0.010)

		return str(pulse_time)
