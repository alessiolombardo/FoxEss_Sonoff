# FoxEss_Sonoff
FoxEss and Sonoff integration to domotize a home appliance

## Overview

This project, entirely written in Python language, allows you to automate the switching on and off of a household appliance via a Sonoff device based on appropriate charging, discharging, feeding and solar production conditions of a FoxESS energy storage solution.

The software currently runs on an [Arietta G25](https://www.acmesystems.it/arietta) appropriately updated with Debian 10 and Python 3.7.

## Getting Started

### Prerequisites

- FoxEss solar inverter with active FoxEss Cloud account
- Sonoff Basic R2 or Basic R3 connected to the power supply of your home appliance
- Python >=3.7.3 (not tested in previous versions)
- Python packages: ``coloredlogs``, ``aiohttp``, ``ansi2html``, ``flask``, ``requests``, ``pycryptodome`` (install them using ``pip3``)

### Configuration

Open **settings.py** and set:
- FoxEss Open API Key (to generate it, go to Foxcloud personal center -> "User profile" -> "API Management")
- Sonoff device ID and device (api) key (to discover them, connect the Sonoff via [Compatible Pairing Mode](https://sonoff.tech/diy-developer/#:~:text=Entering%20the%20Compatible%20Pairing%20Mode,mobile%20phone%20or%20PC) and visits ``http://10.10.7.1/device``)
- Sonoff device type (you can choose ``BASIC_R2``, ``BASIC_R3`` or ``BASIC_R3_DIY``)
- Thresholds of FoxEss values (``FEED_IN_MIN``, ``SOLAR_PROD_MIN``, ``BAT_DISCARGE_MAX``, ``SOC_MIN`` and possible others)

**Note about device type and DIY mode**: At present only Sonoff Basic R2 and Basic R3 are supported but other similar Sonoff devices may work. Sonoff "DIY Mode" allows you to set and read the status of the switches directly via [REST API](https://sonoff.tech/diy-developer/#8). Sonoff Basic R2 doesn't have DIY Mode and it is only possible change the switch state via encrypted communication as shown by [dhanar10](https://github.com/dhanar10/sonoff-basicr2/blob/main/sonoff-basicr2.py). In this case, the Sonoff switch state is inferred by the software logic. If you have a Sonoff Basic R3 it is highly recommended to use ``BASIC_R3_DIY`` as device type to communicate via DIY mode.

Open **main.py** and change your on/off conditions based on data extracted from FoxEss Cloud (see [this document](https://cdck-file-uploads-canada1.s3.dualstack.ca-central-1.amazonaws.com/free1/uploads/ai_speaker/original/2X/5/5e551aef937bf8c456f6ed32375badf2f9a33333.pdf) for details) and your thresholds.
For example:
- Switch off when the battery discharge power is too high or when battery SoC (State of Charge) is too low:
    ```
    if (foxdata["batDischargePower"] > BAT_DISCARGE_MAX or foxdata["SoC"] < SOC_MIN) and sonoff.state == 1:
        sonoff.switch_off()
    ```
- Switch on when the feed in power is enough:
    ```
    if foxdata["feedinPower"] > FEED_IN_MIN and sonoff.state == 0:
        sonoff.switch_on()
	```
- Switch off when the solar production is too low:
    ```
    if foxdata["solarProduction"] < SOLAR_PROD_MIN and sonoff.state == 1:
        sonoff.switch_off()
    ```
    Note 1: ``solarProduction = batChargePower - batDischargePower - gridConsumptionPower + loadsPower + feedinPower``
    Note 2: ``sonoff.state`` indicates the current Sonoff switch state (``0`` is off, ``1`` is on)


### Usage

Execute:
```
python main.py
```
or
```
python3 main.py
```

A simple web application (on port 80) show the log of the application and allows you to manually set the Sonoff switch state.

### Acknowledgements and Sources

- Sonoff Basic non-DIY API and web log: [https://github.com/dhanar10/sonoff-basicr2](https://github.com/dhanar10/sonoff-basicr2)
- FoxEss Cloud Open API: [https://www.foxesscloud.com/public/i18n/en/OpenApiDocument.html](https://www.foxesscloud.com/public/i18n/en/OpenApiDocument.html)

### Testing

- Windows 11, Python 3.12.1
- Windows 10, Python 3.11.7
- Windows 7 x64, Python 3.7.6
- Linux Debian 10 armel on Arietta G25 SoC, Python 3.7.3
- Linux Ubuntu 23.10 LXC on Proxmox VE, Python 3.11.6
