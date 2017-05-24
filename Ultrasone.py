class Ultrasone
	import RPi.GPIO as GPIO
	import time
	import math
	from array import *

	debug = true


	def __init__(self):

		GPIO.setmode(GPIO.BOARD)
		#if left !exist
		TRIG = 7
		ECHO = 12
		#else andere pins
		

		GPIO.setup(TRIG, GPIO.OUT)
		GPIO.output(TRIG, 0)

		GPIO.setup(ECHO, GPIO.IN)

	def getDist(self)
		
		i=0
		results = array('d')
		
		while i<5
			var = getRawData()
			if (var != NULL) # && niet buitengewoon groot of klein na vorige meting?
				results.append(var)
		avgRaw = sum(results) / float(len(results))
		avgCM = avgRaw * 17000

		if (debug)
			for i in results:
				print(i),
				print(results[i]),

		return avgCM








	def getRawData(self)

		#marco
		GPIO.output(TRIG, 1)
		time.sleep(0.00001)
		GPIO.output(TRIG, 0)


		#polo
		while GPIO.input(ECHO) == 0:
			pass
		start = time.time()
	
		while GPIO.input(ECHO) == 1:
			pass
		stop = time.time()

		return (stop - start)