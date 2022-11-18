from big_thing_py.utils import *
import threading
import serial
import time

idx_cnt = 0
idx_id_map = {}
sensor_data = dict.fromkeys(['moved', 'temperature', 'pressure',
                             'humidity', 'ax', 'ay', 'az'])
sensor_data_dict = {}

def get_temperature(idx):
    global sensor_data_dict
    if idx not in idx_id_map.keys():
        time.sleep(3)
    my_id = idx_id_map[idx]
    return sensor_data_dict[my_id]['temperature']

def get_humidity(idx):
    global sensor_data_dict
    if idx not in idx_id_map.keys():
        time.sleep(3)
    my_id = idx_id_map[idx]
    return sensor_data_dict[my_id]['humidity'] 

def read_thread(my_serial):
    """
    It continuously reads data
    """
    # flush buffers before the read thread starts
    time.sleep(0.1)
    my_serial.reset_input_buffer()
    my_serial.reset_output_buffer()

    while True:
        rx_buf = ''
        while not rx_buf.endswith('OnRxDone'):
            rx_buf += my_serial.read().decode()
        parse_data(rx_buf)


def parse_data(buf):
    global sensor_data_dict
    global idx_cnt
    words = buf.split()
    node_id = int(words[0][2:])
    if node_id not in idx_id_map.values():
        idx_id_map[idx_cnt] = node_id
        idx_cnt += 1
    sensor_data['moved'] = int(words[2][1])
    sensor_data['temperature'] = float(words[3][1:]) / 100
    sensor_data['pressure'] = float(words[4][1:]) / 10
    sensor_data['humidity'] = float(words[5][1:]) / 10
    sensor_data['ax'] = int(words[6][2:])
    sensor_data['ay'] = int(words[7][2:])
    sensor_data['az'] = int(words[8][2:])
    sensor_data_dict[node_id] = sensor_data
    # print(sensor_data_dict)

class LoRaStaffThingInfo(SoPStaffThingInfo):
    def __init__(self, device_id: str, idx: int) -> None:
        super().__init__(device_id)
        self.idx = idx        