#!/usr/bin/env python3 -u
from collections import defaultdict
import os
import sys
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from config import *


PLOT_DURATION = 1.0
NOTE_DURATION = 1.0
RELEASE_TIME = 0.65
PEAK_VALUE = 0.75

A_COLOR = '#f8635c'
D_COLOR = '#f2bb3c'
S_COLOR = '#6ce9a5'
R_COLOR = '#843db7'


def t_interval(t0: float, dur: float, fs: int):
    Nsamples = int(dur*fs)
    if Nsamples == 0:
        return np.zeros(1) + t0
    else:    
        return np.linspace(0, dur*(Nsamples-1)/Nsamples, Nsamples) + t0


def f_line(p0: Tuple[float, float], p1: Tuple[float, float], t):
    # Lets supose p1.x > p0.x (p[0])

    # Sauce: https://stats.stackexchange.com/a/178629
    return (p1[1] - p0[1]) * np.linspace(0, 1, len(t)) + p0[1]


# Some arg parsing and error checking
if len(sys.argv) < 2:
    print('[ERROR] Give the name of the <adsr>.orc file to plot the waveform')
    sys.exit(42)

fname = sys.argv[1]

if not os.path.isfile(fname):
    print(f'[ERROR] The file {fname} does not exist')
    sys.exit(42)

# Parse some data (or is it data)
params = defaultdict()
config_line = ''
instrument_name = ''

with open(fname, 'r') as f:
    # Some janky parsing (hope it works)    
    for line in f.readlines():
        line = line.strip()
        if line == "" :
            continue

        if line.startswith('#'):
            instrument_name = line.strip('#').strip()
            continue

        config_line = line
        for elem in line.split(' '):
            if elem.startswith('ADSR_A'):
                params['A'] = float(elem.strip(';').split('=')[1])
            
            elif elem.startswith('ADSR_D'):
                params['D'] = float(elem.strip(';').split('=')[1])
            
            elif elem.startswith('ADSR_S'):
                params['S'] = float(elem.strip(';').split('=')[1])
            
            elif elem.startswith('ADSR_R'):
                params['R'] = float(elem.strip(';').split('=')[1])

            elif elem.startswith('N'):
                params['N'] = int(elem.strip(';').split('=')[1])
        
        break

# Lets supose that all params are set

# Do smth with ADSR data
f0 = 440 * pow(2, (params['N'] - 69) / 12)
#s_duration = max(NOTE_DURATION - params['A'] - params['D'] - params['R'], 0)
s_duration = max(RELEASE_TIME - params['A'] - params['D'], 0)
tA = t_interval(0,                                      params['A'], SAMPLING_FREQ)
tD = t_interval(params['A'],                            params['D'], SAMPLING_FREQ)
tS = t_interval(params['A'] + params['D'],              s_duration,  SAMPLING_FREQ)
tR = t_interval(params['A'] + params['D'] + s_duration, params['R'], SAMPLING_FREQ)

# Hackity hack 2 electric bogaloo
# PEAK_VALUE = min(PEAK_VALUE, params['S'])
dataA = f_line((tA[0], 0),           (tA[-1], PEAK_VALUE),  tA) * np.sin(2*np.pi*f0*tA) * (tA < NOTE_DURATION)
dataD = f_line((tD[0], PEAK_VALUE),  (tD[-1], params['S']), tD) * np.sin(2*np.pi*f0*tD) * (tD < NOTE_DURATION)
dataS = f_line((tS[0], params['S']), (tS[-1], params['S']), tS) * np.sin(2*np.pi*f0*tS) * (tS < NOTE_DURATION)
dataR = f_line((tR[0], params['S']), (tR[-1], 0),           tR) * np.sin(2*np.pi*f0*tR) * (tR < NOTE_DURATION)

# Actual graphing (or is it plotting, idk) code
lwidth = 1.0
a = 0.8

plt.plot(tA, dataA, linewidth=lwidth, c=A_COLOR, alpha=a, label='A')
plt.plot(tD, dataD, linewidth=lwidth, c=D_COLOR, alpha=a, label='D')
plt.plot(tS, dataS, linewidth=lwidth, c=S_COLOR, alpha=a, label='S')
plt.plot(tR, dataR, linewidth=lwidth, c=R_COLOR, alpha=a, label='R')

config_line = config_line.split(' ')
config_line = ' '.join([e for e in config_line if e != ''][2::])

plt.title(f'{instrument_name}\n{config_line}')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.xlim(0, PLOT_DURATION)
plt.ylim(-1, 1)
plt.grid()
plt.legend()

instrument_name = instrument_name.replace(' ', '-').lower()

#savefile = f'''{WORKDIR}/img/adsr-A{int(1e3*params['A'])}-D{int(1e3*params['D'])}-S{int(1e3*params['S'])}-R{int(1e3*params['R'])}.png'''
savefile = f'''{WORKDIR}/img/adsr-{instrument_name}.png'''
print(f'Saving plot as: {savefile}')
plt.savefig(savefile, dpi=PLOT_DPI)
plt.show()
