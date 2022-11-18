from big_thing_py.utils import *
import threading
import serial

nonono = {}
def read_thread(my_serial):
    """
    It continuously reads data
    """
    while True:
        rx_buf = ''
        while not rx_buf.endswith('OnRxDone'):
            rx_buf += my_serial.read().decode()
        
    parse_data(rx_buf)

def parse_data(buf):
    words = buf.split()


