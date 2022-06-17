#!/usr/bin/env python3 -u
import re

import matplotlib.pyplot as plt
import numpy as np
from parse import parse
from scipy import signal
from scipy.fft import fft

from config import *


datafile_regex = r'^fm-\d+-\d+-\d+-data.txt$'
datafiles = [f'{WORKDIR}/work/graphs/{f}' for f in os.listdir(f'{WORKDIR}/work/graphs/') if re.match(datafile_regex, f)]

# Prep data for plotting
data = []
for f in datafiles:
    # Lets suppose 16 bit per sample
    tmp = np.loadtxt(f)
    tmp = tmp.astype(np.float32) / (2**15)

    data.append(tmp)

ndata = len(data)

il = 0
ir = int(SAMPLING_FREQ*0.6)

t = np.linspace(0, (ndata - 1)/SAMPLING_FREQ, ndata)

# Segur que hi han maneres millors, pero ho vull fer rapid
window = signal.windows.hamming(ir - il)
data_fft = [fft(np.multiply(d[il:ir], window)) for d in data]
data_fft = [10*np.log10(np.abs(d)) for d in data_fft]

f = np.linspace(0, SAMPLING_FREQ/2, len(data_fft[0]))

# Actual graphing (or is it plotting, idk) code
lwidth = 1.0

for i in range(ndata):
    _, I, N1, N2 = parse('{}fm-{}-{}-{}-data.txt', datafiles[i])
    plt.semilogx(f, data_fft[i], linewidth=lwidth, alpha=0.4, label=f'I={I}; N1={N1}; N2={N2};')

plt.xlim(50, 300)
plt.xlabel('Frequency [Hz]')
plt.grid()

plt.title('Comparison of FM synthesis spectrums')
plt.legend(loc='lower left')

savefile = f'{WORKDIR}/img/fm-comparison.png'
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()
