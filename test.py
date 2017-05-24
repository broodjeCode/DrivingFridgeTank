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
	distanceValue=Value('d',0)
	cameraResolutionValueX=Value('d',0)
	processingResolusionValueX=Value('d',0)
        cameraResolutionValueY=Value('d',0)
        processingResolusionValueY=Value('d',0)
	objectRadiusValue=Value('d',0)
	objectLocationValueX=Value('d',0)
        objectLocationValueY=Value('d',0)



	ultra=Ultrasone.Ultrasone()
	camera=Camera.cameraThread()
	sensorThread=Process(target=ultra.run, args=(distanceValue,))
	cameraThread=Process(target=camera.run, args=(args,))
	sensorThread.start()






	try:
		while(1):
			sleep(0.001)
			print "swek %s" % distanceValue.value

	except KeyboardInterrupt:
		print "CTRL+C Shutting down..."
		sensorThread.join()

if __name__ == '__main__':
	main()
