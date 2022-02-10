from mtypy.opcua_server_pea import OPCUAServerPEA

from service_raw_data_acquisition import ServiceRawDataAcquisition

import time

module = OPCUAServerPEA()

# Service definition
service_rda = ServiceRawDataAcquisition('raw_data_acquisition', 'provides webserver with frames from the camera')
module.add_service(service_rda)

# Start server
print('--- Start OPC UA server ---')
module.run_opcua_server()

# Test
opcua_server = module.get_opcua_server()
opcua_ns = module.get_opcua_ns()
time.sleep(1)
print('--- Set parameters of procedure to Operator mode ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.shutter_speed_setpoint.op_src_mode.StateOpOp').set_value(True)
time.sleep(1)

print('--- Set procedure parameters ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedures.free_run.procedure_parameters.shutter_speed_setpoint.VOp').set_value(10000)
time.sleep(1)

print('--- Set service to operator mode ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.op_src_mode.StateOpOp').set_value(True)
time.sleep(2)

print('--- Set service procedure ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.procedure_control.ProcedureOp').set_value(1)
time.sleep(2)

print('--- Start service ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.state_machine.CommandOp').set_value(4)
time.sleep(5)

print('--- Complete service ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.state_machine.CommandOp').set_value(1024)
time.sleep(1)

print('--- Reset service ---')
opcua_server.get_node('ns=3;s=services.raw_data_acquisition.state_machine.CommandOp').set_value(2)
