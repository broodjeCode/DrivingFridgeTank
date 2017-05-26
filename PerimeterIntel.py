from multiprocessing import Process
import time

import Ultrasone

class PerimeterIntel(Process):

	def __init__(self,ultra,image):
		debug=False
		self.ultra=ultra
		self.image=image

	def run(self):
		while True:
			time.sleep(1)
			print str(self.ultra.getDist())



#	isWallFront = False
#	isWallLeft = False
#	isWallRight = False
#
#
#
#
#	UltrasoneLeft = Ultrasone()
#	UltrasoneRight = Ultrasone()
#	ip = ImageProcessor()
#
#	def __init__(self):
#
#
#	
#
#
#
#	def getObjectInSIght
#		return ImageProcessor.objectInSight
#
#	def getDistLeft()
#		return 
#
#	def getDistRight()
#		pass
#
#
#
#
#
#	while(true)
#		UltrasoneLeft.getDist()
#		UltrasoneRight.getDist()
