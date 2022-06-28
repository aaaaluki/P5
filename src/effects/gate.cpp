#include <iostream>
#include <algorithm>
#include <math.h>
#include "gate.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

static float SamplingRate = 44100.0f;
static float Scaling = 1000.0f;  // From .orc file fime to seconds

Gate::Gate(const std::string &param) {
  KeyValue kv(param);

  // Get on/off thresholds
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
  
  // Get times (in clock ticks) for attack hold and release
  // The times on the .orc file are in ms NOT second (thats why there is scaling)
  float tmp;
  if (!kv.to_float("attack", tmp)) {
    tmp = 0.0f;
  }
  attack_ticks = tmp * SamplingRate / Scaling;

  if (!kv.to_float("hold", tmp)) {
    tmp = 0.0f;
  }
  hold_ticks = tmp * SamplingRate / Scaling;

  if (!kv.to_float("release", tmp)) {
    tmp = 0.0f;
  }
  release_ticks = tmp * SamplingRate / Scaling;

  // Get the amplification
  if (!kv.to_float("A", A)) {
    A = 1.0f; //default value
  }

  state = State::OFF;
}

void Gate::command(unsigned int comm) {
  if (comm == 0) {
    state = State::NOTHING;
  }
}

void Gate::operator()(std::vector<float> &x) {
  // Sauce: https://en.wikipedia.org/wiki/Noise_gate
  for (unsigned int i = 0; i < x.size(); i++, counter++) {

    switch (state) {
    case State::ATTACK:
      x[i] *= (float)counter / attack_ticks;

      if (counter >= attack_ticks) {
        state = State::ON;
        counter = 0;
      }
      break;
    
    case State::ON:
      if (abs(x[i]) < threshold_off) {
        state = State::HOLD;
        counter = 0;
      }
      break;
    
    case State::HOLD:
      if (abs(x[i]) > threshold_on) {
        state = State::ON;
        counter = 0;

      } else if (counter >= hold_ticks) {
        state = State::RELEASE;
        counter = 0;
      }
      break;
    
    case State::RELEASE:
      x[i] *= (float)(release_ticks - counter) / release_ticks;

      if (counter >= release_ticks) {
        state = State::OFF;
        counter = 0;
      }
      break;
    
    case State::OFF:
      if (abs(x[i]) > threshold_on) {
        state = State::ATTACK;
        counter = 0;
      }

      x[i] = 0.0f;
      break;
    
    default:
      break;
    }

    x[i] *= A;
  }
}
