#ifndef GATE_H
#define GATE_H

#include <vector>
#include <string>
#include "effect.h"

namespace upc {
  class Gate: public upc::Effect {
    enum State {
      ON,
      OFF,
      ATTACK,
      HOLD,
      RELEASE
    };
    private:
	    float	A, threshold, threshold_on, threshold_off;
      State state;
    public:
      Gate(const std::string &param = "");
	    void operator()(std::vector<float> &x);
	    void command(unsigned int);
  };
}

#endif
