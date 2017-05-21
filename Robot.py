class Robot
import time

	
	inOperation = false


	pf = Pathfinder()



	while(true)
		
		if(serviceRequest)
			serviceRequest = false
			inOperation = true
			timeOfInit = datetime.datetime.now()
			
			pf.findPath()



		if(timeExceeded)
