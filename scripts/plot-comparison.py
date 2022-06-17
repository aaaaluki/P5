#!/usr/bin/env python3 -u
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

from config import *

# Some arg parsing and error checking
if len(sys.argv) < 3:
    print('[ERROR] Give the 2 names of the desired files to compare as the argument')
    sys.exit(42)

fname1 = sys.argv[1]
fname2 = sys.argv[2]

if not os.path.isfile(fname1):
    print(f'[ERROR] The file {fname1} does not exist')
    sys.exit(42)

if not os.path.isfile(fname2):
    print(f'[ERROR] The file {fname2} does not exist')
    sys.exit(42)

# Actual graphing (or is it plotting, idk) code
fm1, data1 = wavfile.read(fname1)
fm2, data2 = wavfile.read(fname2)

data1 = data1 / 2**14
data2 = data2 / 2**14

fname1 = Path(fname1).stem
fname2 = Path(fname2).stem

t1 = np.linspace(0, (len(data1) - 1)/fm1, len(data1))
t2 = np.linspace(0, (len(data2) - 1)/fm2, len(data2))

t0l = 0
t0r = 0.6

il1 = int(fm1*t0l)
ir1 = int(fm1*t0r)
il2 = int(fm2*t0l)
ir2 = int(fm2*t0r)

lwidth = 1.0

fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle(f'{fname1} vs {fname2}')

ax1.plot(t1[il1:ir1], data1[il1:ir1], linewidth=lwidth, c='blue', label=fname1)
ax1.set_xlim(t0l, t0r)
ax1.set_ylim(-1, 1)
ax1.set_ylabel(fname1)
ax1.grid()

ax2.plot(t2[il2:ir2], data2[il2:ir2], linewidth=lwidth, c='green', label=fname2)
ax2.set_xlim(t0l, t0r)
ax2.set_ylim(-1, 1)
ax2.set_xlabel('Time [s]')
ax2.set_ylabel(fname2)
ax2.grid()

savefile = f'{WORKDIR}/img/compare-{fname1}-vs-{fname2}.png'
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()
