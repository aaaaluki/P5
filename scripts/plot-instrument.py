#!/usr/bin/env python3 -u
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.fft import fft

from config import *


# Some arg parsing and error checking
if len(sys.argv) < 2:
    print('[ERROR] Give the name of the desired instrument as the argument')
    sys.exit(42)

instrument = sys.argv[1]
datafile = f'{WORKDIR}/work/doremi/{instrument}.wav'

if not os.path.isfile(datafile):
    print(f'[ERROR] The file {datafile} does not exist')
    sys.exit(42)

# Prep data for plotting
sampling_freq, data = wavfile.read(datafile)

# Lets suppose 16 bit per sample
data = data.astype(np.float32) / (2**15)

ndata = len(data)

il = 0
ir = int(sampling_freq*0.6)

t = np.linspace(0, (ndata - 1)/sampling_freq, ndata)

window = signal.windows.hamming(ir - il)
data_fft = fft(np.multiply(data[il:ir], window))
data_fft = 10*np.log10(np.abs(data_fft))

f = np.linspace(0, sampling_freq/2, len(data_fft))

# Actual graphing (or is it plotting, idk) code
lwidth = 1.0

fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle(f'Instrument: {instrument}')

ax1.plot(t[il:ir], data[il:ir], linewidth=lwidth)
ax1.set_xlim(il/sampling_freq, ir/sampling_freq)
ax1.set_xlabel('Time [s]')
ax1.grid()

ax2.semilogx(f, data_fft, linewidth=lwidth)
ax2.set_xlim(10, sampling_freq/2)
ax2.set_xlabel('Frequency [Hz]')
ax2.grid()

savefile = f'{WORKDIR}/img/instrument-{instrument}.png'
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()
