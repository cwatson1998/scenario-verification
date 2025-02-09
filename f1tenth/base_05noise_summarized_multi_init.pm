dtmc
const TIME_LIMIT=30;
const int LIDAR_RANGE = 5;
const int HALL_WIDTH = 5;
const int HALL_LENGTH = 20;
const int INIT_SCENARIO = 0;
const int INIT_CAR_DIST_S = 0;
const int INIT_CAR_DIST_F = 15;
const int INIT_CAR_HEADING = 0;

init (err=0) & (-2 <= car_dist_s) & (car_dist_s <= 2) endinit

module dynamics
    err: [0..1];
    scenario: [0..2]; // 0 is left, 1 is right, 2 is straight.
    car_dist_s: [-8..8]; // This is x_distance.  0 is middle
    car_heading: [0..7]; // Measured in radians, where 0 is forward (decreasing dist_f)


 
    // pc: 0 perception (and bookkeeping for crashing.)
    // pc: 1 controller
    // pc: 2 dynamics 1 (heading)
    // pc: 3 dynamics 2 (movement)
    // Important! At the step between TIME_LIMIT-1 and TIME_LIMIT, we ignore control
    // and just do the bookkeeping to get ready for the next scenario.

 
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 0) ->  0.263: true + 0.028: (car_heading' = 1) + 0.389: (car_dist_s' = -1) + 0.003: (car_dist_s' = -1) & (car_heading' = 1) + 0.04: (car_dist_s' = 0) + 0.005: (car_dist_s' = 0) & (car_heading' = 1) + 0.037: (car_dist_s' = 1) + 0.235: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 1) ->  0.206: (car_heading' = 0) + 0.022: true + 0.305: (car_dist_s' = -1) & (car_heading' = 0) + 0.002: (car_dist_s' = -1) + 0.032: (car_dist_s' = 0) & (car_heading' = 0) + 0.004: (car_dist_s' = 0) + 0.029: (car_dist_s' = 1) & (car_heading' = 0) + 0.3999999999999999: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 2) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 6) ->  0.091: (car_heading' = 0) + 0.029: (car_heading' = 1) + 0.393: (car_dist_s' = -1) & (car_heading' = 0) + 0.015: (car_dist_s' = -1) & (car_heading' = 1) + 0.193: (car_dist_s' = 0) & (car_heading' = 0) + 0.001: (car_dist_s' = 1) & (car_heading' = 0) + 0.278: (err'=1);
    [] (scenario = 0) & (car_dist_s = -2) & (car_heading = 7) ->  0.283: (car_heading' = 0) + 0.028: (car_heading' = 1) + 0.383: (car_dist_s' = -1) & (car_heading' = 0) + 0.002: (car_dist_s' = -1) & (car_heading' = 1) + 0.032: (car_dist_s' = 0) & (car_heading' = 0) + 0.004: (car_dist_s' = 0) & (car_heading' = 1) + 0.03: (car_dist_s' = 1) & (car_heading' = 0) + 0.238: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 0) ->  0.12: (car_dist_s' = -2) + 0.038: (car_dist_s' = -2) & (car_heading' = 1) + 0.5180000000000001: true + 0.023: (car_heading' = 1) + 0.286: (car_dist_s' = 0) + 0.002: (car_dist_s' = 1) + 0.013: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 1) ->  0.12: (car_dist_s' = -2) & (car_heading' = 0) + 0.038: (car_dist_s' = -2) + 0.5180000000000001: (car_heading' = 0) + 0.023: true + 0.286: (car_dist_s' = 0) & (car_heading' = 0) + 0.002: (car_dist_s' = 1) & (car_heading' = 0) + 0.013: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 2) ->  0.208: (car_dist_s' = -2) & (car_heading' = 0) + 0.022: (car_dist_s' = -2) & (car_heading' = 1) + 0.307: (car_heading' = 0) + 0.002: (car_heading' = 1) + 0.032: (car_dist_s' = 0) & (car_heading' = 0) + 0.004: (car_dist_s' = 0) & (car_heading' = 1) + 0.029: (car_dist_s' = 1) & (car_heading' = 0) + 0.3959999999999999: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 6) ->  0.364: (car_dist_s' = -2) & (car_heading' = 0) + 0.026: (car_dist_s' = -2) & (car_heading' = 1) + 0.356: (car_heading' = 0) + 0.254: (err'=1);
    [] (scenario = 0) & (car_dist_s = -1) & (car_heading = 7) ->  0.116: (car_dist_s' = -2) & (car_heading' = 0) + 0.037: (car_dist_s' = -2) & (car_heading' = 1) + 0.5020000000000001: (car_heading' = 0) + 0.02: (car_heading' = 1) + 0.251: (car_dist_s' = 0) & (car_heading' = 0) + 0.002: (car_dist_s' = 1) & (car_heading' = 0) + 0.072: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 0) ->  0.482: (car_dist_s' = -2) + 0.034: (car_dist_s' = -2) & (car_heading' = 1) + 0.472: (car_dist_s' = -1) + 0.012: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 1) ->  0.482: (car_dist_s' = -2) & (car_heading' = 0) + 0.034: (car_dist_s' = -2) + 0.472: (car_dist_s' = -1) & (car_heading' = 0) + 0.012: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 2) ->  0.12: (car_dist_s' = -2) & (car_heading' = 0) + 0.038: (car_dist_s' = -2) & (car_heading' = 1) + 0.5180000000000001: (car_dist_s' = -1) & (car_heading' = 0) + 0.023: (car_dist_s' = -1) & (car_heading' = 1) + 0.286: (car_heading' = 0) + 0.002: (car_dist_s' = 1) & (car_heading' = 0) + 0.013: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 3) ->  0.19: (car_dist_s' = -2) & (car_heading' = 0) + 0.02: (car_dist_s' = -2) & (car_heading' = 1) + 0.28: (car_dist_s' = -1) & (car_heading' = 0) + 0.002: (car_dist_s' = -1) & (car_heading' = 1) + 0.029: (car_heading' = 0) + 0.003: (car_heading' = 1) + 0.026: (car_dist_s' = 1) & (car_heading' = 0) + 0.45: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 6) ->  0.09: (car_dist_s' = -2) & (car_heading' = 0) + 0.028: (car_dist_s' = -2) & (car_heading' = 1) + 0.39: (car_dist_s' = -1) & (car_heading' = 0) + 0.004: (car_heading' = 0) + 0.488: (err'=1);
    [] (scenario = 0) & (car_dist_s = 0) & (car_heading = 7) ->  0.482: (car_dist_s' = -2) & (car_heading' = 0) + 0.034: (car_dist_s' = -2) & (car_heading' = 1) + 0.472: (car_dist_s' = -1) & (car_heading' = 0) + 0.012: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 0) ->  0.098: (car_dist_s' = -2) + 0.031: (car_dist_s' = -2) & (car_heading' = 1) + 0.424: (car_dist_s' = -1) + 0.003: (car_dist_s' = 0) + 0.4439999999999999: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 1) ->  0.473: (car_dist_s' = -2) & (car_heading' = 0) + 0.034: (car_dist_s' = -2) + 0.472: (car_dist_s' = -1) & (car_heading' = 0) + 0.021: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 2) ->  0.437: (car_dist_s' = -2) & (car_heading' = 0) + 0.035: (car_dist_s' = -2) & (car_heading' = 1) + 0.47699999999999987: (car_dist_s' = -1) & (car_heading' = 0) + 0.003: (car_dist_s' = -1) & (car_heading' = 1) + 0.036: (car_dist_s' = 0) & (car_heading' = 0) + 0.012: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 3) ->  0.12: (car_dist_s' = -2) & (car_heading' = 0) + 0.038: (car_dist_s' = -2) & (car_heading' = 1) + 0.5180000000000001: (car_dist_s' = -1) & (car_heading' = 0) + 0.023: (car_dist_s' = -1) & (car_heading' = 1) + 0.286: (car_dist_s' = 0) & (car_heading' = 0) + 0.002: (car_heading' = 0) + 0.013: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 6) ->  0.055: (car_dist_s' = -2) & (car_heading' = 0) + 0.017: (car_dist_s' = -2) & (car_heading' = 1) + 0.24: (car_dist_s' = -1) & (car_heading' = 0) + 0.688: (err'=1);
    [] (scenario = 0) & (car_dist_s = 1) & (car_heading = 7) ->  0.107: (car_dist_s' = -2) & (car_heading' = 0) + 0.034: (car_dist_s' = -2) & (car_heading' = 1) + 0.464: (car_dist_s' = -1) & (car_heading' = 0) + 0.004: (car_dist_s' = 0) & (car_heading' = 0) + 0.391: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 0) ->  0.044: (car_dist_s' = -2) + 0.014: (car_dist_s' = -2) & (car_heading' = 1) + 0.191: (car_dist_s' = -1) + 0.751: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 1) ->  0.416: (car_dist_s' = -2) & (car_heading' = 0) + 0.032: (car_dist_s' = -2) + 0.443: (car_dist_s' = -1) & (car_heading' = 0) + 0.109: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 2) ->  0.467: (car_dist_s' = -2) & (car_heading' = 0) + 0.035: (car_dist_s' = -2) & (car_heading' = 1) + 0.473: (car_dist_s' = -1) & (car_heading' = 0) + 0.025: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 3) ->  0.389: (car_dist_s' = -2) & (car_heading' = 0) + 0.031: (car_dist_s' = -2) & (car_heading' = 1) + 0.4239999999999999: (car_dist_s' = -1) & (car_heading' = 0) + 0.003: (car_dist_s' = -1) & (car_heading' = 1) + 0.032: (car_dist_s' = 0) & (car_heading' = 0) + 0.121: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 6) ->  1.0: (err'=1);
    [] (scenario = 0) & (car_dist_s = 2) & (car_heading = 7) ->  0.051: (car_dist_s' = -2) & (car_heading' = 0) + 0.016: (car_dist_s' = -2) & (car_heading' = 1) + 0.219: (car_dist_s' = -1) & (car_heading' = 0) + 0.714: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 0) ->  0.049: (car_dist_s' = 0) + 0.95: (car_dist_s' = 1) + 0.001: (car_dist_s' = 1) & (car_heading' = 7);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 1) ->  0.029: (car_dist_s' = 0) & (car_heading' = 0) + 0.571: (car_dist_s' = 1) & (car_heading' = 0) + 0.4: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 2) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 5) ->  0.076: (car_dist_s' = 1) & (car_heading' = 0) + 0.003: (car_dist_s' = 1) & (car_heading' = 1) + 0.019: (car_dist_s' = 2) & (car_heading' = 0) + 0.902: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 6) ->  0.7290000000000001: (car_dist_s' = 1) & (car_heading' = 0) + 0.013: (car_dist_s' = 1) & (car_heading' = 1) + 0.085: (car_dist_s' = 2) & (car_heading' = 0) + 0.173: (err'=1);
    [] (scenario = 1) & (car_dist_s = -2) & (car_heading = 7) ->  0.049: (car_dist_s' = 0) & (car_heading' = 0) + 0.95: (car_dist_s' = 1) & (car_heading' = 0) + 0.001: (car_dist_s' = 1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 0) ->  0.862: (car_dist_s' = 1) + 0.018: (car_dist_s' = 1) & (car_heading' = 1) + 0.12: (car_dist_s' = 2);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 1) ->  0.005: (car_dist_s' = 0) & (car_heading' = 0) + 0.821: (car_dist_s' = 1) & (car_heading' = 0) + 0.014: (car_dist_s' = 1) + 0.094: (car_dist_s' = 2) & (car_heading' = 0) + 0.066: (err'=1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 2) ->  0.03: (car_dist_s' = 0) & (car_heading' = 0) + 0.574: (car_dist_s' = 1) & (car_heading' = 0) + 0.396: (err'=1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 6) ->  0.777: (car_dist_s' = 1) & (car_heading' = 0) + 0.029: (car_dist_s' = 1) & (car_heading' = 1) + 0.194: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = -1) & (car_heading = 7) ->  0.8700000000000001: (car_dist_s' = 1) & (car_heading' = 0) + 0.017: (car_dist_s' = 1) & (car_heading' = 1) + 0.113: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 0) ->  0.798: (car_dist_s' = 1) + 0.026: (car_dist_s' = 1) & (car_heading' = 1) + 0.176: (car_dist_s' = 2);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 1) ->  0.789: (car_dist_s' = 1) & (car_heading' = 0) + 0.027: (car_dist_s' = 1) + 0.184: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 2) ->  0.005: (car_heading' = 0) + 0.8340000000000001: (car_dist_s' = 1) & (car_heading' = 0) + 0.013: (car_dist_s' = 1) & (car_heading' = 1) + 0.086: (car_dist_s' = 2) & (car_heading' = 0) + 0.062: (err'=1);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 3) ->  0.03: (car_heading' = 0) + 0.574: (car_dist_s' = 1) & (car_heading' = 0) + 0.396: (err'=1);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 6) ->  0.9700000000000001: (car_dist_s' = 1) & (car_heading' = 0) + 0.004: (car_dist_s' = 1) & (car_heading' = 1) + 0.026: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 0) & (car_heading = 7) ->  0.789: (car_dist_s' = 1) & (car_heading' = 0) + 0.027: (car_dist_s' = 1) & (car_heading' = 1) + 0.184: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 0) ->  0.9700000000000001: true + 0.004: (car_heading' = 1) + 0.026: (car_dist_s' = 2);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 1) ->  0.8160000000000001: (car_heading' = 0) + 0.024: true + 0.16: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 2) ->  0.777: (car_heading' = 0) + 0.029: (car_heading' = 1) + 0.194: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 3) ->  0.005: (car_dist_s' = 0) & (car_heading' = 0) + 0.7929999999999999: (car_heading' = 0) + 0.012: (car_heading' = 1) + 0.082: (car_dist_s' = 2) & (car_heading' = 0) + 0.108: (err'=1);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 6) ->  0.032: (car_dist_s' = -1) & (car_heading' = 0) + 0.154: (car_dist_s' = 0) & (car_heading' = 0) + 0.553: (car_heading' = 0) + 0.011: (car_heading' = 1) + 0.002: (car_heading' = 7) + 0.077: (car_dist_s' = 2) & (car_heading' = 0) + 0.171: (err'=1);
    [] (scenario = 1) & (car_dist_s = 1) & (car_heading = 7) ->  0.9700000000000001: (car_heading' = 0) + 0.004: (car_heading' = 1) + 0.026: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 0) ->  0.033: (car_dist_s' = -1) + 0.16: (car_dist_s' = 0) + 0.5830000000000001: (car_dist_s' = 1) + 0.012: (car_dist_s' = 1) & (car_heading' = 1) + 0.002: (car_dist_s' = 1) & (car_heading' = 7) + 0.082: true + 0.128: (err'=1);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 1) ->  0.8: (car_dist_s' = 1) & (car_heading' = 0) + 0.026: (car_dist_s' = 1) + 0.174: (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 2) ->  0.804: (car_dist_s' = 1) & (car_heading' = 0) + 0.025: (car_dist_s' = 1) & (car_heading' = 1) + 0.171: (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 3) ->  0.777: (car_dist_s' = 1) & (car_heading' = 0) + 0.029: (car_dist_s' = 1) & (car_heading' = 1) + 0.194: (car_heading' = 0);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 6) ->  1.0: (err'=1);
    [] (scenario = 1) & (car_dist_s = 2) & (car_heading = 7) ->  0.031: (car_dist_s' = -1) & (car_heading' = 0) + 0.153: (car_dist_s' = 0) & (car_heading' = 0) + 0.555: (car_dist_s' = 1) & (car_heading' = 0) + 0.011: (car_dist_s' = 1) & (car_heading' = 1) + 0.002: (car_dist_s' = 1) + 0.077: (car_heading' = 0) + 0.171: (err'=1);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 0) ->  0.231: true + 0.743: (car_dist_s' = -1) + 0.026: (car_dist_s' = -1) & (car_heading' = 7);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 1) ->  0.251: (car_heading' = 0) + 0.721: (car_dist_s' = -1) & (car_heading' = 0) + 0.028: (car_dist_s' = -1) & (car_heading' = 7);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 2) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 5) ->  1.0: (car_dist_s' = 0) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 6) ->  0.737: (car_dist_s' = -1) & (car_heading' = 0) + 0.263: (err'=1);
    [] (scenario = 2) & (car_dist_s = -2) & (car_heading = 7) ->  0.251: (car_heading' = 0) + 0.721: (car_dist_s' = -1) & (car_heading' = 0) + 0.028: (car_dist_s' = -1);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 0) ->  1.0: true;
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 1) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 2) ->  0.275: (car_dist_s' = -2) & (car_heading' = 0) + 0.694: (car_heading' = 0) + 0.031: (car_heading' = 7);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 3) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 5) ->  1.0: (car_dist_s' = 1) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 6) ->  1.0: (car_dist_s' = 0) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = -1) & (car_heading = 7) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 0) ->  1.0: true;
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 1) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 2) ->  1.0: (car_dist_s' = -1) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 3) ->  0.275: (car_dist_s' = -2) & (car_heading' = 0) + 0.694: (car_dist_s' = -1) & (car_heading' = 0) + 0.031: (car_dist_s' = -1) & (car_heading' = 7);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 5) ->  1.0: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 6) ->  1.0: (car_dist_s' = 1) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 0) & (car_heading = 7) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 0) ->  1.0: true;
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 1) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 2) ->  1.0: (car_dist_s' = 0) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 3) ->  1.0: (car_dist_s' = -1) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 6) ->  1.0: (car_dist_s' = 2) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 1) & (car_heading = 7) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 0) ->  1.0: true;
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 1) ->  1.0: (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 2) ->  1.0: (car_dist_s' = 1) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 3) ->  1.0: (car_dist_s' = 0) & (car_heading' = 0);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 4) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 5) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 6) ->  1.0: (err'=1);
    [] (scenario = 2) & (car_dist_s = 2) & (car_heading = 7) ->  1.0: (car_heading' = 0);
    
endmodule