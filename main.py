import config, threading, SensorFusion, time, UDPReciever, NewParser

sensorReciever = threading.Thread(target=SensorFusion.sensorFusion, args = ())
sensorReciever.daemon = True

udpReciever = threading.Thread(target=UDPReciever.run, args = ())
udpReciever.daemon = True

parser = threading.Thread(target=NewParser.runLidar, args = ())
parser.daemon = True

analysis = threading.Thread(target=NewParser.frameAnalysis, args = ())


udpReciever.start()
sensorReciever.start()
parser.start()
#analysis.start()
time.sleep(15)
NewParser.readOn = False
print NewParser.readOn
time.sleep(1)