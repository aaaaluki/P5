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
    N1 = 8.0f; //default value
  }
  if (N1 == 0.0f) {
    // Divide by zero blah blah
    // Using == for floats is not *technically* correct BUT who cares :*) <happy clown noises>
    N1 = 0.01f;
  }

  if (!kv.to_float("N2", N2)) {
    N2 = 4.0f; //default value
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
    phase_c = 0.0f;
    delta_phase_c = 2 * M_PI * (fc / SamplingRate);

    // MoDuLaTiOn StUfF
    fm = (fc*N2) / N1;
    phase_m = 0.0f;
    delta_phase_m = 2 * M_PI * (fm / SamplingRate);

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

  for (unsigned int i = 0; i < x.size(); ++i, phase_c += delta_phase_c, phase_m += delta_phase_m) {
    // TODO: take the phase of the outter sin and use it as an index for a LUT (interpolation needed)
    // Probably could do the same for the inner sin, idk

    // This is a "temporary" POC
    x[i] = A*sin(phase_c + I*sin(phase_m));

    // "Clamp" phases between -PI and PI
    while (phase_c > M_PI) { phase_c -= 2*M_PI;}
    while (phase_m > M_PI) { phase_m -= 2*M_PI;}
  }

  //apply envelope to x and update internal status of ADSR
  adsr(x);

  return x;
}
