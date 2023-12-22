#!/usr/bin/env python3

import sys
import os
import asyncio
import time
import logging.config
import coloredlogs
from threading import Thread
from datetime import datetime, timedelta

sys.path.append('../')
from FoxEss_Sonoff.settings import *
from FoxEss_Sonoff import fox_cloud_api, web_log
from FoxEss_Sonoff.sonoff_api import SonoffApi, SonoffModel

sonoffDeviceType = SonoffModel[sonoffDeviceType]
logFile = f"{os.path.dirname(os.path.realpath(__file__))}\\{LOG_FILENAME}"

h_file = logging.FileHandler(logFile)
h_file.setFormatter(coloredlogs.ColoredFormatter(format('%(asctime)s | %(levelname)7s | %(message)s')))
h_stdout = logging.StreamHandler()
logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})
logging.basicConfig(
    handlers=[h_file, h_stdout],
    level=logging.INFO, format='%(asctime)s | %(levelname)7s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

variables = ["loadsPower", "feedinPower", "gridConsumptionPower", "batChargePower", "batDischargePower", "SoC",
             "solarProduction"]


def main():
    cloud_client = fox_cloud_api.FoxCloudApiClient(foxEssUsername, foxEssMd5Password, foxEssDeviceId)
    sonoff = SonoffApi.getsonoff(sonoffDeviceType)

    foxdata = dict({"timestamp": -1}, **{x: -1 for x in variables})

    while True:

        now_minus_5_min = datetime.now() - timedelta(minutes=5)
        query = {
            "deviceId": foxEssDeviceId,
            "variables": variables,
            "timespan": "hour",
            "beginDate": {"year": now_minus_5_min.year, "month": now_minus_5_min.month, "day": now_minus_5_min.day,
                          "hour": now_minus_5_min.hour}
        }

        try:
            response = asyncio.run(cloud_client.raw_query(query))
            for i, _ in enumerate(variables):
                foxdata[variables[i]] = [round(x["value"], 3) for x in response[i]["data"]][-1]
            foxdata["timestamp"] = response[0]["data"][-1]["time"]
            foxdata["solarProduction"] = round(foxdata["batChargePower"] - foxdata["batDischargePower"] - foxdata[
                "gridConsumptionPower"] + foxdata["loadsPower"] + foxdata["feedinPower"], 3)

            logging.info(f"FOXESS LAST DATA: {foxdata}")

            if (foxdata["batDischargePower"] > BAT_DISCARGE_MAX or foxdata["SoC"] < SOC_MIN) and sonoff.state == 1:
                logging.info("CONDITION 1 - SONOFF CHANGE STATE: ON TO OFF")
                sonoff.switch_off()
            elif foxdata["feedinPower"] > FEED_IN_MIN and sonoff.state == 0:
                logging.info("CONDITION 2 - SONOFF CHANGE STATE: OFF TO ON")
                sonoff.switch_on()
            elif foxdata["solarProduction"] < SOLAR_PROD_MIN and sonoff.state == 1:
                logging.info("CONDITION 3 - SONOFF CHANGE STATE: ON TO OFF")
                sonoff.switch_off()

        except Exception as ex:
            logging.error(ex)

        time.sleep(TIMESTEP * 60)

        sonoff.read_switch_state()


def web():
    web_log.app.run(host='0.0.0.0', port='80')


if __name__ == '__main__':
    Thread(target=web).start()
    time.sleep(1)
    Thread(target=main).start()
