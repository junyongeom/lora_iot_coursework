from big_thing_py.manager_thing import *
from lora_utils import *
import serial # pyserial

class LoRaStaffThing(SoPStaffThing):
    """
    It's a virtual LoRa gateway, which makes
    treat several 
    """
    def __init__(self, name: str, service_list: List[SoPService], alive_cycle: float, is_super: bool = False, is_parallel: bool = True,
                 device_id: str = None, idx=None,):
        super().__init__(name, service_list, alive_cycle,
                         is_super, is_parallel, device_id)
        self._idx = idx
        
        
    def moved(self) -> bool:
        
        return False

    def current_temperature(self) -> float:
        # now = datetime.datetime.now()
        # return now.month
        return 30

    def current_pressure(self) -> float:
        return 1000

    def current_humidity(self) -> float:
        return 1000

    def current_ax(self) -> int:
        return 1
    
    def current_ay(self) -> int:
        return 2

    def current_az(self) -> int:
        return 1

    def set_idx(self, idx):
        self._idx = idx
    
    def get_idx(self):
        return self._idx