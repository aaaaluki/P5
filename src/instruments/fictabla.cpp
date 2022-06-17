#include <iostream>
#include <math.h>
#include "keyvalue.h"
#include "fictabla.h"
#include "wavfile_mono.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

FicTabla::FicTabla(const std::string &param) 
  : adsr(SamplingRate, param) {
  bActive = false;
  x.resize(BSIZE);

  KeyValue kv(param);

  std::string file_name;
  static string kv_null;
  if ((file_name = kv("file")) == kv_null) {
    cerr << "Error: no se ha encontrado el campo con el fichero de la señal para un instrumento FicTabla" << endl;
    throw -1;
  }
  
  unsigned int fm;
  if (readwav_mono(file_name, fm, tbl) < 0) {
    cerr << "Error: no se puede leer el fichero " << file_name << " para un instrumento FicTabla" << endl;
    throw -1;
  }

  N = tbl.size();
}


void FicTabla::command(long cmd, long note, long vel) {
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


const vector<float> & FicTabla::synthesize() {
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
