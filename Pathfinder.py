class Pathfinder
	
	timesTurned = 0
	distLeft = 0
	distRight = 0
	operational = false

	PerimeterIntel = PerimeterIntel()
	MovementProcessor = MovementProcessor()

	def __init__(self):


	def startPathfinder(self)
		operational = true
		mainOp()


	def cancelPathfinder(self)
		operational = false


	def mainOp(self)

		while(operational)
			
			distLeft  = PerimeterIntel.getDistLeft()
			distRight = PerimeterIntel.getDistRight()

	def findTarget