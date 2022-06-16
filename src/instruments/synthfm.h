#ifndef SYNTHFM
#define SYNTHFM

#include <vector>
#include <string>
#include "instrument.h"
#include "envelope_adsr.h"

namespace upc {
  class SynthFM: public upc::Instrument {
    EnvelopeADSR adsr;
	float A;
    float I, N1, N2;
    float fc, phase_c, delta_phase_c;
    float fm, phase_m, delta_phase_m;
  public:
    SynthFM(const std::string &param = "");
    void command(long cmd, long note, long velocity=1); 
    const std::vector<float> & synthesize();
    bool is_active() const {return bActive;} 
  };
}

#endif
