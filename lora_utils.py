from big_thing_py.utils import *
from lora_staff_thing import *
from lora_manager_thing import *
import threading
import serial
import time

node_idx = 0
newly_discovered_node = []
node_table = []
sensor_data = dict.fromkeys(['moved', 'temperature', 'pressure',
                             'humidity', 'ax', 'ay', 'az'])
sensor_data_table = {}
node_life = {}

def get_temperature(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)    
    return sensor_data_table[node_id]['temperature']

def get_pressure(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['pressure'] 

def get_humidity(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['humidity'] 

def get_moved(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['moved'] 

def get_ax(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['ax'] 

def get_ay(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['ay'] 

def get_az(node_id):
    global sensor_data_table
    if node_id not in node_table:
        time.sleep(3)
    return sensor_data_table[node_id]['az'] 

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
        alive_check()

def parse_data(buf):
    global sensor_data_table, newly_discovered_node, node_table
    # print("tabletable", node_table)
    print('sensor_table', sensor_data_table)

    words = buf.split()
    node_id = words[0][2:]
    if node_id not in node_table:
        node_table.append(node_id)
        newly_discovered_node.append(node_id)
    sensor_data['moved'] = int(words[2][1])
    sensor_data['temperature'] = float(words[3][1:]) / 100
    sensor_data['pressure'] = float(words[4][1:]) / 10
    sensor_data['humidity'] = float(words[5][1:]) / 10
    sensor_data['ax'] = int(words[6][2:])
    sensor_data['ay'] = int(words[7][2:])
    sensor_data['az'] = int(words[8][2:])
    sensor_data_table[node_id] = sensor_data
    node_life[node_id] = time.time() 
    # print(sensor_data_table)

def alive_check():
    """
    if there are no messages for 15 seconds from a node
    we consider it as there is no connection between the node and gateway
    """
    global node_table
    for node in node_table:
        curr = time.time()
        if curr - node_life[node] > 15:
            node_table.remove(node)

class LoRaStaffThingInfo(SoPStaffThingInfo):
    def __init__(self, device_id: str, idx: int) -> None:
        super().__init__(device_id)       
        self.idx = idx