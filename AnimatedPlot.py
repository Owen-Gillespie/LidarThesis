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
import datetime, thread, time, serial, sys, traceback, math, timeit
import NewParser as parser 


#Serial Set up

#Parser Setup
init_level = 0
index = 0
FullData = [ [0] for i in range(360)]
RPMData=[0 for i in range(50)]
RPMCounter = 0


# First set up the figure, the axis, and the plot element we want to animate
plt.close('all')
fig = plt.figure()
ax = plt.axes(ylim=(-.1, 2),polar=True) #Creates polar plot
ax.set_ylim(0,3500)
lines = []
analog_data = []
lobj1 = ax.plot([], [], lw=2, color="black")[0]
lobj2 = ax.plot([], [], lw=2, color="red")[0]
lines.append(lobj1)
lines.append(lobj2)
analog_data = []
x_data = np.linspace(0, 2*np.pi, 360)
analog_data.append([0] * len(x_data))
analog_data.append([1] * len(x_data))
start = datetime.datetime.now()
last_x = 0

# initialization function: plot the background of each frame
def init():
    lines[0].set_data([], [])
    lines[1].set_data([], [])
    return lines


# animation function.  This is called sequentially
def animate(i):
    global start, last_x
    newnow = datetime.datetime.now();
    delta = newnow - start;
    start = newnow
    seconds = delta.total_seconds();
    #print("time since last animate = ", seconds)
    samples = round(seconds * 5000)
    x = np.linspace(last_x, last_x + seconds, samples)
    last_x += seconds;
    analog_data[0]=parser.readLidar()
    analog_data[1].extend(np.add(np.multiply(np.abs(np.sin(2 * np.pi * x * -1.0)), .3), 1.3))
    lines[0].set_data(x_data, analog_data[0])
    return tuple(lines)

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=1, interval=0, blit=True)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
#anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
plt.xlabel('Time (s)')
plt.ylabel('Voltage (v)')
plt.show()
plt.grid(True)