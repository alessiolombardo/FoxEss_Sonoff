from collections import deque
from ansi2html import Ansi2HTMLConverter
from flask import Flask, redirect, send_from_directory
from datetime import datetime

from FoxEss_Sonoff import main
from FoxEss_Sonoff.sonoff_api import SonoffApi
from FoxEss_Sonoff.settings import WEB_LOG_MAX_LEN

app = Flask(__name__)

foxdata = dict({"timestamp":-1}, **{x:-1 for x in main.variables})


@app.route('/')
def web():

    return """
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
                <style>
                    html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
                    body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;}
                    h3 {color: #444444;margin-bottom: 50px;}
                    .button {display: block;width: 80px;background-color: #1abc9c;border: none;color: white;
                    padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;
                    border-radius: 4px;}
                    .button-on {background-color: #1abc9c;}
                    .button-on:active {background-color: #16a085;}
                    .button-off {background-color: #34495e;}
                    .button-off:active {background-color: #2c3e50;}
                    .flex-parent {display: flex;}
                    p {font-size: 14px;margin-bottom: 10px;}
                    table, th, td {font-size: 14px; border:1px solid black;border-collapse:collapse;padding: 5px;margin-left:auto;margin-right:auto;font-weight:bold;}
                </style>
                
            </head>
            <body>
                <h1>SONOFF BASIC</h1>
                <b>CURRENT STATE: """ + ("ON" if SonoffApi.state else "OFF") + """</b>
                <div class="flex-parent">
                    <a class="button button-on" href="/switch/on">ON</a>
                    <a class="button button-off" href="/switch/off">OFF</a>
                </div>
                <hr>
                <h1>FOXESS</h1>
                <table>
                    <tr>
                        <td>LAST UPDATE</td>
                        <td>""" + f"{timestamp()}" + """</td>
                    </tr>
                    <tr>
                        <td>SOLAR PRODUCTION</td>
                        <td>""" + f"{foxdata['solarProduction']}" + """</td>
                    </tr>
                    <tr>
                        <td>LOADS POWER</td>
                        <td>""" + f"{foxdata['loadsPower']}" + """</td>
                    </tr>
                    <tr>
                        <td>FEED-IN POWER</td>
                        <td>""" + f"{foxdata['feedinPower']}" + """</td>
                    </tr>
                    <tr>
                        <td>GRID CONSUMPTION POWER</td>
                        <td>""" + f"{foxdata['gridConsumptionPower']}" + """</td>
                    </tr>
                    <tr>
                        <td>BATTERY CHARGE</td>
                        <td>""" + f"{foxdata['batChargePower']}" + """</td>
                    </tr>
                    <tr>
                        <td>BATTERY DISCHARGE</td>
                        <td>""" + f"{foxdata['batDischargePower']}" + """</td>
                    </tr>
                    <tr>
                        <td>BATTERY STATE OF CHARGE</td>
                        <td>""" + f"{foxdata['SoC']}" + """</td>
                    </tr>
                </table>
                </br>
                <hr>
                <h1>LOG</h1>
                <style>
                    ul#console {font-family: "Courier New";padding-left: 5px;text-align: left;color: black;}      
                </style>
                <ul id="console">
                """ + Ansi2HTMLConverter(scheme="ansi2html").convert(tail(main.logFile, WEB_LOG_MAX_LEN)).replace(
                    "class=\"body_foreground body_background\"", "") + """
                <ul>
            </body>
        </html>"""


@app.route('/switch/on')
def switch_on():
    sonoff = SonoffApi.getsonoff(main.sonoffDeviceType, init=False)
    sonoff.switch_on()
    return redirect("/")


@app.route('/switch/off')
def switch_off():
    sonoff = SonoffApi.getsonoff(main.sonoffDeviceType, init=False)
    sonoff.switch_off()
    return redirect("/")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def timestamp():
    if type(foxdata['timestamp']) is int:
        return "NOT CONNECTED"
    else: 
        return datetime.strptime(foxdata['timestamp'].rsplit(' ', 1)[0], format('%Y-%m-%d %H:%M:%S')).strftime('%d/%m/%Y %H:%M:%S')


def tail(filename, n=100):
    with open(filename) as f:
        return str("".join(deque(f, n)))
