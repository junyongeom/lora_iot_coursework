from big_thing_py.manager_thing import *

class LoRaStaffThing(SoPStaffThing):
    """
    It's a lora gateway which connected with the server.
    It receives sensor data from sensor node and report it
    to the server using serial communication.
    """
    def __init__(self, name: str, service_list: List[SoPService], alive_cycle: float, is_super: bool = False, is_parallel: bool = True,
                 device_id: str = None,
                 idx=None, bridge_ip=None, user_key=None, header=None):
        super().__init__(name, service_list, alive_cycle,
                         is_super, is_parallel, device_id)
        self._idx = idx
        self._bridge_ip = bridge_ip.strip('/')
        self._user_key = user_key
        self._header = header

    def on(self) -> bool:
        SOPLOG_DEBUG('on actuate!!!', 'green')
        res: requests.Response = API_request(
            method=RequestMethod.PUT,
            url=f'{self._bridge_ip}/{self._user_key}/lights/{self._idx}/state',
            body=dict_to_json_string({'on': True}),
            header=self._header,
            login_retry=False)
        data = res.json()
        if 'success' in data[0]:
            return True
        else:
            return False

    def off(self) -> bool:
        SOPLOG_DEBUG(colored('off actuate!!!', 'green'))
        res: requests.Response = API_request(
            method=RequestMethod.PUT,
            url=f'{self._bridge_ip}/{self._user_key}/lights/{self._idx}/state',
            body=dict_to_json_string({'on': False}),
            header=self._header,
            login_retry=False)
        data = res.json()
        if 'success' in data[0]:
            return True
        else:
            return False

    def set_brightness(self, brightness: int) -> bool:
        SOPLOG_DEBUG('set_brightness actuate!!!', 'green')
        res: requests.Response = API_request(
            method=RequestMethod.PUT,
            url=f'{self._bridge_ip}/{self._user_key}/lights/{self._idx}/state',
            body=dict_to_json_string({'bri': int(brightness)}),
            header=self._header,
            login_retry=False)
        data = res.json()
        if 'success' in data[0]:
            return True
        else:
            return False

    def set_color(self, r: int, g: int, b: int) -> bool:
        SOPLOG_DEBUG('set_color actuate!!!', 'green')
        x, y = rgb_to_xy(float(r), float(g), float(b))
        res: requests.Response = API_request(
            method=RequestMethod.PUT,
            url=f'{self._bridge_ip}/{self._user_key}/lights/{self._idx}/state',
            body=dict_to_json_string({'xy': [x, y]}),
            header=self._header,
            login_retry=False)
        data = res.json()
        if 'success' in data[0]:
            return True
        else:
            return False

    def get_idx(self):
        return self._idx

    def set_idx(self, idx):
        self._idx = idx