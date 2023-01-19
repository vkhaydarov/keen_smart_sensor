from mtppy.service import Service
from mtppy.procedure import Procedure
from mtppy.operation_elements import *
from mtppy.indicator_elements import *
import time
import requests
import base64
import numpy as np
from flask import Flask, Response
from threading import Thread
import socket


class ServiceRawDataAcquisition(Service):
    def __init__(self, tag_name, tag_description):
        super().__init__(tag_name, tag_description)
        self.planteye_endpoint = None
        self.stop_data_acquisition_flag = True
        self.web_server = None
        self.add_free_run_procedure()
        self.add_snapshot_procedure()
        self.web_server_host = '0.0.0.0'
        self.web_server_port = 5002
        self.place_holder_img = self.load_place_holder_image()
        self.frame_to_show = self.place_holder_img
        Thread(target=self.run_webserver).start()

    def load_place_holder_image(self):
        with open('res/novid.jpg', 'rb') as img_file:
            return img_file.read()

    def set_planteye_endpoint(self, planteye_endpoint):
        self.planteye_endpoint = planteye_endpoint

    def add_free_run_procedure(self):
        proc_free_run = Procedure(0, 'free_run', is_self_completing=False, is_default=True)
        proc_parameters = [
            DIntServParam('shutter_speed_setpoint', v_min=1, v_max=60000000, v_scl_min=0, v_scl_max=60000000,
                          v_unit=23),
            DIntServParam('roi_x0', v_min=1, v_max=2448, v_scl_min=0, v_scl_max=2448, v_unit=23),
            DIntServParam('roi_y0', v_min=1, v_max=2048, v_scl_min=0, v_scl_max=2048, v_unit=23),
            DIntServParam('roi_x_delta', v_min=0, v_max=2448, v_scl_min=0, v_scl_max=2448, v_unit=23),
            DIntServParam('roi_y_delta', v_min=0, v_max=2048, v_scl_min=0, v_scl_max=2048, v_unit=23),
            DIntServParam('gain_setpoint', v_min=0, v_max=48, v_scl_min=0, v_scl_max=48, v_unit=23),
            BinServParam('auto_brightness_setpoint', v_state_0='off', v_state_1='on'),
            AnaServParam('time_interval_setpoint', v_min=0, v_max=3600, v_scl_min=0, v_scl_max=3600, v_unit=23),
        ]
        [proc_free_run.add_procedure_parameter(proc_param) for proc_param in proc_parameters]

        report_values = [DIntView('shutter_speed_feedback', v_scl_min=1, v_scl_max=60000000, v_unit=23),
                         DIntView('gain_feedback', v_scl_min=0, v_scl_max=48, v_unit=23),
                         BinView('auto_brightness_feedback', v_state_0='off', v_state_1='on'),
                         StringView('webserver_endpoint'),
                         ]
        [proc_free_run.add_report_value(report_value) for report_value in report_values]

        self.add_procedure(proc_free_run)

    def add_snapshot_procedure(self):
        proc_snapshot = Procedure(1, 'snapshot', is_self_completing=True, is_default=False)
        proc_parameters = [
            DIntServParam('shutter_speed_setpoint', v_min=1, v_max=60000000, v_scl_min=0, v_scl_max=60000000,
                          v_unit=23),
            DIntServParam('roi_x0', v_min=1, v_max=2448, v_scl_min=0, v_scl_max=2448, v_unit=23),
            DIntServParam('roi_y0', v_min=1, v_max=2048, v_scl_min=0, v_scl_max=2048, v_unit=23),
            DIntServParam('roi_x_delta', v_min=0, v_max=2448, v_scl_min=0, v_scl_max=2448, v_unit=23),
            DIntServParam('roi_y_delta', v_min=0, v_max=2048, v_scl_min=0, v_scl_max=2048, v_unit=23),
            DIntServParam('gain_setpoint', v_min=0, v_max=48, v_scl_min=0, v_scl_max=48, v_unit=23),
            BinServParam('auto_brigthness_setpoint', v_state_0='off', v_state_1='on')
        ]
        [proc_snapshot.add_procedure_parameter(proc_param) for proc_param in proc_parameters]

        report_values = [DIntView('shutter_speed_feedback', v_scl_min=1, v_scl_max=60000000, v_unit=23),
                         DIntView('gain_feedback', v_scl_min=0, v_scl_max=48, v_unit=23),
                         BinView('auto_brigthness_feedback', v_state_0='off', v_state_1='on'),
                         StringView('webserver_endpoint'),
                         ]
        [proc_snapshot.add_report_value(report_value) for report_value in report_values]

        self.add_procedure(proc_snapshot)

    def run_webserver(self):
        self.web_server = Flask('Smart Camera - Webserver')
        self.web_server.add_url_rule(rule='/',
                                     endpoint='Video feed',
                                     view_func=lambda: Response(self.video_feed_gen(),
                                                                mimetype='multipart/x-mixed-replace; boundary=frame')
                                     )
        self.web_server.run(host=self.web_server_host, port=self.web_server_port)

    def video_feed_gen(self):
        while True:
            time.sleep(self.procedures[0].procedure_parameters['time_interval_setpoint'].get_v_out())
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + self.frame_to_show + b'\r\n')

    def idle(self):
        print('- Idle -')
        cycle = 0
        while self.is_state('idle'):
            print('Cycle idle %i' % cycle)
            cycle += 1
            time.sleep(1)

    def starting(self):
        print('- Starting -')
        self.apply_procedure_parameters()
        web_server = f'{self.get_endpoint()}:{self.web_server_port}'
        self.procedures[0].report_values['webserver_endpoint'].set_v(web_server)
        self.state_change()

    def get_endpoint(self):
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    def apply_procedure_parameters(self):
        procedure = self.procedure_control.procedures[self.procedure_control.get_procedure_cur()]
        for parameter in procedure.procedure_parameters.values():
            parameter.set_v_out()

    def get_frame(self):
        try:
            res = requests.get(self.planteye_endpoint+'/get_frame')
            if not res.ok:
                print('Not 200 status response from PlanyEye')
                return self.place_holder_img
        except Exception:
            print('No request response from PlanyEye')
            return self.place_holder_img

        try:
            frame_str = res.json()['camera']['data']['frame']['value']
            frame_raw = base64.b64decode(frame_str)
            frame_np = np.frombuffer(frame_raw, dtype=np.uint8)
            frame_bytes = frame_np.tobytes()
            print('PlantEye returned proper image')
            return frame_bytes
        except ConnectionError:
            print('PlantEye is unreachable')
            return self.place_holder_img
        except Exception:
            print('Cannot convert PlantEye response into image')
            return self.place_holder_img

    def execute(self):
        print('- Execute -')
        print(f'ProcedureCur is {self.procedure_control.get_procedure_cur()}')
        self.start_data_acquisition()

    def start_data_acquisition(self):
        self.stop_data_acquisition_flag = False
        self.procedures[0].report_values['webserver_endpoint'].set_v('ip-to-webserver')
        if self.procedure_control.get_procedure_cur() == 0:
            self.execute_free_run()
        elif self.procedure_control.get_procedure_cur() == 1:
            self.execute_snapshot()

    def stop_data_acquisition(self):
        self.stop_data_acquisition_flag = True
        self.procedures[0].report_values['webserver_endpoint'].set_v('')
        self.frame_to_show = self.place_holder_img

    def execute_free_run(self):
        while not self.stop_data_acquisition_flag:
            self.frame_to_show = self.get_frame()
            time.sleep(self.procedures[0].procedure_parameters['time_interval_setpoint'].get_v_out())

    def execute_snapshot(self):
        self.frame_to_show = self.get_frame()
        self.state_change()

    def completing(self):
        self.stop_data_acquisition()
        self.state_change()

    def completed(self):
        pass

    def pausing(self):
        self.stop_data_acquisition()
        self.state_change()

    def paused(self):
        pass

    def resuming(self):
        self.start_data_acquisition()
        self.state_change()

    def holding(self):
        self.stop_data_acquisition()
        self.state_change()

    def held(self):
        pass

    def unholding(self):
        self.start_data_acquisition()
        self.state_change()

    def stopping(self):
        self.stop_data_acquisition()
        self.state_change()

    def stopped(self):
        pass

    def aborting(self):
        self.stop_data_acquisition()
        self.state_change()

    def aborted(self):
        pass

    def resetting(self):
        print('- Resetting -')
        self.state_change()
