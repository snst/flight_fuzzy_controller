import PySimpleGUI as sg


class PlannerGUI:
    def __init__(self, alt_min, alt_def, alt_max, lat_min, lat_def, lat_max, lon_min, lon_def, lon_max):
        self.event = 1
        self.layout = [      
            [sg.Text('Altitude:', font=('Helvetica', 20), size=(7,1)),
            sg.Slider(range=(alt_min, alt_max), orientation='h', size=(20, 20), default_value=alt_def, resolution=1, key='alt_desired'),     
            sg.Text('-100.0', font=('Helvetica', 20), key='alt_actual', size=(10,1)),
            sg.Text('-100.0', font=('Helvetica', 20), key='alt_error', size=(10,1))],
            [sg.Text('Lat:', font=('Helvetica', 20), size=(7,1)),
            sg.Slider(range=(lat_min, lat_max), orientation='h', size=(20, 20), default_value=lat_def, resolution=0.000001, key='lat_desired'),     
            sg.Text('-100.0', font=('Helvetica', 20), key='lat_actual', size=(10,1)),
            sg.Text('-100.0', font=('Helvetica', 20), key='lat_error', size=(10,1))],
            [sg.Text('Lon:', font=('Helvetica', 20), size=(7,1)),
            sg.Slider(range=(lon_min, lon_max), orientation='h', size=(20, 20), default_value=lon_def, resolution=0.000001, key='lon_desired'),     
            sg.Text('-100.0', font=('Helvetica', 20), key='lon_actual', size=(10,1)),
            sg.Text('-100.0', font=('Helvetica', 20), key='lon_error', size=(10,1))]
        ]

        self.window = sg.Window('Planner', default_element_size=(40, 1)).Layout(self.layout)
        pass

    def get_values(self):
        self.event, values = self.window.Read(timeout=10)
        return values

    def stop(self):
        return self.event is None or self.event == 'Exit'

    def update_alt(self, actual, error):
        self.window.FindElement('alt_actual').Update('{:04.0f}'.format(actual))        
        self.window.FindElement('alt_error').Update('{:04.0f}'.format(error))        

    def update_lat(self, actual, error):
        self.window.FindElement('lat_actual').Update('{:f}'.format(actual))        
        self.window.FindElement('lat_error').Update('{:f}'.format(error))        
    
    def update_lon(self, actual, error):
        self.window.FindElement('lon_actual').Update('{:f}'.format(actual))        
        self.window.FindElement('lon_error').Update('{:f}'.format(error))        
    
    def move(self, x, y):
        self.window.Read(timeout=10)
        self.window.Move(x,y)
