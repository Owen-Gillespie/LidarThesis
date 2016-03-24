import config, threading, SensorFusion, time, UDPReciever, NewParser

sensorReciever = threading.Thread(target=SensorFusion.sensorFusion, args = ())
sensorReciever.daemon = True

udpReciever = threading.Thread(target=UDPReciever.run, args = ())
udpReciever.daemon = True

parser = threading.Thread(target=NewParser.runLidar, args = ())
parser.daemon = True


udpReciever.start()
sensorReciever.start()
parser.start()
time.sleep(5)
NewParser.readOn = False
print NewParser.readOn
time.sleep(1)