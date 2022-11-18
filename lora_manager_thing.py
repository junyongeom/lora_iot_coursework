from big_thing_py.manager_thing import *
from lora_staff_thing import *
from lora_utils import *


class LoRaManagerThing(SoPManagerThing):
    """
    It's a lora gateway which connected with the server.
    It receives sensor data from sensor node and report it
    to the server using serial communication.
    """

    def __init__(self, name: str, service_list: List[SoPService], alive_cycle: float, is_super: bool = False, is_parallel: bool = True,
                 ip: str = None, port: int = None, ssl_ca_path: str = None, ssl_enable: bool = None, log_name: str = None, log_enable: bool = True, log_mode: SoPPrintMode = SoPPrintMode.ABBR, append_mac_address: bool = True,
                 mode: SoPManagerMode = SoPManagerMode.SPLIT, network_type: SoPNetworkType = SoPNetworkType.MQTT, scan_cycle=3,
                 serial_port: str = '/dev/ttyACM0', baud_rate: int = 115200):
        super().__init__(name, service_list, alive_cycle, is_super, is_parallel,
                         ip, port, ssl_ca_path, ssl_enable, log_name, log_enable, log_mode, append_mac_address,
                         mode, network_type, scan_cycle)
        self._staff_thing_list: List[LoRaStaffThing] = []
        self.my_serial = serial.Serial(serial_port, baudrate=baud_rate, timeout=None)        

    def setup(self, avahi_enable=True):
        print('set up ...')
        self.my_thread = threading.Thread(
            target=read_thread, args=(self.my_serial, ))
        self.my_thread.start()
        time.sleep(5)
        print('set up done..')
        return super().setup(avahi_enable=avahi_enable)

    def _handle_staff_message(self, msg: str):
        global newly_discovered_node
        protocol_type = None
        lora_device_list: Dict = msg

        if len(newly_discovered_node) != 0:
            protocol_type = [SoPProtocolType.Base.TM_REGISTER, SoPProtocolType.Base.TM_ALIVE]
        else:
            protocol_type = [SoPProtocolType.Base.TM_VALUE_PUBLISH]
        

        if SoPProtocolType.Base.TM_REGISTER in protocol_type:
            self._handle_staff_REGISTER(msg)
        elif SoPProtocolType.Base.TM_ALIVE in protocol_type:
            self._handle_staff_ALIVE(msg)
        elif SoPProtocolType.Base.TM_VALUE_PUBLISH in protocol_type or SoPProtocolType.Base.TM_VALUE_PUBLISH_OLD in protocol_type:
            self._handle_staff_VALUE_PUBLISH(msg)
        elif SoPProtocolType.Base.TM_RESULT_EXECUTE in protocol_type:
            self._handle_staff_RESULT_EXECUTE(msg)

    # TODO: implement this
    def _send_staff_message(self, msg: Union[StaffRegisterResult, None]):
        if type(msg) == StaffRegisterResult:
            self._send_staff_RESULT_REGISTER(msg)
        elif type(msg) == None:
            pass
        else:
            self._publish_staff_packet(msg)

    def _handle_staff_REGISTER(self, msg):
        # lora_device_list = msg
        # for idx, staff_info in lora_device_list.items():
        #     staff_thing_info = LoRaStaffThingInfo(device_id=staff_info['uniqueid'], idx=idx,)

        #     self._staff_register_queue.put(staff_thing_info)
        global newly_discovered_node, node_idx
        for node in newly_discovered_node:            
            staff_thing_info = LoRaStaffThingInfo(device_id=node, idx=node_idx,)            
            self._staff_register_queue.put(staff_thing_info)
            node_idx += 1
            newly_discovered_node.remove(str(node))


    def _handle_staff_ALIVE(self, msg):
        lora_device_list = msg
        pass

    def _handle_staff_VALUE_PUBLISH(self, msg):
        lora_device_list = msg
        pass

    def _handle_staff_RESULT_EXECUTE(self, msg):
        lora_device_list = msg
        pass

    def _send_staff_RESULT_REGISTER(self, register_result: StaffRegisterResult):
        if register_result.device_id is None:
            raise ValueError('staff thing device_id is None')

        SOPLOG_DEBUG(
            f'[_send_staff_RESULT_REGISTER] Register {register_result.staff_thing_name} complete!!!')

    def _send_staff_EXECUTE(self, msg):
        pass

    def _receive_staff_packet(self):
        cur_time = time.time()
        global node_table
        lora_device_list = node_table
        # for discover lora staff thing
        if cur_time - self._last_scan_time > self._scan_cycle:
            print('get staff things list...')
            for staff_thing in self._staff_thing_list:
                self._send_TM_ALIVE(staff_thing.get_name())
                staff_thing.set_last_alive_time(cur_time)
            if self.verify_lora_request_result(node_table):
                self._last_scan_time = cur_time
                return lora_device_list
            else:
                return False
        else:
            for staff_thing in self._staff_thing_list:
                # for check lora staff thing alive
                if staff_thing.get_registered() and cur_time - staff_thing.get_last_alive_time() > staff_thing.get_alive_cycle():
                    if self.verify_lora_request_result(lora_device_list):
                        self._send_TM_ALIVE(staff_thing.get_name())
                        staff_thing.set_last_alive_time(cur_time)
                        return lora_device_list
                    else:
                        return False
                # for check lora staff thing value publish cycle
                else:
                    for value in staff_thing.get_value_list():
                        if cur_time - value.get_last_update_time() > value.get_cycle():
                            # update() method update _last_update_time of SoPValue
                            value.update()  # TM_VALUE_PUBLISH thing name, value name, payload 
                            self._send_TM_VALUE_PUBLISH( staff_thing.get_name(),
                                value.get_name(), value.dump_pub())

        return None

    def _publish_staff_packet(self, msg):
        pass

    def verify_lora_request_result(self, result_list: list):
        return True
        # if type(result_list) == list and 'error' in result_list[0]:
        #     print_error(result_list[0]['error']['description'])
        #     return False
        # else:
        #     return True

    def _create_staff(self, staff_thing_info: LoRaStaffThingInfo) -> LoRaStaffThing:
        
        idx = staff_thing_info.idx
        uniqueid = staff_thing_info.device_id

        lora_child_thing = LoRaStaffThing(
            name='sensor'+str(idx), service_list=[], alive_cycle=10, idx=idx, device_id=uniqueid)

        # staff_value_list: List[SoPService] = []
        staff_function_list: List[SoPService] = []
        tag_list = [SoPTag(name='lora_sensor')]
        staff_value_list: List[SoPService] = [SoPValue(name='temperature',
                                                       func=lora_child_thing.current_temperature,
                                                       type=SoPType.DOUBLE,  
                                                       bound=(-100, 100),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='humidity',
                                                       func=lora_child_thing.current_humidity,
                                                       type=SoPType.DOUBLE,
                                                       bound=(-100, 100),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='pressure',
                                                       func=lora_child_thing.current_pressure,
                                                       type=SoPType.INTEGER ,
                                                       bound=(-10000, 10000),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='ax',
                                                       func=lora_child_thing.current_ax,
                                                       type=SoPType.INTEGER ,  
                                                       bound=(-10000, 10000),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='ay',
                                                       func=lora_child_thing.current_ay,
                                                       type=SoPType.INTEGER,
                                                       bound=(-10000, 10000),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='az',
                                                       func=lora_child_thing.current_az,
                                                       type=SoPType.INTEGER,
                                                       bound=(-10000, 10000),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              SoPValue(name='moved',
                                                       func=lora_child_thing.moved,
                                                       type=SoPType.INTEGER,
                                                       bound=(-2, 2),
                                                       cycle=1,
                                                       tag_list=tag_list),
                                              ]

        service_list: List[SoPService] = staff_function_list + staff_value_list

        for staff_service in service_list:            
            staff_service.add_tag(SoPTag(uniqueid))
            staff_service.add_tag(SoPTag('sensor'+str(idx)))
            lora_child_thing._add_service(staff_service)

        return lora_child_thing
