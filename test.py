from multiprocessing import Process, Queue, Manager, Value, Array
from time import sleep as sleep
import Ultrasone
import Camera
import argparse

## set program version
pName="test"
pVersion="0.1"

def main():
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

	sleep(2)

	manager = Manager()

        ## Define shared Values (for SMP/Threading IPC)
	distanceLValue=Value('f',0)
	distanceRValue=Value('f',0)
	cameraResolutionValueX=Value('i',0)
	processingResolusionValueX=Value('i',0)
        cameraResolutionValueY=Value('i',0)
        processingResolusionValueY=Value('i',0)
	objectDetectValue=Value('b',0)
	objectRadiusValue=Value('d',0)
	objectLocationValueX=Value('i',0)
        objectLocationValueY=Value('i',0)

	## Initialize and start processes
	ultra=Ultrasone.Ultrasone(args)
	sensorThread=Process(target=ultra.run, args=(distanceLValue,distanceRValue,))
	sensorThread.start()
	camera=Camera.cameraThread(args)
	cameraThread=Process(target=camera.run, args=(cameraResolutionValueX,cameraResolutionValueY,processingResolusionValueX,processingResolusionValueY,objectDetectValue,objectRadiusValue,objectLocationValueX,objectLocationValueY,))
	cameraThread.start()






	try:
		while(1):
			sleep(0.1)
			print "BOT Statistics:"
			print "Ultrasone distance L:%i cm R:%i cm" % ( int(distanceLValue.value), int(distanceRValue.value) )
			print "Camera Resolution: %sx%s" % (cameraResolutionValueX.value, cameraResolutionValueY.value)
			print "Processing Resolution: %sx%s" % (processingResolusionValueX.value, processingResolusionValueY.value)
			print ""
			print "Object Statistics:"
			print "Object detected: %s"  % objectDetectValue.value
			print "Object Radius: %s" % objectRadiusValue.value
			print "Object Location: x:%s y:%s" % (objectLocationValueX.value, objectLocationValueY.value)
			

	except KeyboardInterrupt:
		print "CTRL+C Shutting down..."
		sensorThread.join()

if __name__ == '__main__':
	main()
