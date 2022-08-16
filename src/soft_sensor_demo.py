from mtppy.opcua_server_pea import OPCUAServerPEA

from service_raw_data_acquisition import ServiceRawDataAcquisition
from service_archiving import ServiceArchiving
from service_data_processing import ServiceDataProcessing

import time

module = OPCUAServerPEA()

planteye_endpoint = 'http://10.6.51.140:5000/'

# Service definition
service_rda = ServiceRawDataAcquisition('raw_data_acquisition', 'provides webserver with frames from the camera')
service_rda.set_planteye_endpoint(planteye_endpoint)
module.add_service(service_rda)

service_arch = ServiceArchiving('archiving', 'archives data')
service_arch.set_planteye_endpoint(planteye_endpoint)
module.add_service(service_arch)

service_data_proc = ServiceDataProcessing('data_processing', 'processes data')
service_data_proc.set_planteye_endpoint(planteye_endpoint)
module.add_service(service_data_proc)


# Start server
print('--- Start OPC UA server ---')
module.run_opcua_server()

# Test
opcua_server = module.get_opcua_server()
opcua_ns = module.get_opcua_ns()
time.sleep(1)
print('--- Set Shutter Speed---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.shutter_speed_setpoint.op_src_mode.StateOpOp').set_value(True)
time.sleep(2)
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.shutter_speed_setpoint.VOp').set_value(10000)
time.sleep(1)

print('--- Set Time Interval---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.time_interval_setpoint.op_src_mode.StateOpOp').set_value(True)
time.sleep(2)
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.time_interval_setpoint.VOp').set_value(1.0)
time.sleep(1)

print('--- Set services to operator mode ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.op_src_mode.StateOpOp').set_value(True)
opcua_server.get_node('ns=3;s=services.archiving.op_src_mode.StateOpOp').set_value(True)
opcua_server.get_node('ns=3;s=services.data_processing.op_src_mode.StateOpOp').set_value(True)
time.sleep(1)

print('--- Set service procedure ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedure_control.ProcedureOp').set_value(0)
time.sleep(1)

print('--- Start service data acquisition---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.state_machine.CommandOp').set_value(4)
time.sleep(1)

print('--- Start service data processing---')
opcua_server.get_node('ns=3;s=services.data_processing.state_machine.CommandOp').set_value(4)
time.sleep(3)

print('--- Start service archiving---')
opcua_server.get_node('ns=3;s=services.archiving.state_machine.CommandOp').set_value(4)
time.sleep(60)

print('--- Complete service data processing---')
opcua_server.get_node('ns=3;s=services.data_processing.state_machine.CommandOp').set_value(1024)
time.sleep(1)

print('--- Complete service data archiving---')
opcua_server.get_node('ns=3;s=services.archiving.state_machine.CommandOp').set_value(1024)
time.sleep(1)

print('--- Complete service data acquisition---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.state_machine.CommandOp').set_value(1024)
time.sleep(1)
