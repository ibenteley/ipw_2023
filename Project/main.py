import machine
import time
import ujson
import network
import socket
import math
import urequests as requests
from machine import ADC, Pin
from pimoroni import Buzzer

# UREQUEST DOCUMENTATION


def getTemperature(sensor, type):
    resistance = 10000
    c1 = 1.009249522e-03
    c2 = 2.378405444e-04
    c3 = 2.019202697e-07
    reading = sensor.read_u16()
    R2 = resistance * (65535 / reading - 1.0)
    logR2 = math.log(R2)
    T = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2))
    Tc = T - 273.15
    Tf = (Tc * 9.0) / 5.0 + 32.0
    if type == "c":
        return Tc
    else:
        return Tf


connected_thermistor = ADC(28)
connected_led_red = machine.Pin(0, machine.Pin.OUT)
connected_led_yellow = machine.Pin(1, machine.Pin.OUT)
connected_led_green = machine.Pin(2, machine.Pin.OUT)
buzzer = Buzzer(3)

# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('piton', 'samibagpulanpython')

while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)

ip = wlan.ifconfig()
print(ip[0])

# Initialize the communication over the web
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

City = "Bucharest"
apiKey = "6da6a4bc869047087961b7b0ef15ffcc"

URL = "https://api.openweathermap.org/data/2.5/weather?q=" + City + "&appid=" + apiKey

data = {}

humidity = 0
wind_speed = 0
pressure = 0

r = requests.get(URL)
if r.status_code == 200:
    data = r.json()
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    pressure = data['main']['pressure']

print('!!!Weather received!!!')

c1 = 0
c2 = 0
c3 = 0
c4 = 0
substring1 = "/temperature"
substring2 = "/led_red"
substring3 = "/led_yellow"
substring4 = "/led_green"
substring5 = "/buzzer"

while True:
    time.sleep(2)
    try:
        C1, addr = s.accept()
        print('client connected from', addr)
        # c1_request = c1.recv(4096)
        C1_request = C1.recv(1024)
        try:
            request = str(C1_request)

            if substring1 in request:
                time.sleep(1)
                C1.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                time.sleep(1)
                sent_temp = getTemperature(connected_thermistor, 'c')
                received_humidity = str(humidity)
                city = City
                received_wind = wind_speed
                received_pressure = pressure
                sent_data = {'temperature': sent_temp, 'humidity': received_humidity,
                             'city': City, 'pressure': received_pressure, 'wind': received_wind}
                response_content = ujson.dumps(sent_data)
                C1.send(response_content)
                time.sleep(1)
                C1.close()
            elif substring2 in request:
                C1.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                C1.close()
                if c1 == 0:
                    connected_led_red.high()
                    c1 = 1
                else:
                    connected_led_red.low()
                    c1 = 0
            elif substring3 in request:
                C1.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                C1.close()
                if c2 == 0:
                    connected_led_yellow.high()
                    c2 = 1
                else:
                    connected_led_yellow.low()
                    c2 = 0
            elif substring4 in request:
                C1.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                C1.close()
                if c3 == 0:
                    connected_led_green.high()
                    c3 = 1
                else:
                    connected_led_green.low()
                    c3 = 0
            elif substring5 in request:
                C1.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                C1.close()
                if c4 == 0:
                    buzzer.set_tone(1000)
                    c4 = 1
                else:
                    buzzer.set_tone(0)
                    c4 = 0
            else:
                print('cacamaca')
                C1.send('HTTP/1.0 404 Not Found\r\nContent-type: text/plain\r\n\r\n')
                C1.send('No data found!')
                C1.close()
        except OSError as e:
            print(e)
            C1.close()
    except OSError as e:
        C1.close()
        print('Connection closed')


print("OUT")
