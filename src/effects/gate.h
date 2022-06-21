#ifndef GATE_H
#define GATE_H

#include <vector>
#include <string>
#include "effect.h"

namespace upc {
  class Gate: public upc::Effect {
    private:
	    float	A, threshold;
    public:
      Gate(const std::string &param = "");
	    void operator()(std::vector<float> &x);
	    void command(unsigned int);
  };
}

#endif
