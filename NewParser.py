#Display Data from Neato LIDAR
#based on code from Nicolas "Xevel" Saugnier
#requires vpython and pyserial



import thread, bisect, time, serial, sys, config, traceback, math,cv2, matplotlib.pyplot as plt
import numpy as np
import bottleneck as bn



index = 0
FullData = [ [0] for i in range(360)]
AdjustedData = [[0] for i in range(720)]
ser = config.ser
readOn=True

pointAngleArray=[0]
pointDistanceArray=[0]
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
                if config.debug:
                    print "RPM:", adjustedData[1]
                return adjustedData
            else:
                return [0]
def lidarOff():
    print "Off"
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
    if new_rho == 53:
        print "Dumb sensor"
        new_rho=4000
    return [(int(round(theta))+719)%360, new_rho]  #Fix it so new_theta is correct

def storeData(data):
    if len(data)!=6:
        return
    if config.debug:
        print data
    global lastAngle
    currentAngle = data[2][0]
    if currentAngle < lastAngle:
        lastAngle = 0
    startIndex = find_le(pointAngleArray, currentAngle)#Wrong!
    endIndex = find_ge(pointAngleArray, data[5][0])#Wrong!
    if config.debug:
        print "Start Index:", startIndex, currentAngle
        print "End Index:", endIndex, data[5][0]
    if endIndex==0:
        del pointAngleArray[startIndex:]
        del pointDistanceArray[startIndex:]
    else:
        del pointAngleArray[startIndex:endIndex]
        del pointDistanceArray[startIndex:endIndex]
    pointAngleArray.insert(startIndex,data[2][0])
    pointAngleArray.insert(startIndex+1,data[3][0])
    pointAngleArray.insert(startIndex+2,data[4][0])
    pointAngleArray.insert(startIndex+3,data[5][0])
    pointDistanceArray.insert(startIndex,data[2][1])
    pointDistanceArray.insert(startIndex+1,data[3][1])
    pointDistanceArray.insert(startIndex+2,data[4][1])
    pointDistanceArray.insert(startIndex+3,data[5][1])
    if config.debug:
        print pointAngleArray

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_right(a, x)
    if i != len(a):
        return i
    return 0

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect.bisect_left(a, x)
    if i:
        return i
    return 0

def runLidar():
    lidarOn()
    while readOn:
        for x in range(45):
            storeData(readLidar())
        frameAnalysis()
    lidarOff()
    lidarOff()

def frameAnalysis():
    image=np.zeros((4000,4000), np.uint8)
    for index in range(len(pointAngleArray)):
        theta=pointAngleArray[index]
        rho=pointDistanceArray[index]
        x,y=pol2cart(rho, math.radians(theta))
        if config.debug:
            print x,y
        if -2000<x<2000 and -2000<y<2000:
            image[2000+x][2000+y]= 200
    accumulator, thetas, rhos = hough_line(image)
    arr = np.ravel(accumulator)
    sortedArr=bn.argpartsort(arr, n=arr.shape[0]-config.maxLines)
    possibleLines=sortedArr[-config.maxLines:]
    lines=[]
    for x in range(len(possibleLines)):
        index=possibleLines[x]
        rho = rhos[index / accumulator.shape[1]]
        theta = thetas[index % accumulator.shape[1]]
        for i in range(x+1,len(possibleLines)):
            index2 = possibleLines[i]
            rho2 = rhos[index2 / accumulator.shape[1]]
            theta2 = thetas[index2 % accumulator.shape[1]]
            #print "Theta1: " + repr(theta) + " Theta2: " + repr(theta2) + " Rho1: " + repr(rho) + " Rho2: " + repr(rho2)
            if abs(theta-theta2) < .04 and ((rho > 0) == (rho2>0)):
                #print "Merge suceeded"
                arr[index]+= arr[index2]
                arr[index2]=0
                theta = (theta + theta2)/2.
                rho = (rho + rho2)/2
            #else:
            #    print "Merge failed"
        if arr[index] >= config.minLength:
            print "index:"
            print arr[index]
            lines.append([arr[index],theta,rho])
            print "rho={0:.2f}, theta={1:.0f}".format(rho, np.rad2deg(theta))
    cv2.imwrite('houghlines3.jpg',image)

def hough_line(img):
  # Rho and Theta ranges
  thetas = np.deg2rad(np.arange(-90.0, 90.0))
  width, height = img.shape
  diag_len = np.ceil(np.sqrt(width * width + height * height))   # max_dist
  print "Diag len: " + repr(diag_len)
  rhos = np.linspace(-diag_len, diag_len, diag_len * 2.0)

  # Cache some resuable values
  cos_t = np.cos(thetas)
  sin_t = np.sin(thetas)
  num_thetas = len(thetas)

  # Hough accumulator array of theta vs rho
  accumulator = np.zeros((2 * diag_len, num_thetas), dtype=np.uint64)
  y_idxs, x_idxs = np.nonzero(img)  # (row, col) indexes to edges

  # Vote in the hough accumulator
  for i in range(len(x_idxs)):
    x = x_idxs[i]
    y = y_idxs[i]

    for t_idx in range(num_thetas):
      # Calculate rho. diag_len is added for a positive index
      rho = round((x-2000) * cos_t[t_idx] + (y-2000) * sin_t[t_idx]) + diag_len
      accumulator[rho, t_idx] += 1

  return accumulator, thetas, rhos

def pol2cart(rho, theta):
    x = rho * math.cos(theta)
    y = rho * math.sin(theta)
    return(x, y)