#!/usr/bin/env python

import PySimpleGUI as sg
import time, datetime, csv, threading, sys
from math import *
from ctypes import * 
from os.path import dirname
sys.path.append(dirname(__file__) + '/../..')
from modules.utils import *
from modules.utils2 import *
from modules.pyMultiwii import MultiWii
#print(dirname(__file__))
#sys.path.append(dirname(__file__))

fuzzy_alt_controller = cdll.LoadLibrary(dirname(__file__) + "/../../build/controller/altitude/libaltitude_fuzzy_controller.so")  

TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 3333 # 51001 # This port match the ones using on other scripts



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
        pass

    def update(self, desired, actual):
        error = desired - actual
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
        return self.out_scaled

class FlightControllerGUI:
    def __init__(self):
        self.event = 1
        self.layout = [      
            [sg.Text('Alt setpoint:', font=('Helvetica', 20)),
            sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=50, key='alt_setpoint')],     
            [sg.Text('Alt current:', font=('Helvetica', 20)),
            sg.Text('123', font=('Helvetica', 20), key='alt_current')],
            [sg.Text('Alt error:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(1, 1000), orientation='h', size=(20, 20), default_value=95, key='alt_error_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='alt_error', size=(10,1))],
            [sg.Text('Alt dot:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(1, 1000), orientation='h', size=(20, 20), default_value=265, key='alt_error_dot_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='alt_error_dot', size=(10,1))],
            [sg.Text('FuzzyOut:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=23, key='power_fuzzy_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='power_fuzzy_out', size=(18,1))],
            [sg.Text('Throttle:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(1450, 1650), orientation='h', size=(20, 20), default_value=1565, key='hover_throttle'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='desired_throttle')],
            [sg.Text('-1000.0:', font=('Helvetica', 20), size=(15,1), key='lat'),
            sg.Text('-1000.0', font=('Helvetica', 20), size=(15,1), key='lon')]
        ]

        self.window = sg.Window('alt controller', default_element_size=(40, 1)).Layout(self.layout)
        pass

    def set_alt_current(self, alt_current):
        self.window.FindElement('alt_current').Update('{:03.0f}'.format(alt_current))

    def set_alt_error(self, alt_error, alt_error_scaled):
        self.window.FindElement('alt_error').Update('{:03.0f} / {:1.3f}'.format(alt_error, alt_error_scaled));

    def set_alt_error_dot(self, alt_error_dot, alt_error_dot_scaled):
        self.window.FindElement('alt_error_dot').Update('{:03.2f} / {:1.3f}'.format(alt_error_dot, alt_error_dot_scaled));

    def set_gps(self, lat, lon):
        self.window.FindElement('lat').Update('{:f}'.format(lat))
        self.window.FindElement('lon').Update('{:f}'.format(lon))

    def set_power_fuzzy_out(self, power_fuzzy_out, power_fuzzy_out_scaled, throttle_correct):
        self.window.FindElement('power_fuzzy_out').Update('{:1.3f} / {:1.3f} / {:03.0f}'.format(power_fuzzy_out, power_fuzzy_out_scaled, throttle_correct));

    def set_desired_throttle(self, desiredThrottle):
        self.window.FindElement('desired_throttle').Update('{:04.0f}'.format(desiredThrottle))

    def get_values(self):
        self.event, values = self.window.Read(timeout=10)
        return values

    def stop(self):
        return self.event is None or self.event == 'Exit'


class FlightController:
    def __init__(self):
        self.gui = FlightControllerGUI()
        self.alt = FuzzyController()
        self.pitch = FuzzyController()
        self.roll = FuzzyController()
        self.rcCMD = [1500, # rechts
        1500, # 1600 vorwärts
        1500, # power
        1500 # gier 1600 uhrzeigersinn
        ]
        self.vehicle = MultiWii(TCP_IP, TCP_PORT)
        self.alt_error_last = 0
        self.desired_lat = 49.486962
        self.desired_lon = 11.124982
#        self.desired_lon = 11.125000
        pass

    def Gui(self):
        return self.gui

    def control_altitude(self, vehicle, values):
        desired = values['alt_setpoint']
        actual = vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE)
        self.alt.error_scale = values['alt_error_scale'] / 10000.0
        self.alt.error_dot_scale = values['alt_error_dot_scale'] / 50000.0
        self.alt.out_scale = values['power_fuzzy_scale'] / 100.0 * 200.0
        out = self.alt.update(desired, actual) 
        throttle = values['hover_throttle'] + out
        """fc.gui.set_alt_current(actual)
        fc.gui.set_alt_error(self.alt.error_last, self.alt.error_scaled)
        fc.gui.set_alt_error_dot(self.alt.error_dot, self.alt.error_dot_scaled)
        fc.gui.set_power_fuzzy_out(self.alt.out, self.alt.out_scaled, 0)
        fc.gui.set_desired_throttle(throttle)"""
        return int(limit(throttle,1000,2000))

    def control_pitch(self, vehicle, values):
        desired = self.desired_lon
        pos = self.vehicle.getData(MultiWii.RAW_GPS)
        actual = pos['lon']
        self.pitch.error_scale = values['alt_error_scale'] * 100.0
        self.pitch.error_dot_scale = values['alt_error_dot_scale'] * 100
        self.pitch.out_scale = values['power_fuzzy_scale'] / 100.0 * 500.0
        out = self.pitch.update(desired, actual) 
        throttle = 1500 + out
        fc.gui.set_alt_current(actual)
        fc.gui.set_alt_error(self.pitch.error_last, self.pitch.error_scaled)
        fc.gui.set_alt_error_dot(self.pitch.error_dot, self.pitch.error_dot_scaled)
        fc.gui.set_power_fuzzy_out(self.pitch.out, self.pitch.out_scaled, 0)
        fc.gui.set_desired_throttle(throttle)
        return int(limit(throttle,1000,2000)), pos        

    def control_roll(self, vehicle, values):
        desired = self.desired_lat
        pos = self.vehicle.getData(MultiWii.RAW_GPS)
        actual = pos['lat']
        self.roll.error_scale = values['alt_error_scale'] * 100.0
        self.roll.error_dot_scale = values['alt_error_dot_scale'] * 100
        self.roll.out_scale = values['power_fuzzy_scale'] / 100.0 * 500.0
        out = self.roll.update(actual, desired) 
        throttle = 1500 + out
        fc.gui.set_alt_current(actual)
        fc.gui.set_alt_error(self.roll.error_last, self.roll.error_scaled)
        fc.gui.set_alt_error_dot(self.roll.error_dot, self.roll.error_dot_scaled)
        fc.gui.set_power_fuzzy_out(self.roll.out, self.roll.out_scaled, 0)
        fc.gui.set_desired_throttle(throttle)
        return int(limit(throttle,1000,2000)), pos     

    def control_altitude2(self, vehicle, values, delta_time):
        alt_error_dot = 0
        alt_current = vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE)
        alt_setpoint = values['alt_setpoint']
        alt_error = alt_setpoint - alt_current
        alt_error_scaled = alt_error * values['alt_error_scale'] / 10000.0

        if delta_time > 0:
            alt_error_dot = (alt_error - self.alt_error_last) / delta_time #last_time * 1000000000.0

        self.alt_error_last = alt_error
        alt_error_dot_scaled =  alt_error_dot * values['alt_error_dot_scale'] / 50000.0

        error_fuzzy_in = float(alt_error_scaled)
        error_dot_fuzzy_in = float(alt_error_dot_scaled)

        power_fuzzy_out = fuzzy_alt_controller.alt_ctrl(c_double(error_fuzzy_in), c_double(error_dot_fuzzy_in)) / -1000.0
        
        power_fuzzy_out_scaled = power_fuzzy_out * values['power_fuzzy_scale'] / 100.0
        throttle_correct = 200 * power_fuzzy_out_scaled

        desiredThrottle = values['hover_throttle'] + (throttle_correct)
        desiredThrottle = limit(desiredThrottle, 1000, 2000)

        fc.gui.set_alt_current(alt_current)
        fc.gui.set_alt_error(alt_error, alt_error_scaled)
        fc.gui.set_alt_error_dot(alt_error_dot, alt_error_dot_scaled)
        fc.gui.set_power_fuzzy_out(power_fuzzy_out, power_fuzzy_out_scaled, throttle_correct)
        fc.gui.set_desired_throttle(desiredThrottle)

        self.rcCMD[2] = int(limit(desiredThrottle,1000,2000))

    def control_pos(self, vehicle, values, delta_time):
        pos = self.vehicle.getData(MultiWii.RAW_GPS)
        fc.gui.set_gps(pos['lat'], pos['lon'])

        if (pos['lon'] < self.desired_lon):
            self.rcCMD[1] = 1520
        else:
            self.rcCMD[1] = 1480

        pass

    def run(self):
        current_time = 0
        alt_current = 1
        last_time = 0
        alt_error_last = 0
        alt_error_dot = 0
        pos = 0

        while (not fc.gui.stop()):

            try:

                values = fc.gui.get_values()

                """current_time = time.time()
                if(last_time==0):
                    last_time = current_time
                delta_time = current_time - last_time
                last_time = current_time
                print(delta_time)

                fc.control_altitude(self.vehicle, values, delta_time)
                fc.control_pos(self.vehicle, values, delta_time)"""

                val, pos = self.control_pitch(self.vehicle, values)
                val2, pos2 = self.control_roll(self.vehicle, values)
                self.rcCMD[0] = val2
                self.rcCMD[1] = val
                self.rcCMD[2] = self.control_altitude(self.vehicle, values)
                self.vehicle.sendCMD(8, MultiWii.SET_RAW_RC, self.rcCMD)
                fc.gui.set_gps(pos['lat'], pos['lon'])

            except Exception as error:
                pass

            #print(event, values)
            #print(values['alt'])
        #window.Close()        pass


fc = FlightController()
fc.run()


