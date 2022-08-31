import json
import time

from datetime import datetime

from http.server import BaseHTTPRequestHandler, HTTPServer
# hostName = "127.0.0.1"
hostName = "0.0.0.0"
serverPort = 4343

import crMQTT
# Address of the MQTT server
mqtt_address = '10.42.1.102'
mqtt_port = 1884
mqtt = crMQTT.crMQTT(mqtt_address,mqtt_port)

entries = {}

def on_message(tag,message):
    entries[tag] = message

epoch_entries = set(['time_utc','date_max_temp','date_min_temp'])
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
        self.write(f'<h2>Zeitstempel: {datetime.now().strftime("%d.%m.%Y %H:%M:%S Uhr")}</h2>')
        
        w = 'Wohnzimmer/reading'
        t = 'Terasse/reading'
        s = 'Schlafzimmer/reading'
        if w in entries and t in entries and s in entries:
            wt = entries[w]['Temperature']
            tt = entries[t]['Temperature']
            st = entries[s]['Temperature']
            if tt < wt:
                self.write(f'<p>Draussen ({tt} Celsius) ist es kaelter als im Wohnzimmer ({wt} Celsius). Unten kann gelueftet werden!</p>')
            else:
                self.write(f'<p>Draussen ({tt} Celsius) ist es waermer als im Wohnzimmer ({wt} Celsius). Tuer zu unten!</p>')
            if tt < st:
                self.write(f'<p>Draussen ({tt} Celsius) ist es kaelter als im Schlafzimmer ({st} Celsius). Oben kann gelueftet werden!</p>')
            else:
                self.write(f'<p>Draussen ({tt} Celsius) ist es waermer als im Schlafzimmer ({st} Celsius). Tuer zu oben!</p>')

        for entry in entries.keys():
            self.write(f'<h3>{entry}</h3>')
            readings = entries[entry]
            self.write('<ul>')
            for r in readings.keys():
                v = readings[r] if not r in epoch_entries else datetime.fromtimestamp(readings[r]).strftime("%d.%m.%Y %H:%M Uhr (%Ss)")
                self.write(f'<li>{r} : {v}</li>')
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
