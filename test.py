from multiprocessing import Process, Queue, Manager, Value, Array
import time
import argparse

import Ultrasone
import ImageProcessor
import PerimeterIntel

## set program version
pName="test"
pVersion="0.1"

def main():  #link naar argument parser page, uit ball tracking code
	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--daemon", help="daemonize program", type=bool, default=False)
	ap.add_argument("-D", "--debug", help="general program debugging", type=bool, default=False)
	ap.add_argument("-DS", "--sdebug", help="sensor debugging", type=bool, default=False)
	ap.add_argument("-DC", "--cdebug", help="Camera debugging", type=bool, default=False)
	ap.add_argument("-cw", "--cwidth", help="Camera Resolution width", type=int, default=320)
	ap.add_argument("-ch", "--cheight", help="Camera Resolution height", type=int, default=240)
	ap.add_argument("-pw", "--pwidth", help="Processing Resolution width", type=int, default=320)
	ap.add_argument("-ph", "--pheight", help="Processing Resolution height", type=int, default=240)
	ap.add_argument("-b", "--buffer", help="tracing buffer", type=int, default=64)
	args=vars(ap.parse_args())

	print "Starting %s %s" % (str(pName), str(pVersion))
	print "-=====[ Options ]=====-"
	print "--daemon:    %s" % str(args["daemon"])
	print "--debug:     %s" % str(args["debug"])
	print "--sdebug:    %s" % str(args["sdebug"])
	print "--cdebug:    %s" % str(args["cdebug"])
	print "--cwidth:    %s" % str(args["cwidth"])
	print "--cheight:   %s" % str(args["cheight"])
	print "--pwidth:    %s" % str(args["pwidth"])
	print "--pheight:   %s" % str(args["pheight"])
	print "--buffer:    %s" % str(args["buffer"])

	time.sleep(2)

        ## Init Data arrays for trasferring data over smp threads (somewhat simple IPC)
	UltrasoneDataOut=Array('f', range(4))
	ImageProcessorDataOut=Array('f', range(9))
	PerIntelDataIn=Array('f', range(3))
	PerIntelDataOut=Array('f', range(3))

	## Initialize and start processes

	# UltrasoneThread
	ultra=Ultrasone.Ultrasone(args)
	ultrasoneThread=Process(target=ultra.run, args=(UltrasoneDataOut,))
	ultrasoneThread.start()

	# CameraThread
	imageProcessor=ImageProcessor.ImageProcessor(args)
	imageProcessorThread=Process(target=imageProcessor.run, args=(ImageProcessorDataOut,))
	imageProcessorThread.start()

	# PerimeterIntelThread
	perIntel=PerimeterIntel.PerimeterIntel(args)
	perIntelThread=Process(target=perIntel.run, args=(PerIntelDataIn, PerIntelDataOut,)) ## Initialize PerIntelThread and parse PerIntelDataIn and PerIntelDataOut
	perIntelThread.start()




	lastDisplayUpdate=0
	lastDataUpdate=0
	displayUpdateSpeed=0.500
	dataUpdateSpeed=0.1
	try:
		while True:	## Main loop for basic stuff and data transmissions between threads
			time.sleep(0.001) ## don't hog the cpu
			#DATABROKER - if lastDateUpdate is lower than current epoch time, rephresh
			if lastDataUpdate+dataUpdateSpeed < time.time():
				#set current epoch
				lastDataUpdate=time.time()
				#print "---DATAUPDATE---"
				## Data handling/ipc shizzle
				# PerIntelDataIn:
				PerIntelDataIn[0]=UltrasoneDataOut[0]
				PerIntelDataIn[1]=UltrasoneDataOut[1]
				PerIntelDataIn[2]=UltrasoneDataOut[2]




			if lastDisplayUpdate+displayUpdateSpeed < time.time(): ## make sure not to delay the main loop, sure i could use sleep but that's a loss of cycles.... but you allready knew that.
			#sleep(0.1)
				#rephresh lastDisplayUpdate to current epoch time
				lastDisplayUpdate=time.time()
				print "lastDisplayUpdate: %s next: %s)" % (lastDisplayUpdate, (time.time()+displayUpdateSpeed))
				print "BOT Statistics:"
				print "Ultrasone distance L:%i cm F:%s cm R:%i cm" % ( int(UltrasoneDataOut[0]), int(UltrasoneDataOut[2]), int(UltrasoneDataOut[1]) )
				print "Ultrasone samples per second: %s" % ( ( (1/UltrasoneDataOut[3])*3 )*2 ) ## 1/looptime *3 (amount of samples per run) *2 (amount of sensors) = samples per second
				print "Camera Resolution: %sx%s" % (ImageProcessorDataOut[0], ImageProcessorDataOut[1])
				print "Image Processing Resolution: %sx%s" % (ImageProcessorDataOut[2], ImageProcessorDataOut[3])
				print "Image Processing speed: %s fps" % (1/ImageProcessorDataOut[8]) ## 1/looptime = opencv thread fps
				print "Obstructions: LEFT:%s FRONT:%s RIGHT:%s" % (PerIntelDataOut[0], PerIntelDataOut[1], PerIntelDataOut[2])
				print ""
				print "Object Statistics:"
				print "Object detected: %s"  % ImageProcessorDataOut[4]
				print "Object Radius: %s" % ImageProcessorDataOut[5]
				print "Object Location: x:%s y:%s" % (ImageProcessorDataOut[6], ImageProcessorDataOut[7])
			

	except KeyboardInterrupt:
		print "CTRL+C Shutting down..."
		sensorThread.join()
		imageProcessorThread.join()
		perIntelThread.join()

if __name__ == '__main__':
	main()
