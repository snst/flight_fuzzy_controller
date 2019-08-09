#!/usr/bin/env python

import PySimpleGUI as sg
import time, datetime, csv, threading, sys
from math import *
from os.path import dirname
sys.path.append(dirname(__file__) + '/../..')
from modules.utils import *
from modules.utils2 import *
from modules.pyMultiwii import MultiWii
from FuzzyController import *
from FuzzyControllerGUI import *
from PlannerGUI import *

#import FuzzyControllerGUI as aa
#print(dirname(__file__))
#sys.path.append(dirname(__file__))


TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 3333 # 51001 # This port match the ones using on other scripts

LAT = 49.486962
LON = 11.124982

PD = 0.00005


class FlightController:
    def __init__(self):
        self.alt_gui = FuzzyControllerGUI('altitude', 1565)
        self.roll_gui = FuzzyControllerGUI('roll', 1500)
        self.pitch_gui = FuzzyControllerGUI('pitch', 1500)
        self.alt_ctrl = FuzzyController()
        self.roll_ctrl = FuzzyController()
        self.pitch_ctrl = FuzzyController()
        self.planner_gui = PlannerGUI(0, 100, 200, LAT-PD, LAT, LAT+PD, LON-PD, LON, LON+PD)

        self.rcCMD = [1500, # rechts
        1500, # 1600 vorwärts
        1500, # power
        1500 # gier 1600 uhrzeigersinn
        ]
        self.vehicle = MultiWii(TCP_IP, TCP_PORT)
        pass



    def run(self):

        fc.planner_gui.move(10,10)
        fc.alt_gui.move(10,210)
        fc.roll_gui.move(10,430)
        fc.pitch_gui.move(10,800)
        

        while (not fc.planner_gui.stop() and not fc.alt_gui.stop() and not fc.roll_gui.stop()  and not fc.pitch_gui.stop()):

            try:

                alt_actual = self.vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE)
                gps_actual = self.vehicle.getData(MultiWii.RAW_GPS)
                lat_actual = gps_actual['lat']
                lon_actual = gps_actual['lon']

                #alt_actual = 100
                #lat_actual = 49.486962
                #lon_actual = 11.124982

                planner = self.planner_gui.get_values()

                alt_error = planner['alt_desired'] - alt_actual
                fc.planner_gui.update_alt(alt_actual, alt_error)
                self.alt_gui.update_controller_config(self.alt_ctrl, 10000.0, 50000.0, 0.5)
                self.alt_ctrl.update(alt_error)
                self.alt_gui.update_gui(self.alt_ctrl)

                lat_error = -(planner['lat_desired'] - lat_actual)
                fc.planner_gui.update_lat(lat_actual, lat_error)
                self.roll_gui.update_controller_config(self.roll_ctrl, 0.1, 0.1, 1)
                self.roll_ctrl.update(lat_error)
                self.roll_gui.update_gui(self.roll_ctrl)

                lon_error = planner['lon_desired'] - lon_actual
                fc.planner_gui.update_lon(lon_actual, lon_error)
                self.pitch_gui.update_controller_config(self.pitch_ctrl, 0.1, 0.1, 1)
                self.pitch_ctrl.update(lon_error)
                self.pitch_gui.update_gui(self.pitch_ctrl)


                self.rcCMD[0] = limit(int(self.roll_ctrl.out_signal), 1000, 2000)
                self.rcCMD[1] = limit(int(self.pitch_ctrl.out_signal), 1000, 2000)
                self.rcCMD[2] = limit(int(self.alt_ctrl.out_signal), 1000, 2000)
                self.vehicle.sendCMD(8, MultiWii.SET_RAW_RC, self.rcCMD)
                

            except Exception as error:
                print(error)
                pass

            #print(event, values)
            #print(values['alt'])
        #window.Close()        pass


fc = FlightController()
fc.run()


