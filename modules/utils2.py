#!/usr/bin/env python

import time
from math import cos,sin,pi,radians,degrees,sqrt

class PID2:
    def __init__(self, P, I, D, Integrator_max=200.0):

        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Integrator=0
        self.Integrator_max=Integrator_max
        self.last_time = 0
        self.last_error = 0

    def update(self, error):

        current_time = time.time()
        if(self.last_time==0):
            self.last_time = current_time

        delta_time = current_time - self.last_time
        delta_error = error - self.last_error

        # Proportional term
        self.P_value = self.Kp * error

        # Integral term
        self.Integrator = self.Integrator + error * delta_time

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < -self.Integrator_max:
            self.Integrator = -self.Integrator_max

        self.I_value = self.Integrator * self.Ki


        # Derivative term
        if(delta_time>0):
            self.D_value = self.Kd * (delta_error / delta_time )
        else:
            self.D_value = 0

        self.last_time = current_time
        self.last_error = error

        PID = self.P_value + self.I_value + self.D_value
        return PID

    def setKp(self,P):
        self.Kp=P

    def setKi(self,I):
        self.Ki=I

    def setKd(self,D):
        self.Kd=D

  
  