from mtypy.service import Service
from mtypy.procedure import Procedure
from mtypy.operation_elements import *
from mtypy.indicator_elements import *
import time


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
            DIntServParam('model_id', v_scl_min=0, v_scl_max=0),
        ]
        [proc_trigger.add_procedure_parameter(proc_param) for proc_param in proc_parameters]
        report_values = [AnaView('result', v_scl_min=-65535, v_scl_max=65536, v_unit=23),
                         AnaView('confidence_interval', v_scl_min=0, v_scl_max=100, v_unit=23),
                         DIntView('WQC', v_scl_min=0, v_scl_max=255, v_unit=23),
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
        self.configure_planteye()
        self.state_machine.start()

    def configure_planteye(self):
        pass

    def execute(self):
        print('- Execute -')
        print(f'ProcedureCur is {self.procedure_control.get_procedure_cur()}')
        self.start_data_processing()

    def start_data_processing(self):
        pass

    def stop_processing(self):
        pass

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

    def trigger_cb(self):
        pass
