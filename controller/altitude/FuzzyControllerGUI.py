import PySimpleGUI as sg


class FuzzyControllerGUI:
    def __init__(self, name, out_base):
        self.event = 1
        self.layout = [      
            [sg.Text('Error:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(0, 1000), orientation='h', size=(20, 20), default_value=95, key='error_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='error', size=(15,1))],
            [sg.Text('Error dot:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(0, 1000), orientation='h', size=(20, 20), default_value=265, key='error_dot_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='error_dot', size=(15,1))],
            [sg.Text('Fuzzy out:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=23, key='fuzzy_scale'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='fuzzy_out', size=(15,1))],
            [sg.Text('Out:', font=('Helvetica', 20), size=(10,1)),
            sg.Slider(range=(1450, 1650), orientation='h', size=(20, 20), default_value=out_base, key='out_base'),
            sg.Text('-1000.0', font=('Helvetica', 20), key='out')]
        ]

        self.window = sg.Window(name, default_element_size=(40, 1)).Layout(self.layout)
        pass

    def set_error(self, error, error_scaled):
        self.window.FindElement('error').Update('{:03.0f} / {:1.3f}'.format(error, error_scaled));

    def set_error_dot(self, error_dot, error_dot_scaled):
        self.window.FindElement('error_dot').Update('{:03.2f} / {:1.3f}'.format(error_dot, error_dot_scaled));

    def set_fuzzy_out(self, fuzzy_out, fuzzy_out_scaled, out_signal):
        self.window.FindElement('fuzzy_out').Update('{:1.3f} / {:03.0f}'.format(fuzzy_out, fuzzy_out_scaled));
        self.window.FindElement('out').Update('{:4.0f}'.format(out_signal));

    def set_scaled_out(self, desiredThrottle):
        self.window.FindElement('scaled_out').Update('{:04.0f}'.format(desiredThrottle))

    def get_values(self):
        self.event, values = self.window.Read(timeout=10)
        return values

    def stop(self):
        return self.event is None or self.event == 'Exit'

    def update_controller_config(self, controller, error_div, error_dot_div, out_div):
        values = self.get_values()
        controller.error_scale = values['error_scale'] / error_div
        controller.error_dot_scale = values['error_dot_scale'] / error_dot_div
        controller.out_scale = values['fuzzy_scale'] / out_div
        controller.out_base = values['out_base']
        

    def update_gui(self, controller):
        #self.set_actual(controller.actual)
        self.set_error(controller.error_last, controller.error_scaled)
        self.set_error_dot(controller.error_dot, controller.error_dot_scaled)
        self.set_fuzzy_out(controller.out, controller.out_scaled, controller.out_signal)
        #self.set_scaled_out(throttle)

    def move(self, x, y):
        self.window.Read(timeout=10)
        self.window.Move(x,y)
