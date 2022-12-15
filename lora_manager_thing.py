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
                 manager_mode: SoPManagerMode = SoPManagerMode.JOIN.value,  scan_cycle=30,
                 serial_port: str = '/dev/ttyACM0', baud_rate: int = 115200):
        super().__init__(name, service_list, alive_cycle, is_super, is_parallel,
                         ip, port, ssl_ca_path, ssl_enable, log_name, log_enable, log_mode, append_mac_address,
                         manager_mode, scan_cycle)
        self._staff_thing_list: List[LoRaStaffThing] = []
        self.my_serial = serial.Serial(serial_port, baudrate=baud_rate, timeout=None)        

    def setup(self, avahi_enable=True):
        print('warming up ...')
        self.my_thread = threading.Thread(
            target=read_thread, args=(self.my_serial, ))
        self.my_thread.start()
        time.sleep(5)
        self.connection_validation = threading.Thread(target=alive_check)
        self.connection_validation.start()
        print('done..')
        return super().setup(avahi_enable=avahi_enable)

    # def _handle_staff_message(self, msg: str):  ################### jy
    #     global newly_discovered_node
    #     protocol_type = None
    #     lora_device_list: Dict = msg

    #     if len(newly_discovered_node) != 0:
    #         protocol_type = [SoPProtocolType.Base.TM_REGISTER, SoPProtocolType.Base.TM_ALIVE]
    #     else:
    #         # time.sleep(0.5)
    #         protocol_type = [SoPProtocolType.Base.TM_VALUE_PUBLISH]
        
    #     if SoPProtocolType.Base.TM_REGISTER in protocol_type:
    #         self._handle_staff_REGISTER(msg)
    #     elif SoPProtocolType.Base.TM_ALIVE in protocol_type:
    #         self._handle_staff_ALIVE(msg)
    #     elif SoPProtocolType.Base.TM_VALUE_PUBLISH in protocol_type or SoPProtocolType.Base.TM_VALUE_PUBLISH_OLD in protocol_type:
    #         self._handle_staff_VALUE_PUBLISH(msg)
    #     elif SoPProtocolType.Base.TM_RESULT_EXECUTE in protocol_type:
    #         self._handle_staff_RESULT_EXECUTE(msg)
    
    # def _handle_staff_REGISTER(self, msg):  ### jy
    #     global newly_discovered_node, node_idx
    #     for node in newly_discovered_node:            
    #         staff_thing_info = LoRaStaffThingInfo(device_id=node, idx=node_idx,)            
    #         self._staff_register_queue.put(staff_thing_info)
    #         node_idx += 1
    #         newly_discovered_node.remove(str(node))


    def _receive_staff_packet(self): ### jy
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
                            self._send_TM_VALUE_PUBLISH("MT/EXECUTE/__"+value.get_name(), staff_thing.get_name(), value.dump_pub())

        return None


    ##################################
    # override
    def _connect_staff_thing(self, staff_thing: SoPStaffThing) -> bool:
        # api 방식에서는 api 요청 결과에 staff thing이 포함되어 있으면 연결.
        staff_thing._receive_queue.put(dict(device_id=staff_thing.get_device_id(),
                                            protocol=SoPProtocolType.Base.TM_REGISTER,
                                            payload=staff_thing.dump()))
        staff_thing._is_connected = True

    # override
    def _disconnect_staff_thing(self, staff_thing: SoPStaffThing) -> bool:
        # api 방식에서는 api 요청 결과에 staff thing이 포함되어 있지 않으면 연결해제.
        staff_thing._is_connected = False

    # override
    def _handle_REGISTER_staff_message(self, staff_thing: SoPStaffThing, payload: str) -> Tuple[str, dict]:
        
        return staff_thing.get_name(), payload

    # override
    def _handle_UNREGISTER_staff_message(self, staff_thing: SoPStaffThing) -> str:
        self._send_TM_UNREGISTER(staff_thing.get_name())

    # override
    def _handle_ALIVE_staff_message(self, staff_thing: SoPStaffThing) -> str:
        pass

    # override
    def _handle_VALUE_PUBLISH_staff_message(self, staff_thing: SoPStaffThing, payload: str) -> Tuple[str, str, dict]:
        pass

    # override
    def _handle_RESULT_EXECUTE_staff_message(self, staff_thing: SoPStaffThing, payload: str) -> str:
        pass

    # override
    def _send_RESULT_REGISTER_staff_message(self, staff_thing: SoPStaffThing, payload: dict) -> str:
        pass

    # override
    def _send_RESULT_UNREGISTER_staff_message(self, staff_thing: SoPStaffThing, payload: dict) -> str:
        pass

    # override
    def _send_EXECUTE_staff_message(self, staff_thing: SoPStaffThing, payload: dict) -> str:
        pass

    # override
    def _publish_staff_message(self, staff_msg) -> None:
        pass

    # override
    def _receive_staff_message(self):
        for staff_thing in self._staff_thing_list:
            try:
                staff_msg = staff_thing._receive_queue.get(
                    timeout=THREAD_TIME_OUT)
                return staff_msg
            except Empty:
                pass

    # override
    def _parse_staff_message(self, staff_msg) -> Tuple[SoPProtocolType, str, str]:
        protocol = staff_msg['protocol']
        device_id = staff_msg['device_id']
        payload = staff_msg['payload']

        return protocol, device_id, payload

    # override
    def _scan_staff_thing(self, timeout: float = 5) -> List[dict]:
        pass

    ###################################
   

    def _create_staff(self, staff_thing_info: dict) -> LoRaStaffThing:
        
        idx = staff_thing_info.idx
        uniqueid = staff_thing_info.device_id

        lora_child_thing = LoRaStaffThing(
            name='sensor'+str(idx), service_list=[], alive_cycle=10, idx=idx, device_id=uniqueid)

        lora_child_thing.make_service_list()
        lora_child_thing.set_function_result_queue(self._publish_queue)
        for staff_service in lora_child_thing.get_value_list() + lora_child.get_function_list():
            staff_service.add_tag(SoPTag(self._conf_select))
        

        return lora_child_thing
