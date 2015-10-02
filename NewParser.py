#Display Data from Neato LIDAR
#based on code from Nicolas "Xevel" Saugnier
#requires vpython and pyserial


import thread, time, serial, sys, traceback, math, matplotlib.pyplot as plt
import numpy as np

com_port = "COM3" # example: 5 == "COM6" == "/dev/tty5" # Windows
# com_port = "/dev/cu.usbmodem12341" # Mac OS X
# com_port = "/dev/ttyACM0" # Beaglebone Black Ubuntu
baudrate = 115200

# On Mac OS X, to see which port, run $ python -m serial.tools.list_ports

ser = serial.Serial(com_port, baudrate)
ser.write("MotorOn\n")
ser.write("HideRPM\n")
ser.write("Set RPM 280")
time.sleep(5)
ser.flushOutput()
index = 0
read=True
FullData = [ [0] for i in range(360)]
polarDistances=[i[0] for i in FullData]
polarAngles=[math.pi*2.0/360.0*i for i in range(360)]
RPMData=[0 for i in range(50)]
RPMCounter = 0

#plt.ion()
#plt.show()


def readPacket():
    data=[ord(b) for b in ser.read(19)]
    #print data
    #print ser.inWaiting()
    if checksum(data):
        #print "True!"
        #print data[0]
        return data
    else:
        #print "False!"
        return 0

def checksum(data):
    dataList=[]
    chk32=0
    dataList.append(0xFA + (data[0] << 8))
    for x in range(9):
        dataList.append(data[2*(x+1)-1] + (data[2*(x+1)]<<8))
    
    for d in dataList:
        chk32= (chk32 << 1) + d

    checksum= (chk32 & 0x7FFF) + (chk32 >> 15)
    checksum=checksum & 0x7FFF
    binaryChecksum=[ord(b) for b in ser.read(2)]
    #print binaryChecksum
    #print checksum
    return checksum==binaryChecksum[0] + (binaryChecksum[1] << 8)

def parse(data):
    index=data[0]-160  #adjust index
    RPM=(data[1]+(data[2]<<8))/64.0
    #print RPM 
    reading0=[data[3]+((data[4]&0x3F)<<8),data[4]&0x80>>7,data[4]&0x40>>6,data[5]+(data[6]<<8)]
    reading1=[data[7]+((data[8]&0x3F)<<8),data[8]&0x80>>7,data[8]&0x40>>6,data[9]+(data[10]<<8)]
    reading2=[data[11]+((data[12]&0x3F)<<8),data[12]&0x80>>7,data[12]&0x40>>6,data[13]+(data[14]<<8)]
    reading3=[data[15]+((data[16]&0x3F)<<8),data[16]&0x80>>7,data[16]&0x40>>6,data[17]+(data[18]<<8)]
    return [index,RPM,reading0,reading1,reading2,reading3]


def storeData(data):
    tempIndex=data[0]*4
    FullData[tempIndex]=data[2]
    FullData[tempIndex+1]=data[3]
    FullData[tempIndex+2]=data[4]
    FullData[tempIndex+3]=data[5]
    return 0

def updateDisplay():
    polarDistances=[i[0] for i in FullData]
    polarAngles=[math.pi*2.0/360.0*i for i in range(360)]
    #print "update!"
    plt.draw()


def readLidar():
    init_level=0
    while True:
        if init_level==0:
            byte=ser.read(1)
            if ord(byte)==250:
                init_level=1
        if init_level==1:
            result=readPacket()
            if result!=0:
                parsedData=parse(result)
                storeData(parsedData)
                return [i[0] for i in FullData]
            else:
                return 0
            
print readLidar()            
ser.write("MotorOff\n")
ser.close


