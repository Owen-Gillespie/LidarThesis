"""
Matplotlib Animation Example

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
Please feel free to use and modify this, but keep the above information. Thanks!
""" 

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import datetime, thread, time, serial, sys, traceback, math, timeit, time
import NewParser as parser
import cv2 


#Serial Set up

#Parser Setup
init_level = 0
index = 0
FullData = [ [0] for i in range(360)]
RPMData=[0 for i in range(50)]
RPMCounter = 0
ptArray=np.zeros((1000,1000), np.uint8)

def pol2cart(rho, phi):
    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
    return(x, y)

# First set up the figure, the axis, and the plot element we want to animate
plt.close('all')
fig = plt.figure()
ax = plt.axes(ylim=(-.1, 2),polar=True) #Creates polar plot
ax.set_ylim(0,3500)
lines = []
x_data = np.linspace(0, 2*np.pi, 360)
analog_data = [0] * len(x_data)
lobj1 = ax.plot([], [], lw=2, color="black")[0]
lines.append(lobj1)

# initialization function: plot the background of each frame
def init():
    lines[0].set_data([], [])
    return lines


# animation function.  This is called sequentially
def animate(i):
    analog_data=parser.readLidar()
    for index, item in enumerate(analog_data):
    	x,y = pol2cart(item,x_data[index])
    	ptArray[max(min(999,(int)(x+500)),0)][max(min(999,(int)(y+500)),0)]=200
    lines[0].set_data(x_data, analog_data)
    '''print np.sum(ptArray)'''
    return tuple(lines)



# call the animator.  blit=True means only re-draw the parts that have changed.
'''anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=1, interval=0, blit=True)'''
plt.xlabel('Time (s)')
plt.ylabel('Voltage (v)')
plt.ion()
plt.show()
for i in range(300):
	print i
	animate(i)
	plt.draw()

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
#anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

plt.grid(True)
print '4'
Houghlines = cv2.HoughLines(ptArray,1,np.pi/180,10)
print '5'
print Houghlines
print '3'
for i in Houghlines:
	rho=i[0][0]
	theta= i[0][1]
	a = np.cos(theta)
	b = np.sin(theta)
	x0 = a*rho
	y0 = b*rho
	x1 = int(x0 + 1000*(-b))
	y1 = int(y0 + 1000*(a))
	x2 = int(x0 - 1000*(-b))
	y2 = int(y0 - 1000*(a))

	cv2.line(ptArray,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imshow('lines', ptArray)
cv2.waitKey(0)
cv2.imwrite('houghlines2.jpg',ptArray)
print np.sum(ptArray)
print '6'