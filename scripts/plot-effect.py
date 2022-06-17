#!/usr/bin/env python3 -u
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from config import *

# Some arg parsing and error checking
if len(sys.argv) < 2:
    print('[ERROR] Give the name of the desired effect as the argument')
    sys.exit(42)

effect_name = sys.argv[1]
datafile = f'{WORKDIR}/work/graphs/effect-{effect_name}-data.txt'

if not os.path.isfile(datafile):
    print(f'[ERROR] The file {datafile} does not exist')
    sys.exit(42)

# Actual graphing (or is it plotting, idk) code
data = np.loadtxt(datafile)

data_orig = data[:,0]
data_effe = data[:,1]

ndata = len(data_orig)
t = np.linspace(0, (ndata - 1)/SAMPLING_FREQ, ndata)

il = 0
ir = int(SAMPLING_FREQ*0.6)
lwidth = 1.0

fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle(f'Effect: {effect_name}')

ax1.plot(t[il:ir], data_orig[il:ir], linewidth=lwidth, c='blue', label='Original')
ax1.set_ylim(-1, 1)
ax1.set_ylabel('Original')
ax1.grid()

ax2.plot(t[il:ir], data_effe[il:ir], linewidth=lwidth, c='green', label=effect_name)
ax2.set_ylim(-1, 1)
ax2.set_xlabel('Time [s]')
ax2.set_ylabel(effect_name)
ax2.grid()

plt.savefig(f'{WORKDIR}/img/effect-{effect_name}.png', dpi=200)
plt.show()
