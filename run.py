from lora_manager_thing import *
from lora_staff_thing import *

import argparse

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", '-n', action='store', type=str,
                        required=False, default='hue_manager_thing', help="thing name")
    parser.add_argument("--host", '-ip', action='store', type=str,
                        required=False, default='127.0.0.1', help="host name")
    parser.add_argument("--port", '-p', action='store', type=int,
                        required=False, default=11083, help="port")
    parser.add_argument("--alive_cycle", '-ac', action='store', type=int,
                        required=False, default=60, help="alive cycle")
    parser.add_argument("--auto_scan", '-as', action='store_true',
                        required=False, help="middleware auto scan enable")
    parser.add_argument("--log", action='store_true', dest='log',
                        required=False, default=True, help="log enable")
    parser.add_argument("--serial_port", '-sp', action='store', type=str,
                        required=False, default='/dev/ttyACM0', help="serial port")
    parser.add_argument("--baud_rate", '-br', action='store', type=int,
                        required=False, default=115200, help="baud rate")  
    parser.add_argument("--scan_cycle", '-sc', action='store', type=int,
                        required=False, default=3, help="scan_cycle")
    parser.add_argument("--mode", '-md', action='store', type=str,
                        required=False, default=SoPManagerMode.SPLIT.value, help="scan_cycle")
                      
    arg_list, unknown = parser.parse_known_args()

    return arg_list


def generate_thing(args):
    client = LoRaManagerThing(name=args.name, ip=args.host, port=args.port, ssl_ca_path=None, ssl_enable=False,
                                alive_cycle=args.alive_cycle, service_list=[], scan_cycle=args.scan_cycle,
                                mode=args.mode, serial_port = args.serial_port, baud_rate = args.baud_rate,)                                
    return client


if __name__ == '__main__':
    args = arg_parse()
    thing = generate_thing(args)
    thing.setup(avahi_enable=args.auto_scan)
    thing.run()
