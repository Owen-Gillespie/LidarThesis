#Display Data from Neato LIDAR
#based on code from Nicolas "Xevel" Saugnier
#requires vpython and pyserial



import thread, bisect, time, serial, sys, config, traceback, math, matplotlib.pyplot as plt
import numpy as np

index = 0
FullData = [ [0] for i in range(360)]
AdjustedData = [[0] for i in range(720)]
ser = config.ser
readOn=True

pointArray=[[0,0] for i in range(config.maxPoints)]
lastAngle = 0

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
    return checksum==binaryChecksum[0] + (binaryChecksum[1] << 8)

def parse(data):
    index=data[0]-160  #adjust index
    RPM=(data[1]+(data[2]<<8))/64.0
    reading0=[data[3]+((data[4]&0x3F)<<8),data[4]&0x80>>7,data[4]&0x40>>6,data[5]+(data[6]<<8)]
    reading1=[data[7]+((data[8]&0x3F)<<8),data[8]&0x80>>7,data[8]&0x40>>6,data[9]+(data[10]<<8)]
    reading2=[data[11]+((data[12]&0x3F)<<8),data[12]&0x80>>7,data[12]&0x40>>6,data[13]+(data[14]<<8)]
    reading3=[data[15]+((data[16]&0x3F)<<8),data[16]&0x80>>7,data[16]&0x40>>6,data[17]+(data[18]<<8)]
    return [index,RPM,reading0,reading1,reading2,reading3]


def adjustData(data):
    adjustedData=[[0] for x in range(6)]
    adjustedData[0]=data[0]*4
    adjustedData[1]=data[1]
    for x in range(2,6):
        adjustedDataPoint=inverseKinematics(data[x][0], adjustedData[0]+x-1)
        adjustedData[x] = adjustedDataPoint
    return adjustedData

def readLidar():
    init_level=0
    while readOn:
        if init_level==0:
            byte=ser.read(1)
            if ord(byte)==250:
                init_level=1
        if init_level==1:
            result=readPacket()
            if result!=0:
                parsedData=parse(result)
                adjustedData = adjustData(parsedData)
                print "RPM:", adjustedData[1]
                return adjustedData
            else:
                return [0]
def lidarOff():

    ser.write("MotorOff\n")
    ser.close

def lidarOn():
    print "Motor on!"
    ser.write("MotorOn\n")
    ser.write("HideRPM\n")
    ser.write("Set RPM 300")

def inverseKinematics(rho, theta):
    
    theta_offset = config.poseX
    x_offset = config.poseY
    y_offset = config.poseAngle
    
    x_total= x_offset + rho * math.cos(math.radians(theta + theta_offset))
    y_total= y_offset + rho * math.sin(math.radians(theta + theta_offset))
    
    new_rho = int(round(math.sqrt(x_total**2 + y_total**2)))
    if (x_total==0):
        if (y_total==0):
            new_theta=0
        elif (y_total>0):
            new_theta=90
        else:
            new_theta=270
    else:
        new_theta = math.degrees(math.atan(y_total/x_total))
    return [(int(round(new_theta))+360)%360, new_rho]

def storeData(data):
    if data[2][0] < lastAngle:
        lastAngle = 0
    startIndex = find_ge(pointArray, data[2][0])
    endIndex = find_le(pointArray, data[5][0])
    del pointArray[startIndex:endIndex+1]
    pointArray.insert(startIndex,data[2])
    pointArray.insert(startIndex+1,data[3])
    pointArray.insert(startIndex+2,data[4])
    pointArray.insert(startIndex+3,data[5])

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect_left(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError

def runLidar():
    lidarOn()
    while readOn:
        storeData(readLidar())
    lidarOff()
    lidarOff()