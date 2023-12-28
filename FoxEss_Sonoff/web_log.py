from collections import deque
from ansi2html import Ansi2HTMLConverter
from flask import Flask, redirect

from FoxEss_Sonoff import main
from FoxEss_Sonoff.sonoff_api import SonoffApi
from FoxEss_Sonoff.settings import WEB_LOG_MAX_LEN

app = Flask(__name__)


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
                </style>
            </head>
            <body>
                <h1>SONOFF BASIC - CURRENT STATE: """ + ("ON" if SonoffApi.state else "OFF") + """</h1>
                <p>
                <div class="flex-parent">
                    <a class="button button-on" href="/switch/on">ON</a>
                    <a class="button button-off" href="/switch/off">OFF</a>
                </div>
                </p>
                <style>
                    ul#console {font-family: "Courier New";padding-left: 5px;text-align: left;color: black;}      
                </style>
                <ul id="console">
                """ + Ansi2HTMLConverter(scheme="ansi2html").convert(tail(main.logFile,WEB_LOG_MAX_LEN)).replace(
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


def tail(filename, n=100):
    with open(filename) as f:
        return str("".join(deque(f, n)))
