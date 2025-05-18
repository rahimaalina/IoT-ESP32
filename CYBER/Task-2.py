from machine import I2C, Pin, ADC
import network
import socket
import ujson as json

# Configure access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-GROUP-08')
ap.config(authmode=3, password='password1')

# Function to convert data to temperature
def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp

# Initialize I2C, button, and potentiometer
i2c = I2C(scl=Pin(22), sda=Pin(23))
btn = Pin(4, Pin.IN)
potentiometer = ADC(Pin(32, Pin.IN))
potentiometer.atten(ADC.ATTN_11DB)

# Socket setup
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Listening on', addr)

while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    cl_file = cl.makefile('rwb', 0)

    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break

    # Generate dictionary with updated values
    data = {
        'Button': btn(),
        'Potentiometer': potentiometer.read(),
        'Temperature': temp_c(i2c.readfrom_mem(24, 5, 2))
    }
    response = json.dumps(data)
    cl.send(response)
    cl.close()
