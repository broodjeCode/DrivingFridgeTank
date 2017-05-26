from multiprocessing import Process
import time

class PerimeterIntel(Process):

	def __init__(self, args):
		self.debug=args["debug"]

	def run(self, PerIntelDataIn, PerIntelDataOut):
		while True:
			sleep(0.1)
			if self.debug:
				print "PerIntel: L:%s, F:%s, R:%s" % (PerIntelDataIn[0], PerIntelDataIn[1], PerIntelDataIn[2])
				# Check vehicle boundaries
			for i in range(len(PerIntelDataIn)):
				if self.debug:
					print "PerIntel: %s" % PerIntelDataIn[i]
				if i==1:
					if PerIntelDataIn[i] <= 20:
						PerIntelDataOut[i]=1
					else:
						PerIntelDataOut[i]=0
				else:
					if PerIntelDataIn[i] <= 15:
						PerIntelDataOut[i]=1
					else:
						PerIntelDataOut[i]=0

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
