import asyncio
import aiohttp
import async_timeout
import logging
import hashlib
import time

FOXESS_BASE_URI = "https://www.foxesscloud.com"
FOXESS_DEVICE_URI = "/op/v0/device/list"
FOXESS_REALTIME_URI = "/op/v0/device/real/query"
FOXESS_INVALID_HEADER_PARAM = 40256
FOXESS_INVALID_BODY_PARAM = 40257
FOXESS_OVERLOAD = 40400
FOXESS_TIMEOUT = 30
FOXESS_OK = 0
FOXESS_RETRIES = 5
FOXESS_RETRY_DELAY = 10
FOXESS_HEADER_DATA = {"User-Agent": "Mozilla/5.0", 'lang': 'en'}


class FoxCloudApiClient:

    def __init__(self, fox_apikey: str) -> None:
        self._fox_apikey = fox_apikey
        self._fox_retries = 0
              
    async def _update_signature(self, path: str) -> None:
        FOXESS_HEADER_DATA["token"]=self._fox_apikey
        FOXESS_HEADER_DATA["timestamp"]=str(round(time.time() * 1000))       
        signature = fr'{path}\r\n{FOXESS_HEADER_DATA["token"]}\r\n{FOXESS_HEADER_DATA["timestamp"]}'
        FOXESS_HEADER_DATA["signature"]=hashlib.md5(signature.encode(encoding='UTF-8')).hexdigest()

    async def async_post_data(self, path: str, params: dict) -> dict:
        self._fox_retries = 0
        return await self._post_data(path, params)

   
    async def _post_data(self, path: str, params: dict) -> dict:

        await self._update_signature(path)
        logging.debug(f"FOXESS POST URL: {FOXESS_BASE_URI}{path}")
        logging.debug(f"FOXESS POST DATA: {params}")

        async with async_timeout.timeout(FOXESS_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                response = await session.post(url=FOXESS_BASE_URI+path, json=params, headers=FOXESS_HEADER_DATA)

        await asyncio.sleep(0.5)  # Leave 0.5 second between subsequent Fox calls

        if response.status == 200:           
            result = await response.json(content_type=None)                   
            status = result["errno"]           
            if status == FOXESS_OK:
                return result["result"]
            elif status == FOXESS_INVALID_HEADER_PARAM:
                raise Exception("FOXESS Error - The request header parameters are invalid")
            elif status == FOXESS_INVALID_BODY_PARAM:
                raise Exception("FOXESS Error - The request body parameters are invalid")
            elif status == FOXESS_OVERLOAD and self._fox_retries < FOXESS_RETRIES:              
                self._fox_retries += 1
                sleep_time = self._fox_retries * FOXESS_RETRY_DELAY
                logging.warning(
                    f"FOXESS Overload - The number of requests is too frequent - Retrying {self._fox_retries}/{FOXESS_RETRIES} after {sleep_time}s wait...")
                await asyncio.sleep(sleep_time)
                return await self._post_data(path, params)
            else:
                raise Exception(f"FOXESS Error {status}")
        else:
            raise Exception(f"FOXESS Exception - HTTP Status {response.status}")

    async def realtime_data_query(self, variables: list) -> dict:
        response = await self.async_post_data(FOXESS_REALTIME_URI, {"variables": variables})
        return response
