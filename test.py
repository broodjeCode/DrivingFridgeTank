from multiprocessing import Process, Queue, Manager, Value, Array
from time import sleep as sleep
import Ultrasone
import Camera

def main():
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
	camera=Camera.
	sensorThread=Process(target=ultra.run, args=(distanceValue,))
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
