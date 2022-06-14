#ifndef FICTABLA
#define FICTABLA

#include <vector>
#include <string>
#include "instrument.h"
#include "envelope_adsr.h"

namespace upc {
  class FicTabla: public upc::Instrument {
    EnvelopeADSR adsr;
    float index;
    float delta_idx;
	float A;
    int N;
    std::vector<float> tbl;
  public:
    FicTabla(const std::string &param = "");
    void command(long cmd, long note, long velocity=1); 
    const std::vector<float> & synthesize();
    bool is_active() const {return bActive;} 
  };
}

#endif
