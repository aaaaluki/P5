#!/usr/bin/env python3 -u
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnchoredText
from parse import parse
from scipy import signal
from scipy.fft import fft

from config import *


# Show peaks
PEAK_ESTIMATION = True

# Number of peaks to find
N_PEAKS = 3

# Plot where the peaks are found
PEAKS_PLOT = 0

# Left and right frequencies for the plot
F_LEFT = 100
F_RIGHT = 400


datafile_regex = r'^fm-\d+-\d+-\d+-data.txt$'
datafiles = [f'{WORKDIR}/work/graphs/{f}' for f in os.listdir(f'{WORKDIR}/work/graphs/') if re.match(datafile_regex, f)]

# Prep data for plotting
data = []
for f in datafiles:
    # Lets suppose 16 bit per sample
    tmp = np.loadtxt(f)
    tmp = tmp.astype(np.float32) / SIGNAL_SCALING

    data.append(tmp)

ndata = len(data)

il = 0
ir = int(SAMPLING_FREQ*0.6)

t = np.linspace(0, (ndata - 1)/SAMPLING_FREQ, ndata)

# Next power of two as NFFT
nfft = 2**(ir - il - 1).bit_length()

# Window for the signal
window = signal.windows.kaiser(ir - il, 16)
# window = np.ones(ir-il)
# window = signal.windows.hamming(ir-il)

# Compute FFT
data_fft = [fft(np.multiply(d[il:ir], window), n=nfft) for d in data]
data_fft = [10*np.log10(np.abs(d)) for d in data_fft]
f = np.linspace(0, SAMPLING_FREQ, nfft)

# Find indices corresponding to F_LEFT and F_RIGHT
il = np.argmin(np.abs(f - F_LEFT))
ir = np.argmin(np.abs(f - F_RIGHT))

# Actual graphing (or is it plotting, idk) code
lwidth = 1.0

fig, ax = plt.subplots()
plot_type = ax.plot
for i in range(ndata):
    _, I, N1, N2 = parse('{}fm-{}-{}-{}-data.txt', datafiles[i])
    plot_type(f, data_fft[i], linewidth=lwidth, alpha=0.4, label=f'I={I}; N1={N1}; N2={N2};')

    # Find peaks of the specified plot
    if PEAK_ESTIMATION and i == PEAKS_PLOT:
        # Make mask array for the desired search area
        scale = 1.5*np.max(np.abs(data_fft))
        bound = np.arange(nfft)
        bound = scale*(2*(bound >= il)*(bound <= ir) - 1) 

        # Find the first N_PEAKS with max value
        peaks, props = signal.find_peaks(data_fft[i], height=(None, bound))

        # Sort peaks by peak value
        peak_val = [x for x in zip(peaks, data_fft[i][peaks])]
        peak_val.sort(key=lambda x: x[1], reverse=True)
        peak_val = peak_val[:N_PEAKS]

        peaks, val = zip(*peak_val)
        peaks = np.array(peaks)

        # Calculate estimations
        fc = SAMPLING_FREQ * peaks[0] / nfft
        fl = SAMPLING_FREQ * peaks[1] / nfft
        fr = SAMPLING_FREQ * peaks[2] / nfft
        fm = 0.5*np.abs(fl - fr)

        if fc > fm:
            N1_est = fc / fm
            N2_est = 1

        else:
            N1_est = 1
            N2_est = fm / fc

        box_text = '\n'.join([f'fc = {fc:.2f} Hz',
                              f'fm = {fm:.2f} Hz',
                              f'N1 = {N1_est:.1f}',
                              f'N2 = {N2_est:.1f}'])
        print(box_text)

        plot_type(f[peaks], data_fft[i][peaks], 'x', c='red', alpha=0.8, label=f'I={I}; N1={N1}; N2={N2};')

        # Add text box with estimations
        text_box = AnchoredText(box_text, frameon=True, loc=4, pad=0.5)
        plt.gca().add_artist(text_box)

ax.set_xlim(F_LEFT, F_RIGHT)
ax.set_ylim(-120, 0)
ax.set_xlabel('Frequency [Hz]')
ax.grid()

ax.set_title('Comparison of FM synthesis spectrums')
ax.legend(loc='lower left')

savefile = f'{WORKDIR}/img/fm-comparison.png'
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()
