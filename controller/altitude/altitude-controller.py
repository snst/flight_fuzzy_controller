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
print(dirname(__file__))
#sys.path.append(dirname(__file__))

fun = cdll.LoadLibrary(dirname(__file__) + "/../../build/controller/altitude/libaltitude_fuzzy_controller.so")  

TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 3333 # 51001 # This port match the ones using on other scripts

rcCMD = [0,0,1500,0]
desiredThrottle = 1500

vehicle = MultiWii(TCP_IP, TCP_PORT)


layout = [      
    [sg.Text('Alt setpoint:', font=('Helvetica', 20)),
     sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=50, key='alt_setpoint')],     
    [sg.Text('Alt current:', font=('Helvetica', 20)),
     sg.Text('123', font=('Helvetica', 20), key='alt_current')],
    [sg.Text('Alt error:', font=('Helvetica', 20), size=(10,1)),
     sg.Slider(range=(1, 200), orientation='h', size=(20, 20), default_value=119, key='alt_error_scale'),
     sg.Text('-1000.0', font=('Helvetica', 20), key='alt_error', size=(10,1))],
    [sg.Text('Alt dot:', font=('Helvetica', 20), size=(10,1)),
     sg.Slider(range=(1, 100), orientation='h', size=(20, 20), default_value=10, key='alt_error_dot_scale'),
     sg.Text('-1000.0', font=('Helvetica', 20), key='alt_error_dot', size=(10,1))],
    [sg.Text('FuzzyOut:', font=('Helvetica', 20), size=(10,1)),
     sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=23, key='power_fuzzy_scale'),
     sg.Text('-1000.0', font=('Helvetica', 20), key='power_fuzzy_out', size=(18,1))],
    [sg.Text('Throttle:', font=('Helvetica', 20), size=(10,1)),
     sg.Slider(range=(1450, 1650), orientation='h', size=(20, 20), default_value=1562, key='hover_throttle'),
     sg.Text('-1000.0', font=('Helvetica', 20), key='desired_throttle')]
]

window = sg.Window('alt controller', default_element_size=(40, 1)).Layout(layout)


current_time = 0
paused = False
start_time = int(round(time.time() * 100))
alt_current = 1
Integrator = 0
last_time = 0
alt_error_last = 0
alt_error_dot = 0
while (True):
    event, values = window.Read(timeout=10)

    try:
        current_time = time.time()
        if(last_time==0):
            last_time = current_time
        delta_time = current_time - last_time

        alt_current = vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE)
        alt_setpoint = values['alt_setpoint']
        alt_error = alt_setpoint - alt_current
        alt_error_scaled = alt_error / values['alt_error_scale']


        if delta_time > 0:
            alt_error_dot = (alt_error - alt_error_last) / last_time * 1000000000.0
        alt_error_last = alt_error
        alt_error_dot_scaled = alt_error_dot / values['alt_error_dot_scale']

        window.FindElement('alt_current').Update('{:03.0f}'.format(alt_current))
        window.FindElement('alt_error').Update('{:03.0f} / {:1.3f}'.format(alt_error, alt_error_scaled));
        window.FindElement('alt_error_dot').Update('{:03.2f} / {:1.3f}'.format(alt_error_dot, alt_error_dot_scaled));
        #print(alt_error_dot)

        error_fuzzy_in = float(alt_error_scaled)
        error_dot_fuzzy_in = float(alt_error_dot_scaled)

        power_fuzzy_out = fun.alt_ctrl(c_double(error_fuzzy_in), c_double(error_dot_fuzzy_in)) / -1000.0
        
        
        power_fuzzy_out_scaled = power_fuzzy_out * values['power_fuzzy_scale'] / 100.0
        throttle_correct = 200 * power_fuzzy_out_scaled

        window.FindElement('power_fuzzy_out').Update('{:1.3f} / {:1.3f} / {:03.0f}'.format(power_fuzzy_out, power_fuzzy_out_scaled, throttle_correct));

        desiredThrottle = values['hover_throttle'] + (throttle_correct)
        desiredThrottle = limit(desiredThrottle, 1000, 2000)
        window.FindElement('desired_throttle').Update('{:04.0f}'.format(desiredThrottle))

        rcCMD[2] = int(limit(desiredThrottle,1000,2000))
        vehicle.sendCMD(8,MultiWii.SET_RAW_RC,rcCMD)

    except Exception as error:
        pass


    if event is None or event == 'Exit':
        break
    #print(event, values)
    #print(values['alt'])
window.Close()