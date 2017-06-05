from multiprocessing import Process, Manager, Value, Array	# Used for handling multicore processing
import time							# Used for timing and sleep functions
import argparse							# Used for parsing commandline arguments
import Ultrasone						# Ultrasone functions	(Detect distance to objects)
import ImageProcessor						# OpenCV functions	(process camera and detect object)
import PerimeterIntel						# Perimeter functions	(basic driving intelligence like obstacle detection based on Ultrasone)

## set program version
pName="DrivingFridgeRobot"
pVersion="0.2"

def main():  
## Use argparse to pass options/variables to main process and child processes (Used parts of the code on http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/ as reference for my argument parser)
	# Add arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--daemon", help="daemonize program", type=bool, default=False) ## no gui is loaded, if this is set the program can be run from the commandline without X (headless)
	ap.add_argument("-D", "--debug", help="Enable general program debugging", type=bool, default=False)
	ap.add_argument("-DS", "--sdebug", help="Enable sensor debugging", type=bool, default=False)
	ap.add_argument("-DC", "--cdebug", help="Enable camera debugging", type=bool, default=False)
	ap.add_argument("-cw", "--cwidth", help="Camera Resolution width", type=int, default=320)
	ap.add_argument("-ch", "--cheight", help="Camera Resolution height", type=int, default=240)
	ap.add_argument("-pw", "--pwidth", help="Processing Resolution width", type=int, default=320)
	ap.add_argument("-ph", "--pheight", help="Processing Resolution height", type=int, default=240)
	ap.add_argument("-b", "--buffer", help="tracing buffer (red line in gui tracing object)", type=int, default=64)
	args=vars(ap.parse_args())

	# Print settings on startup
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

	# Give us some time to actually read the arguments before the program starts
	time.sleep(2)

## Init Data arrays for trasferring data over smp threads (somewhat simple IPC)
        # DataManager
        dataManager=Manager() ## Use Manager from multiprocessing to synchronize data objects (basically pass proxies to threads instead of actual arrays, the server is in the parent program)

        # Array objects, used for transporting data using proxies to communicate between threads (IPC part)
	UltrasoneDataOut=dataManager.Array('f', range(7))
	ImageProcessorDataOut=dataManager.Array('f', range(9))
	PerIntelDataIn=dataManager.Array('f', range(4))
	PerIntelDataOut=dataManager.Array('f', range(3))

## Initialize and start processes
	# UltrasoneThread
	ultra=Ultrasone.Ultrasone(args)	# Create ultra object from Ultrasone class with args
	ultrasoneThread=Process(target=ultra.run, args=(UltrasoneDataOut,)) # Create ultrasoneThread to run function "run" of Ultrasone.Ultrasone. Parse UltrasoneDataOut proxy to store values
	ultrasoneThread.start() # Now start the thread!

	# CameraThread
	imageProcessor=ImageProcessor.ImageProcessor(args) # Create imageProcessor object from imageProcessor class with args
	imageProcessorThread=Process(target=imageProcessor.run, args=(ImageProcessorDataOut,)) # Create imageProcessorThread to run function "run" of imageProcessor.ImageProcessor. Parse ImageProcessorDataOut proxy to store values
	imageProcessorThread.start() # Now start this thread also!

	# PerimeterIntelThread
	perIntel=PerimeterIntel.PerimeterIntel(args) # Create perIntel object from PerimeterIntel class with args
	perIntelThread=Process(target=perIntel.run, args=(PerIntelDataIn, PerIntelDataOut,)) ## Create PerIntelThread thread to run function "run" of PerimeterIntel.PerimeterIntel. Pass PerIntelDataIn and PerIntelDataOut proxies to process and store values
	perIntelThread.start() # Fire!

## Timing settings for displaying statistics on console and transferring data to proxies
	# Last time the display was updated
	lastDisplayUpdate=0
        # Last time in us that the proxies were updated.
	lastDataUpdate=0
        # Print stats every 500ms
	displayUpdateSpeed=0.500
        # Update data proxies every 10ms
	dataUpdateSpeed=0.01

## Here starts the main loop
	try:
		while True: ## Main loop for displaying statistics and data handling transmissions between threads
			time.sleep(0.001) ## don't hog the cpu (atleast set some sort of limit to prevent the CPU from flooding with the while True loop

			# dataManager - if lastDateUpdate is lower than current epoch time, then update data values. This must happen often but not continuesly.
			if lastDataUpdate+dataUpdateSpeed < time.time():
				# Get current epoch time in us
				lastDataUpdate=time.time()

				# Pass data from various sources to PerIntelDataIn:
				PerIntelDataIn[0]=UltrasoneDataOut[0]      # Left Ultrasone sensor values
				PerIntelDataIn[1]=UltrasoneDataOut[1]      # Front Ultrasone sensor values
				PerIntelDataIn[2]=UltrasoneDataOut[2]      # Right Ultrasone sensor values
				PerIntelDataIn[3]=ImageProcessorDataOut[4] # Object detected
				PerIntelDataIn[4]=ImageProcessorDataOut[5] # Object radius
				PerIntelDataIn[5]=ImageProcessorDataOut[6] # Object location X
				PerIntelDataIn[6]=ImageProcessorDataOut[7] # Object location Y


                        ## make sure not to delay the main loop, sure i could use sleep but that's a loss of cycles.... but you allready knew that.
			if lastDisplayUpdate+displayUpdateSpeed < time.time(): ## make sure not to delay the main loop, sure i could use sleep but that's a loss of cycles.... but you allready knew that.
				lastDisplayUpdate=time.time() # Update lastDisplayUpdate with the current epoch time in us

                                # Print statistics.
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

			
## Try to handle and cleanup incase someone hits CTRL+C
	except KeyboardInterrupt:
		print "CTRL+C Shutting down..."
		sensorThread.join()
		imageProcessorThread.join()
		perIntelThread.join()

## If I'm started execute main() and let the magick begin.
if __name__ == '__main__':
	main()
