#!/usr/bin/env python3 -u
import os

import matplotlib.pyplot as plt
import numpy as np

WORKDIR = os.path.expanduser('~/PAV/P5')
SAMPLING_FREQ = 44100


data = np.loadtxt(f'{WORKDIR}/work/graphs/interpolation-data.txt')

tablel = data[:,0]
tabler = data[:,1]
tablelerp = data[:,2]

ndata = len(tablel)
t = np.linspace(0, (ndata - 1)/SAMPLING_FREQ, ndata)

il = 2**15
ir = il + 2**7

mark = 'o'
marksize = 8

plottype = plt.scatter

plottype(t[il:ir], tablel[il:ir], marker=mark, s=marksize, c='blue', label='Ceil values')
plottype(t[il:ir], tabler[il:ir], marker=mark, s=marksize, c='red', label='Floor values')
plottype(t[il:ir], tablelerp[il:ir], marker=mark, s=4*marksize, c='green', label='Lerp values')

plt.title('Table interpolation')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid()

plt.legend()
plt.savefig(f'{WORKDIR}/img/table-interpolation.png', dpi=200)
plt.show()

