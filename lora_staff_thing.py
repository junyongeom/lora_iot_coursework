from big_thing_py.manager_thing import *
from lora_manager_thing import *
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

    # override
    def make_service_list(self):
        tag_list = [SoPTag(name='lora_sensor')]
        staff_function_list: List[SoPService] = []
        staff_value_list: List[SoPService] = [SoPValue(name='temperature',
                                                       func=self.current_temperature,
                                                       type=SoPType.DOUBLE,  
                                                       bound=(-100, 100),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='humidity',
                                                       func=self.current_humidity,
                                                       type=SoPType.DOUBLE,
                                                       bound=(-100, 100),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='pressure',
                                                       func=self.current_pressure,
                                                       type=SoPType.INTEGER ,
                                                       bound=(-10000, 10000),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='ax',
                                                       func=self.current_ax,
                                                       type=SoPType.INTEGER ,  
                                                       bound=(-10000, 10000),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='ay',
                                                       func=self.current_ay,
                                                       type=SoPType.INTEGER,
                                                       bound=(-10000, 10000),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='az',
                                                       func=self.current_az,
                                                       type=SoPType.INTEGER,
                                                       bound=(-10000, 10000),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              SoPValue(name='moved',
                                                       func=self.moved,
                                                       type=SoPType.INTEGER,
                                                       bound=(-2, 2),
                                                       cycle=3,
                                                       tag_list=tag_list),
                                              ]
        
        self.add_tag_to_service(staff_value_list + staff_function_list)
