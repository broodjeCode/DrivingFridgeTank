from multiprocessing import Process, Queue, Manager, Value, Array
import time
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

	time.sleep(2)

	manager = Manager()

        ## Define shared Values (for SMP/Threading IPC)
	UltrasoneData=Array('f', range(4));
	CameraData=Array('f', range(9) )
	

	## Initialize and start processes
	ultra=Ultrasone.Ultrasone(args)
	sensorThread=Process(target=ultra.run, args=(UltrasoneData,))
	sensorThread.start()

	camera=Camera.cameraThread(args)
	cameraThread=Process(target=camera.run, args=(CameraData,))
	cameraThread.start()





	lastDisplayUpdate=0
	updateSpeed=1
#	try:
	while(1):
			if lastDisplayUpdate+updateSpeed < time.time(): ## make sure not to delay the main loop, sure i could use sleep but that's a loss of cycles.... but you allready knew that.
			#sleep(0.1)
				lastDisplayUpdate=time.time()
				print "lastDisplayUpdate: %s next: %s)" % (lastDisplayUpdate, (time.time()+updateSpeed))
				print "BOT Statistics:"
				print "Ultrasone distance L:%i cm F:%s cm R:%i cm" % ( int(UltrasoneData[0]), int(UltrasoneData[2]), int(UltrasoneData[1]) )
				print "Ultrasone samples per second: %s" % ( ( (1/UltrasoneData[3])*3 )*2 ) ## 1/looptime *3 (amount of samples per run) *2 (amount of sensors) = samples per second
				print "Camera Resolution: %sx%s" % (CameraData[0], CameraData[1])
				print "Image Processing Resolution: %sx%s" % (CameraData[2], CameraData[3])
				print "Image Processing speed: %s fps" % (1/CameraData[8]) ## 1/looptime = opencv thread fps
				print ""
				print "Object Statistics:"
				print "Object detected: %s"  % CameraData[4]
				print "Object Radius: %s" % CameraData[5]
				print "Object Location: x:%s y:%s" % (CameraData[6], CameraData[7])
			

#	except KeyboardInterrupt:
#		print "CTRL+C Shutting down..."
#		sensorThread.join()

if __name__ == '__main__':
	main()
