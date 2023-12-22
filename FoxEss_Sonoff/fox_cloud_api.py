import asyncio
import aiohttp
import async_timeout
import logging

FOXESS_BASE_URI = "https://www.foxesscloud.com/c/v0"
FOXESS_DEVICE_URI = "/device/list"
FOXESS_RAW_URI = "/device/history/raw"
FOXESS_LOGIN_URI = "/user/login"
FOXESS_TIMEOUT = 30
FOXESS_OK = 0
FOXESS_INVALID_TOKEN_ERR = 41808
FOXESS_TIMEOUT_ERR = 41203
FOXESS_RETRIES = 5
FOXESS_RETRY_DELAY = 10
FOXESS_HEADER_DATA = {"User-Agent": "Mozilla/5.0"}


class FoxCloudApiClient:

    def __init__(self, fox_username: str, fox_password: str, fox_device_id: str) -> None:
        self._token = None
        self._fox_username = fox_username
        self._fox_password = fox_password
        self._fox_device_id = fox_device_id
        self._fox_retries = 0

    async def _refresh_token(self) -> None:
        result = await self._post_data(f"{FOXESS_BASE_URI}{FOXESS_LOGIN_URI}",
                                       {"user": self._fox_username, "password": self._fox_password})
        self._token = result["token"]

    async def async_post_data(self, url: str, params: dict) -> dict:
        self._fox_retries = 0
        if self._token is None:
            await self._refresh_token()
        return await self._post_data(url, params)

    async def _post_data(self, url: str, params: dict) -> dict:
        if self._token is not None:
            FOXESS_HEADER_DATA["token"] = self._token

        logging.debug(f"FOXESS POST URL: {url}")
        logging.debug(f"FOXESS POST DATA: {params}")
        async with async_timeout.timeout(FOXESS_TIMEOUT):

            async with async_timeout.timeout(FOXESS_TIMEOUT):
                async with aiohttp.ClientSession() as session:
                    if url == f"{FOXESS_BASE_URI}{FOXESS_LOGIN_URI}":
                        response = await session.post(url,
                                                      data="user=" + self._fox_username + "&password=" +
                                                           self._fox_password, headers=FOXESS_HEADER_DATA)
                    else:
                        response = await session.post(url, json=params, headers=FOXESS_HEADER_DATA)

        await asyncio.sleep(0.5)  # Leave 0.5 second between subsequent Fox calls

        if response.status == 200:
            result = await response.json(content_type=None)
            status = result["errno"]
            if status == FOXESS_OK:
                return result["result"]
            elif status == FOXESS_INVALID_TOKEN_ERR:
                logging.info("FOXESS Token has expired - Refreshing...")
                await self._refresh_token()
                return await self._post_data(url, params)
            elif status == FOXESS_TIMEOUT_ERR and self._fox_retries < FOXESS_RETRIES:
                self._fox_retries += 1
                sleep_time = self._fox_retries * FOXESS_RETRY_DELAY
                logging.warning(
                    f"FOXESS Timeout - Retrying {self._fox_retries}/{FOXESS_RETRIES} after {sleep_time}s wait...")
                await asyncio.sleep(sleep_time)
                return await self._post_data(url, params)
            else:
                self._token = None
                raise Exception(f"FOXESS Exception - Error {status}")
        else:
            raise Exception(f"FOXESS Exception - HTTP Status {response.status}")

    async def device_info(self) -> None:
        device = await self.async_post_data(
            f"{FOXESS_BASE_URI}{FOXESS_DEVICE_URI}", {
                "pagesize": 10,
                "currentPage": 1,
                "total": 0,
                "condition": {"queryDate": {"begin": 0, "end": 0}},
            }
        )
        logging.info(device)

    async def raw_query(self, data: dict) -> dict:
        response = await self.async_post_data(f"{FOXESS_BASE_URI}{FOXESS_RAW_URI}", data)
        return response
