import sys
import os
import RPi.GPIO as GPIO
import time
import math
from array import *

class Ultrasone():
	def __init__(self):
                self.debug=False
		GPIO.setmode(GPIO.BOARD)
		#if left !exist
		self.TRIG = 7
		self.ECHO = 12
		#else andere pins
		

		GPIO.setup(self.TRIG, GPIO.OUT)
		GPIO.output(self.TRIG, 0)
		GPIO.setup(self.ECHO, GPIO.IN)


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


	def getDist(self):
		
		i=0
		results = [] #array()
		
		while i<5:
                        i=i+1
			var = self.getRawData()
			if (var != None): # && niet buitengewoon groot of klein na vorige meting?
				results.append(var)

#		i=1
#		for i in results: ## Check if value is positive, otherwise error
#	                print 
#			if int(results[i]) <= 0:
#				print "ERROR"
#				return 0

		fResults=[float(i) for i in results] ## convert values to a nice float
		avgRaw = sum(fResults) / float(len(fResults))
		avgCM = avgRaw * 17000
#		avgCM = (fResults[1] / 2) / 29.1

		if (self.debug):
			for i in results:
				print(i),
				print(str(results)),

		return avgCM


	def getRawData(self):
                TRIG=self.TRIG
                ECHO=self.ECHO

                GPIO.output(TRIG, 1)
       		time.sleep(0.00001)
        	GPIO.output(TRIG, 0)
       		pulse_time = self.get_pulse_time(ECHO, 1, 0.900)

		print str(pulse_time)

		return str(pulse_time)

		#marco
#		GPIO.output(TRIG, 1)
#		time.sleep(0.00001)
#		GPIO.output(TRIG, 0)
#
#                print "aids"
#		#polo
#		while GPIO.input(ECHO) == 0:
#			pass
#		start = time.time()
#	
#		while GPIO.input(ECHO) == 1:
#			pass
#		stop = time.time()
#
#		return (stop - start)



distance=Ultrasone()
print distance.getDist()
