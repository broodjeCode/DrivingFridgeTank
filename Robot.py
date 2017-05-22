class Robot
import time

	serviceRequest = False
	inOperation = False


	pf = Pathfinder()


	#loop
	while(true)
		
		if(serviceRequest && !inOperation)
			serviceRequest = False
			inOperation = True
			timeOfInit = datetime.datetime.now()
			
			pf.findPath()
		else
			time.sleep(1)



		if(timeExceeded)
