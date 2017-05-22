class Robot
import time

	
	inOperation = false


	pf = Pathfinder()


	#loop
	while(true)
		
		if(serviceRequest && !inOperation)
			serviceRequest = false
			inOperation = true
			timeOfInit = datetime.datetime.now()
			
			pf.findPath()
		else
			time.sleep(1)



		if(timeExceeded)
