#include <iostream>
#include <algorithm>
#include <math.h>
#include "gate.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

static float SamplingRate = 44100;

Gate::Gate(const std::string &param) {
  KeyValue kv(param);

  if (!kv.to_float("threshold_on", threshold_on)) {
    threshold_on = 0.5f; //default value
  }
  if (threshold_on == 0.0f) {
    threshold_on = 0.001f;
  }
  
  if (!kv.to_float("threshold_off", threshold_off)) {
    threshold_off = threshold_on; // default value, no hysteresis
  }
  if (threshold_off == 0.0f) {
    threshold_off = 0.001f;
  }
  
  if (!kv.to_float("A", A)) {
    A = 1.0f; //default value
  }

  threshold = threshold_off;
  state = State::OFF;
}

void Gate::command(unsigned int comm) {
  if (comm == 0) {
    threshold = threshold_off;
    state = State::OFF;
  }
}

void Gate::operator()(std::vector<float> &x){
  // Sauce: https://en.wikipedia.org/wiki/Noise_gate
  for (unsigned int i = 0; i < x.size(); i++) {
    // First hard clip
    if (abs(x[i]) < threshold) {
      state = State::OFF;
    } else {
      state = State::ON;
    }

    switch (state) {
    case State::ON:
      threshold = threshold_off;
      break;
    
    case State::OFF:
      x[i] = 0.0f;
      threshold = threshold_on;
      break;
    
    default:
      break;
    }

    x[i] *= A;
  }
}
