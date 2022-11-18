from big_thing_py.manager_thing import *
from lora_utils import *
from lora_manager_thing import *

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
        self._device_id = device_id   
    def moved(self) -> int:        
        return get_moved(self._device_id)

    def current_temperature(self) -> float:        
        return get_temperature(self._device_id)

    def current_pressure(self) -> float:
        return get_pressure(self._device_id)

    def current_humidity(self) -> float:
        return get_humidity(self._device_id)

    def current_ax(self) -> int:
        return get_ax(self._device_id)
    
    def current_ay(self) -> int:
        return get_ay(self._device_id)

    def current_az(self) -> int:
        return get_az(self._device_id)
