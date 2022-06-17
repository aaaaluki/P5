#include <iostream>
#include <math.h>
#include "synthfm.h"
#include "keyvalue.h"

#include <stdlib.h>


using namespace upc;
using namespace std;

SynthFM::SynthFM(const std::string &param) 
  : adsr(SamplingRate, param) {
  bActive = false;
  x.resize(BSIZE);

  KeyValue kv(param);

  if (!kv.to_float("I", I)) {
    I = 1.0f; //default value
  }
  // Yoinked from "effects/vibrato.cpp"
  // Pass I in semitones to linear I
  I = 1.0f - pow(2.0f, -I / 12.0f);

  if (!kv.to_float("N1", N1)) {
    // N1 = c
    N1 = 8.0f; //default value
  }
  if (N1 == 0.0f) {
    // Divide by zero blah blah
    // Using == for floats is not *technically* correct BUT who cares :*) <happy clown noises>
    N1 = 0.01f;
  }

  if (!kv.to_float("N2", N2)) {
    // N2 = m
    N2 = 4.0f; //default value
  }

  // Create a tbl with one period of a sinusoidal wave
  // Just using it as a LUT, frequency does not matter (the most samples the better tough)
  scaling_const = 2 * M_PI / (float)N;
  tbl.resize(N);
  phase_c = 0.0f;
  phase_m = 0.0f;
  float phase = 0, step = scaling_const;

  for (int i=0; i < N ; ++i) {
    tbl[i] = sin(phase);
    phase += step;
  }
}


void SynthFM::command(long cmd, long note, long vel) {
  if (cmd == 9) {		//'Key' pressed: attack begins
    bActive = true;
    adsr.start();

    if (vel > 127) {
        vel = 127;
    }
    A = vel / 127.0f;    
    
    // Carrier thingiys
    fc = 440 * powf(2, (note - 69.0f) / 12.0f);
    delta_phase_c = N * (fc / SamplingRate);

    // MoDuLaTiOn StUfF
    fm = (fc*N2) / N1;
    delta_phase_m = N * (fm / SamplingRate);

  } else if (cmd == 8) {	//'Key' released: sustain ends, release begins
    adsr.stop();

  } else if (cmd == 0) {	//Sound extinguished without waiting for release to end
    adsr.end();
  }
}


const vector<float> & SynthFM::synthesize() {
  if (not adsr.active()) {
    x.assign(x.size(), 0);
    bActive = false;
    return x;

  } else if (not bActive) {
    return x;
  }

  #if USE_INTERPOLATION == 1
  float frac;
  int il, ir;
  float inner_phase;
  #endif

  for (unsigned int i = 0; i < x.size(); ++i, phase_c += delta_phase_c, phase_m += delta_phase_m) {
    // "Clamp" phases between 0 and N
    // It's like the modulus operator but with floats
    while (phase_c > (float)tbl.size()) { phase_c -= (float)tbl.size(); }
    while (phase_m > (float)tbl.size()) { phase_m -= (float)tbl.size(); }

    #if USE_INTERPOLATION == 1
    // Value for inside sine
    il = (int)floor(phase_m);
    frac = phase_m - (float)il;
    ir = il == N-1 ? 0 : il + 1;
    
    // Lerp phase
    inner_phase = phase_c + (I / scaling_const) * ((1-frac)*tbl[il] + frac*tbl[ir]);
    while (inner_phase > (float)tbl.size()) { inner_phase -= (float)tbl.size(); }
    while (inner_phase < 0) { inner_phase += (float)tbl.size(); }
    // "FUN FACT": pot ser que inner_phase sigui negatiu si:
    //  - es fa servir una I molt gran,
    //  - el sinus que modula la freqüència és negatiu
    //  - phase_c es bastant petit
    //
    // Com només es comprobava per index massa grans (> N) hi havien glitchs en el audio
    // per index negatius, que posaven el senyal a 0 en alguns trams.
    //
    // Ha costat bastant trobar de que es tractava, pero ja esta :^)
    // me: chr(0x41)*41
    // 

    // Value for outter sine
    il = (int)floor(inner_phase);
    frac = inner_phase - (float)il;
    ir = il >= N-1 ? 0 : il + 1;

    // Lerp final
    x[i] = A * ((1-frac)*tbl[il] + frac*tbl[ir]);

    #else
    x[i] = A * sin(2*M_PI*phase_c/N + I*sin(2*M_PI*phase_m/N));
    #endif
  }

  //apply envelope to x and update internal status of ADSR
  adsr(x);

  return x;
}
