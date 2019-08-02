#include "generated/altitude.h"

FunctionBlock_alt_controller alt_controller;

extern "C" int alt_ctrl(double err, double err_dot)
{
    alt_controller.alt = err;
    alt_controller.alt_dot = err_dot;
    alt_controller.calc();
    return alt_controller.power * 1000;
}
