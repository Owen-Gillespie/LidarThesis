import socket, config

def run():
	UDP_IP = "127.0.0.1"
	UDP_PORT = 5005

	sock = socket.socket(socket.AF_INET, # Internet
	                     socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT))

	while True:
	    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	    print "received message:", data
	    if len(data) >= 4:
		    config.sensorData[data[0:4]]=data[4:]
		    print data[0:4], config.sensorData[data[0:4]]
