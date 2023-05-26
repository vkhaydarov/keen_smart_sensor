from mtppy.opcua_server_pea import OPCUAServerPEA
import argparse
import sys

from service_raw_data_acquisition import ServiceRawDataAcquisition
from service_archiving import ServiceArchiving
from service_data_processing import ServiceDataProcessing
from yaml import safe_load
import logging


def read_config_file(path_to_cfg):
    logging.info(f'Configuration is read from the file {path_to_cfg}')
    with open(path_to_cfg) as config_file:
        config_dict = safe_load(config_file)
    return config_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PlantEye: Smart Sensor')
    parser.add_argument('--cfg',
                        help="Path to configuration file",
                        metavar='config',
                        type=str,
                        required=False)
    args = parser.parse_args(sys.argv[1:])
    print(args)

    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    path_to_cfg = args.cfg
    if path_to_cfg is None:
        path_to_cfg = 'src/config_deploy.yaml'
    config_dict = read_config_file(path_to_cfg)
    
    module = OPCUAServerPEA(endpoint='opc.tcp://0.0.0.0:4840/')

    # Service definition
    service_rda = ServiceRawDataAcquisition('raw_data_acquisition', 'provides webserver with frames from the camera')
    service_rda.set_planteye_endpoint(config_dict['planteye_endpoint'])
    module.add_service(service_rda)

    service_arch = ServiceArchiving('archiving', 'archives data', archiving_path=config_dict['local_archiving_path'])
    service_arch.set_planteye_endpoint(config_dict['planteye_endpoint'])
    module.add_service(service_arch)

    service_data_proc = ServiceDataProcessing('data_processing', 'processes data',
    model_path=config_dict['model_path'],
    model_name=config_dict['model_name'],
    model_version=config_dict['model_version'])

    service_data_proc.set_planteye_endpoint(config_dict['planteye_endpoint'])
    module.add_service(service_data_proc)

    # Start server
    print('--- Start OPC UA server ---')
    module.run_opcua_server()
