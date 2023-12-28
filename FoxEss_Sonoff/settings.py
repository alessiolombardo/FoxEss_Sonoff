# General settings
LOG_FILENAME = "log.txt"
TIMESTEP = 5  # minutes
WEB_LOG_PORT = 80
WEB_LOG_MAX_LEN = 1000

# FoxEss login settings
foxEssUsername = "USERNAME"
foxEssMd5Password = "00000000000000000000000000000000"  # Md5 encrypted password. Do not insert password in clear text
foxEssDeviceId = "00000000-0000-0000-0000-000000000000"

# Sonoff device settings
sonoffDeviceHost = "192.168.178.46"
sonoffDeviceId = "0000000000"  # In Compatible Pairing Mode visits "http://10.10.7.1/device"
sonoffDeviceKey = "00000000-0000-0000-0000-000000000000"  # In Compatible Pairing Mode, visits "http://10.10.7.1/device"
sonoffDeviceType = "BASIC_R3_DIY"  # Compatible devices: "BASIC_R2", "BASIC_R3" or "BASIC_R3_DIY"

# Foxess thresholds
FEED_IN_MIN = 1.9  # Minimun feed in grid power (kW)
SOLAR_PROD_MIN = 2.1  # Minimun solar production (kW)
BAT_DISCARGE_MAX = 0.2  # Maximum Battery discharge power (kW)
SOC_MIN = 60  # Minimun Battery State of Charge (%)
