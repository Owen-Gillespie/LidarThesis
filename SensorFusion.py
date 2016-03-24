import config, time

def calculatePose(): #The user can define this to work however they want based on the sensors they have
	poseXName = "odmx"
	poseYName = "odmy"
	poseAngleName = "odma"

	if (poseXName in config.sensorData):
		config.poseX = config.sensorData["poseX"]
	if (poseYName in config.sensorData):
		config.poseY = config.sensorData["poseY"]
	if (poseAngleName in config.sensorData):
		config.poseAngle = config.sensorData["poseAngle"]

def sensorFusion():
	n = 0
	while True:
		calculatePose()
		time.sleep(.1)
		print n
		n+=1