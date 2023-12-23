import time
import json
import requests
import logging
from abc import abstractmethod
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes
from enum import Enum

from FoxEss_Sonoff import settings

SONOFF_SWITCH_URI = "/zeroconf/switch"
SONOFF_INFO_URI = "/zeroconf/info"
SONOFF_PORT = "8081"


class SonoffModel(Enum):
    BASIC_R2 = 1
    BASIC_R3 = 2
    BASIC_R3_DIY = 3


class SonoffApi:
    state = None

    @staticmethod
    def getsonoff(sonoff_type: SonoffModel, init: bool = True) -> None:
        if sonoff_type == SonoffModel.BASIC_R2:
            return SonoffBasicApi(settings.sonoffDeviceHost, settings.sonoffDeviceId, settings.sonoffDeviceKey, init)
        elif sonoff_type == SonoffModel.BASIC_R3:
            return SonoffBasicApi(settings.sonoffDeviceHost, settings.sonoffDeviceId, settings.sonoffDeviceKey, init)
        elif sonoff_type == SonoffModel.BASIC_R3_DIY:
            return SonoffBasicDiyApi(settings.sonoffDeviceHost, settings.sonoffDeviceId, settings.sonoffDeviceKey, init)
        return None

    def __init__(self, dev_host: str, dev_id: str, dev_key: str) -> None:
        self._dev_host = dev_host
        self._dev_id = dev_id
        self._dev_key = dev_key

    def info(self):
        logging.info(
            f"SONOFF API: {self.__class__.__name__}, SONOFF DEVICE: {self._dev_id} at {self._dev_host}:{SONOFF_PORT}")

    @abstractmethod
    def send(self, url: str, data: dict):
        pass

    def switch_on(self):
        url = f"http://{self._dev_host}:{SONOFF_PORT}{SONOFF_SWITCH_URI}"
        data = {'switch': 'on'}
        self.send(url, data)
        logging.info("SET SONOFF STATE TO ON")
        SonoffApi.state = 1

    def switch_off(self):
        url = f"http://{self._dev_host}:{SONOFF_PORT}{SONOFF_SWITCH_URI}"
        data = {'switch': 'off'}
        self.send(url, data)
        logging.info("SET SONOFF STATE TO OFF")
        SonoffApi.state = 0

    @abstractmethod
    def read_switch_state(self):
        pass


class SonoffBasicApi(SonoffApi):

    def __init__(self, dev_host: str, dev_id: str, dev_key: str, init: bool = True) -> None:
        super().__init__(dev_host, dev_id, dev_key)
        if init:
            self.info()
            logging.info("SONOFF INITIAL CONFIGURATION: SET STATE TO OFF")
            self.switch_off()

    def send(self, url: str, data: dict):
        sequence = str(int(time.time() * 1000))
        payload = {
            'sequence': sequence,
            'deviceid': self._dev_id,
            'selfApikey': '123',
            'data': data
        }
        epayload = self.__encrypt(payload)
        logging.debug(f"SONOFF POST URL: {url}")
        logging.debug(f"SONOFF POST DATA: {data}")
        try:
            resp = requests.post(url, json=epayload, headers={'Connection': 'close'}, timeout=1)
            if resp.json()['error'] == 0:
                return resp
            else:
                logging.error(f"SONOFF Exception - Error {resp.json()['error']}")
        except Exception as ex:
            logging.error(f"SONOFF Exception {ex}")

    def __encrypt(self, payload: dict):

        hash_ = MD5.new()
        hash_.update(self._dev_key.encode('utf-8'))
        key = hash_.digest()

        iv = get_random_bytes(16)
        plaintext = json.dumps(payload['data']).encode('utf-8')

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)

        padding_len = AES.block_size - len(plaintext) % AES.block_size
        padded = plaintext + (bytes([padding_len]) * padding_len)

        ciphertext = cipher.encrypt(padded)

        payload['encrypt'] = True
        payload['iv'] = b64encode(iv).decode('utf-8')
        payload['data'] = b64encode(ciphertext).decode('utf-8')

        return payload

    def __decrypt(self, payload: dict):

        hash_ = MD5.new()
        hash_.update(self._dev_key.encode('utf-8'))
        key = hash_.digest()

        edata = b64decode(payload['data'])
        iv = b64decode(payload['iv'])

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        data = cipher.decrypt(edata)
        data = data[:-(int(data[-1]))]

        payload["data"] = json.loads(data.decode('utf-8'))
        del (payload["encrypt"])
        del (payload["iv"])

        return payload

    def read_switch_state(self):
        pass  # ONLY AVAILABLE IN DIY MODE


class SonoffBasicDiyApi(SonoffApi):

    def __init__(self, dev_host: str, dev_id: str, dev_key: str, init: bool = True) -> None:
        super().__init__(dev_host, dev_id, dev_key)
        if init:
            self.info()
            logging.info("SONOFF INITIAL CONFIGURATION: READ STATE")
            self.read_switch_state()
            logging.info("CURRENT SONOFF STATE: " + ("ON" if SonoffApi.state == 1 else "OFF"))

    def send(self, url: str, data: dict):
        payload = {
            'deviceid': self._dev_id,
            'data': data
        }
        logging.debug(f"SONOFF POST URL: {url}")
        logging.debug(f"SONOFF POST DATA: {data}")

        try:
            resp = requests.post(url, json=payload, headers={'Connection': 'close'}, timeout=1)
            if resp.json()['error'] != 0:
                raise Exception(f"SONOFF Exception - Error {resp.json()['error']}")
            return resp.json()
        except Exception as ex:
            logging.error(f"SONOFF Exception {ex}")

    def read_switch_state(self):
        url = f"http://{self._dev_host}:{SONOFF_PORT}{SONOFF_INFO_URI}"
        data = {}
        resp = self.send(url, data)
        if resp is not None:
            SonoffApi.state = 1 if resp["data"]["switch"] == "on" else 0
