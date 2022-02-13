from mtppy.service import Service
from mtppy.procedure import Procedure
from mtppy.operation_elements import *
from mtppy.indicator_elements import *
import time
import requests


class ServiceArchiving(Service):
    def __init__(self, tag_name, tag_description):
        super().__init__(tag_name, tag_description)
        self.planteye_endpoint = None
        self.add_procedure_trigger_based()

    def set_planteye_endpoint(self, planteye_endpoint):
        self.planteye_endpoint = planteye_endpoint

    def add_procedure_trigger_based(self):
        proc_trigger = Procedure(0, 'trigger_based', is_self_completing=False, is_default=True)
        proc_parameters = [
            StringServParam('data_sink'),
            StringServParam('data_format'),
        ]
        [proc_trigger.add_procedure_parameter(proc_param) for proc_param in proc_parameters]
        report_values = [DIntView('WQC', v_scl_min=0, v_scl_max=255, v_unit=23),
                         StringView('status_message'),
                         ]
        [proc_trigger.add_report_value(report_value) for report_value in report_values]

        self.add_procedure(proc_trigger)

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
        self.start_archiving()
        self.state_machine.start()

    def execute(self):
        print('- Execute -')

    def start_archiving(self):
        started = False
        while not started:
            current_config = self.get_current_planteye_config()
            if current_config is not None:
                current_config['processors']['100_archiving'] = {
                    'name': 'archiver',
                    'type': 'save_on_disk',
                    'parameters': {
                        'save_path': '../data'
                    }
                }
                started = self.set_current_planteye_config(current_config)
            time.sleep(0.5)

    def stop_archiving(self):
        current_config = self.get_current_planteye_config()
        if current_config is None:
            return False
        if 'processors' not in current_config:
            return True
        if 'archiving' in current_config['processors']:
            current_config['processors'].pop('100_archiving')
            self.set_current_planteye_config(current_config)
            return True
        else:
            return True

    def get_current_planteye_config(self):
        url = self.planteye_endpoint + '/get_config'
        try:
            current_config = requests.get(url).json()
            return current_config
        except ConnectionError:
            print('PlantEye is unreachable')
            return None
        except Exception:
            print('Cannot get configuration')
            return None

    def set_current_planteye_config(self, config):
        url = self.planteye_endpoint + '/upload_config'
        try:
            ret_val = requests.post(url, json=config)
            return ret_val.ok
        except Exception:
            print('Cannot upload new configuration onto PlantEye')
            return False

    def completing(self):
        self.stop_archiving()
        self.state_machine.complete()

    def completed(self):
        pass

    def pausing(self):
        self.stop_archiving()
        self.state_machine.pause()

    def paused(self):
        pass

    def resuming(self):
        self.start_archiving()

    def holding(self):
        self.stop_archiving()
        self.state_machine.hold()

    def held(self):
        pass

    def unholding(self):
        self.start_archiving()

    def stopping(self):
        self.stop_archiving()
        self.state_machine.stop()

    def stopped(self):
        pass

    def aborting(self):
        self.stop_archiving()
        self.state_machine.abort()

    def aborted(self):
        pass

    def resetting(self):
        print('- Resetting -')
        self.state_machine.reset()
