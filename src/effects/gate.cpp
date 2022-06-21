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

  if (!kv.to_float("threshold", threshold)) {
    threshold = 0.5f; //default value
  }
  if (threshold == 0.0f) {
    threshold = 0.001f;
  }
  
  if (!kv.to_float("A", A)) {
    A = 1.0f; //default value
  }
}

void Gate::command(unsigned int comm) {
  if (comm == 0) {
    threshold = 0.0f;
  }
}

void Gate::operator()(std::vector<float> &x){
  for (unsigned int i = 0; i < x.size(); i++) {
    // Uncomment to get data for plotting
    //printf("%.5f\t", x[i]);

    // First hard clip
    if (abs(x[i]) < threshold) {
      x[i] = 0.0f;

    }

    x[i] *= A;

    //printf("%.5f\n", x[i]);
  }
}
