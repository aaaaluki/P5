#ifndef GATE_H
#define GATE_H

#include <vector>
#include <string>
#include "effect.h"

namespace upc {
  class Gate: public upc::Effect {
    const std::vector<std::string> StateName = {"ON", "ATTACK", "HOLD", "RELEASE", "OFF", "NOTHING"};
    enum State {
      ON,
      ATTACK,
      HOLD,
      RELEASE,
      OFF,
      NOTHING
    };
    private:
	    float	A, threshold_on, threshold_off;
      unsigned int attack_ticks, hold_ticks, release_ticks;
      unsigned int counter;
      State state;
    public:
      Gate(const std::string &param = "");
	    void operator()(std::vector<float> &x);
	    void command(unsigned int);
  };
}

#endif
