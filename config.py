import serial

poseX = 0  #Coordinates in feet
poseY = 0
poseAngle = 0 #Angle stored in degrees

maxLines = 30
minLength = 10
sensorData={}

maxPoints=1000 #Maximum number of points stored in one rotation. Should be chosen based on platforms max rotating speed. 
com_port = "COM3" # example: 5 == "COM6" == "/dev/tty5" # Windows
# com_port = "/dev/cu.usbmodem12341" # Mac OS X
# com_port = "/dev/ttyACM0" # Beaglebone Black Ubuntu
baudrate = 115200

# On Mac OS X, to see which port, run $ python -m serial.tools.list_ports
ser = serial.Serial(com_port, baudrate)
readOn=True
debug=False