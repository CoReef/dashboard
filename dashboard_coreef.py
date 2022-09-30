from curses import noraw
import json
import time

from datetime import datetime
from collections import namedtuple

from http.server import BaseHTTPRequestHandler, HTTPServer
# hostName = "127.0.0.1"
hostName = "0.0.0.0"
serverPort = 4343

import crMQTT
# Address of the MQTT server
mqtt_address = '10.42.1.102'
mqtt_port = 1884
mqtt = crMQTT.crMQTT(mqtt_address,mqtt_port)

Entry = namedtuple('Entry','tag last_message timestamp')

entries = {}

def on_message(tag,message):
    entry = Entry(tag,message,datetime.now())
    entries[tag] = entry

epoch_entries = set(['time_utc','date_max_temp','date_min_temp'])

def timespan_description(ts_early,ts_late):
    tsi = int((ts_late - ts_early).total_seconds()/60)
    if tsi == 0:
        return "now"
    elif tsi == 1:
        return "1 minute ago"
    elif tsi < 60:
        return f'{tsi} minutes ago'
    return f'{tsi // 60}h {tsi % 60} minutes ago'
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global entries
        global epoch_entries
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("refresh", "60")
        self.end_headers()
        self.write("<html><head><title>CoReef - Simple Dashboard</title></head>")
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.write("<body>")
        self.write(f'<h2>Aktueller Zeitstempel: {datetime.now().strftime("%d.%m.%Y %H:%M:%S Uhr")}</h2>')
        
        w = 'Wohnzimmer/reading'
        t = 'Terasse/reading'
        s = 'Schlafzimmer/reading'
        if w in entries and t in entries and s in entries:
            wt = entries[w].last_message['Temperature']
            tt = entries[t].last_message['Temperature']
            st = entries[s].last_message['Temperature']
            if tt < wt:
                self.write(f'<p>Draussen ({tt} Celsius) ist es kaelter als im Wohnzimmer ({wt} Celsius). Unten kann gelueftet werden!</p>')
            else:
                self.write(f'<p>Draussen ({tt} Celsius) ist es waermer als im Wohnzimmer ({wt} Celsius). Tuer zu unten!</p>')
            if tt < st:
                self.write(f'<p>Draussen ({tt} Celsius) ist es kaelter als im Schlafzimmer ({st} Celsius). Oben kann gelueftet werden!</p>')
            else:
                self.write(f'<p>Draussen ({tt} Celsius) ist es waermer als im Schlafzimmer ({st} Celsius). Tuer zu oben!</p>')

        now = datetime.now()
        for entry in entries.keys():
            self.write(f'<h3>{entry}</h3>')
            e = entries[entry]
            readings = e.last_message
            self.write('<ul>')
            diff = timespan_description(e.timestamp,now)
            self.write(f'<li>Last message received {e.timestamp.strftime("%d.%m.%Y %H:%M:%S Uhr")} ({diff})</li>')
            for r in readings.keys():
                if r in epoch_entries:
                    diff = timespan_description(datetime.fromtimestamp(readings[r]),now)
                    self.write(f'<li>{r} : {datetime.fromtimestamp(readings[r]).strftime("%d.%m.%Y %H:%M:%S Uhr")} ({diff})</li>')
                else:
                    self.write(f'<li>{r} : {readings[r]}</li>')
            self.write('</ul>')
        self.write("</body></html>")

    def write(self,s):
        self.wfile.write(bytes(s,"utf-8"))

def main():
    print("dashboard started")
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("HTTPServer started")
    mqtt.subscribe('#',on_message)
    print("Connected to MQTT server")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()

if __name__ == '__main__':
    main()
