import time, sys
from ctypes import * 
from os.path import dirname
sys.path.append(dirname(__file__) + '/../..')

fuzzy_alt_controller = cdll.LoadLibrary(dirname(__file__) + "/../../build/controller/altitude/libaltitude_fuzzy_controller.so")  


class FuzzyController:
    def __init__(self):
        self.error_scaled = 0
        self.error_scale = 1
        self.error_last = 0
        self.error_dot = 0
        self.error_dot_scale = 1
        self.error_dot_scaled = 0
        self.out_scale = 1
        self.out = 0
        self.out_scaled = 0
        self.last_time = 0
        self.out_base = 0
        self.out_signal = 0
        pass

    def update(self, error):
        self.error_scaled = error * self.error_scale

        now = time.time()
        if(self.last_time==0):
            self.last_time = now
        delta_time = now - self.last_time
        self.last_time = now

        if delta_time > 0:
            self.error_dot = (error - self.error_last) / delta_time

        self.error_last = error
        self.error_dot_scaled = self.error_dot * self.error_dot_scale
        self.out = fuzzy_alt_controller.alt_ctrl(c_double(self.error_scaled), c_double(self.error_dot_scaled)) / -1000.0
        self.out_scaled =  self.out * self.out_scale
        self.out_signal = self.out_base + self.out_scaled

        return self.out_scaled