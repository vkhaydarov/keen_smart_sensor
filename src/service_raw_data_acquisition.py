from mtypy.service import Service
from mtypy.procedure import Procedure
from mtypy.operation_elements import *
from mtypy.indicator_elements import *
import time
import requests


class ServiceRawDataAcquisition(Service):
    def __init__(self, tag_name, tag_description):
        super().__init__(tag_name, tag_description)
        self.add_free_run_procedure()
        self.add_snapshot_procedure()
        self.planteye_endpoint = '127.0.0.1:5000/get_frame'
        self.run_webserver()

    def add_free_run_procedure(self):
        # Free run procedure
        proc_free_run = Procedure(0, 'free_run', is_self_completing=False, is_default=True)
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
        [proc_free_run.add_procedure_parameter(proc_param) for proc_param in proc_parameters]

        report_values = [DIntView('shutter_speed_feedback', v_scl_min=1, v_scl_max=60000000, v_unit=23),
                         DIntView('gain_feedback', v_scl_min=0, v_scl_max=48, v_unit=23),
                         BinView('auto_brigthness_feedback', v_state_0='off', v_state_1='on'),
                         StringView('webserver_endpoint'),
                         ]
        [proc_free_run.add_report_value(report_value) for report_value in report_values]

        self.add_procedure(proc_free_run)

    def add_snapshot_procedure(self):
        # Snapshot run procedure
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

    def idle(self):
        print('- Idle -')
        cycle = 0
        while True:
            if self.thread_ctrl.get_flag('idle'):
                break
            print('Cycle %i' % cycle)
            cycle += 1
            time.sleep(1)

    def starting(self):
        print('- Starting -')
        self.procedures[0].report_values['webserver_endpoint'].set_v(self.planteye_endpoint)
        self.configure_planteye()
        self.state_machine.start()

    def configure_planteye(self):
        pass

    def run_webserver(self):
        pass

    def request_frame_from_planteye(self):
        res = requests.get('http://127.0.0.1:5000/get_frame').json()
        frame = res['camera']['data']['frame']['value'][0:100]
        print(frame)
        return frame

    def update_frame(self):
        frame = self.request_frame_from_planteye()

    def execute(self):
        print('- Execute -')

        print(f'ProcedureCur is {self.procedure_control.get_procedure_cur()}')
        if self.procedure_control.get_procedure_cur() == 0:
            self.execute_free_run()
        elif self.procedure_control.get_procedure_cur() == 1:
            self.execute_snapshot()

    def execute_free_run(self):
        cycle = 0
        while True:
            if self.thread_ctrl.get_flag('execute'):
                break
            print('Cycle %i' % cycle)
            self.update_frame()
            cycle += 1
            time.sleep(1)

    def execute_snapshot(self):
        self.update_frame()
        self.state_machine.complete()

    def completing(self):
        self.procedures[0].report_values['webserver_endpoint'].set_v('')
        self.state_machine.complete()

    def completed(self):
        pass

    def pausing(self):
        pass

    def paused(self):
        pass

    def resuming(self):
        pass

    def holding(self):
        pass

    def held(self):
        pass

    def unholding(self):
        pass

    def stopping(self):
        pass

    def stopped(self):
        pass

    def aborting(self):
        pass

    def aborted(self):
        pass

    def resetting(self):
        print('- Resetting -')
        self.state_machine.reset()
