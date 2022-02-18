from mtppy.service import Service
from mtppy.procedure import Procedure
from mtppy.operation_elements import *
from mtppy.indicator_elements import *
import time
import requests


class ServiceDataProcessing(Service):
    def __init__(self, tag_name, tag_description):
        super().__init__(tag_name, tag_description)
        self.planteye_endpoint = None
        self.add_procedure_trigger_based()

    def set_planteye_endpoint(self, planteye_endpoint):
        self.planteye_endpoint = planteye_endpoint

    def add_procedure_trigger_based(self):
        proc_trigger = Procedure(0, 'trigger_based', is_self_completing=False, is_default=True)
        proc_parameters = [
            DIntServParam('model_id', v_scl_min=0, v_scl_max=1),
        ]
        [proc_trigger.add_procedure_parameter(proc_param) for proc_param in proc_parameters]
        report_values = [AnaView('result', v_scl_min=-65535, v_scl_max=65536, v_unit=23),
                         AnaView('confidence_interval', v_scl_min=0, v_scl_max=100, v_unit=23),
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
        self.start_data_processing()
        self.state_machine.start()

    def execute(self):
        print('- Execute -')
        print(f'ProcedureCur is {self.procedure_control.get_procedure_cur()}')
        self.start_data_processing()

    def pipeline_configuration_1(self):
        return [
            {
                'name': '001_resize',
                'type': 'image_resize',
                'hidden': True,
                'parameters': {
                    'width': 250,
                    'height': 250,
                    'interpolation': 'INTER_NEAREST',
                },
            },
            {
                'name': '002_crop',
                'type': 'image_crop',
                'hidden': True,
                'parameters': {
                    'x_init': 2,
                    'x_diff': 248,
                    'y_init': 2,
                    'y_diff': 248,
                },
            },
            {
                'name': '003_inference',
                'type': 'tf_inference',
                'hidden': False,
                'parameters': {
                    'path_to_models': '../models/',
                    'model_name': 'dogs_vs_cats',
                    'model_version': '1.0',
                },
            },
        ]

    def start_data_processing(self):
        started = False
        proc_id = self.procedure_control.get_procedure_cur()
        if self.procedures[proc_id].procedure_parameters['model_id'].get_v_out() == 0:
            config_addon = self.pipeline_configuration_1()
        else:
            return

        while not started:
            if self.thread_ctrl.get_flag('starting'):
                break
            current_config = self.get_current_planteye_config()
            if current_config is not None:
                for cfg_element in config_addon:
                    current_config['processors'][cfg_element['name']] = cfg_element
                started = self.set_current_planteye_config(current_config)
            time.sleep(0.5)

    def stop_processing(self):
        if self.procedure_control.get_procedure_cur() == 0:
            config_addon = self.pipeline_configuration_1()
        else:
            return
        current_config = self.get_current_planteye_config()
        if current_config is None:
            return False
        if 'processors' not in current_config:
            return True
        for cfg_element in config_addon:
            if cfg_element['name'] in current_config['processors']:
                current_config['processors'].pop(cfg_element['name'])
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
        self.stop_processing()
        self.state_machine.complete()

    def completed(self):
        pass

    def pausing(self):
        self.stop_processing()
        self.state_machine.pause()

    def paused(self):
        pass

    def resuming(self):
        self.start_data_processing()

    def holding(self):
        self.stop_processing()
        self.state_machine.hold()

    def held(self):
        pass

    def unholding(self):
        self.start_data_processing()

    def stopping(self):
        self.stop_processing()
        self.state_machine.stop()

    def stopped(self):
        pass

    def aborting(self):
        self.stop_processing()
        self.state_machine.abort()

    def aborted(self):
        pass

    def resetting(self):
        print('- Resetting -')
        self.state_machine.reset()