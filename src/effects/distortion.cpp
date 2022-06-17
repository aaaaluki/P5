#include <iostream>
#include <algorithm>
#include <math.h>
#include "distortion.h"
#include "keyvalue.h"

#include <stdlib.h>

using namespace upc;
using namespace std;

static float SamplingRate = 44100;

Distortion::Distortion(const std::string &param) {
  KeyValue kv(param);

  if (!kv.to_float("threshold", threshold)) {
    threshold = 0.5f; //default value
  }
  if (threshold == 0.0f) {
    threshold = 0.001f;
  }
  
  if (!kv.to_float("A", A)) {
    A = 1; //default value
  }
  
  std::string clipping = kv("clipping");
  transform(clipping.begin(), clipping.end(), clipping.begin(), ::toupper);
  soft_clipping = (clipping == "SOFT");
}

void Distortion::command(unsigned int comm) {
  if (comm == 0) {
    threshold = 1.0f;
  }
}

void Distortion::operator()(std::vector<float> &x){
  // Nice stuff: https://www.kvraudio.com/forum/viewtopic.php?t=195315
  
  for (unsigned int i = 0; i < x.size(); i++) {
    // Uncomment to get data for plotting
    //printf("%.5f\t", x[i]);

    x[i] /= threshold;

    // First hard clip
    if (x[i] > 1.0f) {
      x[i] = 1.0f;

    } else if (x[i] < -1.0f) {
      x[i] = -1.0f;
    }

    if (soft_clipping) {
      // Smoothstep input is from 0 to 1 and output from 0 to 1, just some scaling
      x[i] = 2.0f*smoothstep(x[i]/2 + 0.5f) - 1;
    }

    x[i] *= A*threshold;

    //printf("%.5f\n", x[i]);
  }
}

float Distortion::smoothstep(float x) {
  // Sauce: https://en.wikipedia.org/wiki/Smoothstep
  return 3.0f*x*x - 2.0f*x*x*x;
}
