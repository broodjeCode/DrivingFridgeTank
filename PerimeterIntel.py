from multiprocessing import Process
import time

class PerimeterIntel(Process):

	def __init__(self, args):
		debug=args["debug"]

	def run(self, PerIntelDataIn, PerIntelDataOut):
		while True:
			time.sleep(1)
			print "PerIntel: L:%s, F:%s, R:%s" % (PerIntelDataIn[0], PerIntelDataIn[1], PerIntelDataIn[2])

#import Ultrasone
#
#class PerimeterIntel
#
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
