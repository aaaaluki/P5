#!/usr/bin/env python3 -u
import os

import matplotlib.pyplot as plt
import numpy as np

from config import *


data = np.loadtxt(f'{WORKDIR}/work/graphs/interpolation-data.txt')

tablel = data[:,0]
tabler = data[:,1]
tablelerp = data[:,2]

ndata = len(tablel)
t = np.linspace(0, (ndata - 1)/SAMPLING_FREQ, ndata)

il = 2**15
ir = il + 2**7

mark = 'o'

plottype = plt.scatter

plottype(t[il:ir], tablel[il:ir], marker=mark, s=2, c='blue', label='Ceil values')
plottype(t[il:ir], tabler[il:ir], marker=mark, s=2, c='red', label='Floor values')
plottype(t[il:ir], tablelerp[il:ir], marker=mark, s=6, c='green', label='Lerp values')

plt.title('Table interpolation')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid()

plt.legend()
savefile = f'{WORKDIR}/img/table-interpolation.png'
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()

