#include <iostream>
#include <math.h>
#include "seno.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

Seno::Seno(const std::string &param) 
  : adsr(SamplingRate, param) {
  bActive = false;
  x.resize(BSIZE);

  KeyValue kv(param);

  if (!kv.to_int("N", N)) {
    N = 40; //default value
  }

  //Create a tbl with one period of a sinusoidal wave
  tbl.resize(N);
  float phase = 0, step = 2 * M_PI /(float) N;
  index = 0.0f;

  for (int i=0; i < N ; ++i) {
    tbl[i] = sin(phase);
    phase += step;
  }
}


void Seno::command(long cmd, long note, long vel) {
  if (cmd == 9) {		//'Key' pressed: attack begins
    bActive = true;
    adsr.start();
    index = 0;

    if (vel > 127) {
        vel = 127;
    }
    A = vel / 127.0f;

    // Calculate delta for the table index
    float f0_note = 440 * powf(2, (note - 69.0f) / 12.0f);
    delta_idx = (float)N * f0_note / SamplingRate;
    
  } else if (cmd == 8) {	//'Key' released: sustain ends, release begins
    adsr.stop();

  } else if (cmd == 0) {	//Sound extinguished without waiting for release to end
    adsr.end();
  }
}


const vector<float> & Seno::synthesize() {
  if (not adsr.active()) {
    x.assign(x.size(), 0);
    bActive = false;
    return x;

  } else if (not bActive) {
    return x;
  }

  float frac;
  int il, ir;

  for (unsigned int i = 0; i < x.size(); ++i, index += delta_idx) {
    // It's like the modulus operator but with floats
    while (index > (float)tbl.size()) { index -= (float)tbl.size();}

    // Get base and fraction indices
    il = (int)floor(index);
    frac = index - (float)il;
    ir = il == N-1 ? 0 : il + 1;

    // Lerp
    x[i] = A * ((1-frac)*tbl[il] + frac*tbl[ir]);

    // Uncomment to get data to plot
    // printf("%.10f\t%.10f\t%.10f\n", tbl[il], tbl[ir], ((1-frac)*tbl[il] + frac*tbl[ir]));
  }

  //apply envelope to x and update internal status of ADSR
  adsr(x);

  return x;
}
