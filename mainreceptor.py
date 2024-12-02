from machine import Pin, SPI, I2C, SoftI2C, Timer
import utime
from nrf24l01 import NRF24L01  
from ssd1306 import SSD1306_I2C
import socket
import network
import rp2
import ubinascii
import urequests as requests
import time


WIDTH  = 128                                            # oled ancho
HEIGHT = 64                                            # oled alto

i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=200000)       # Inicilizar i2c, pines SCL y SDA
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # oled address
print("I2C Configuration: "+str(i2c))                   # Display I2C configuracion


oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Inicializar OLED

csn = Pin(5, Pin.OUT) #Pines NRF CSN y CE
ce = Pin(17, Pin.OUT)

spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)) # Configuración del bus SPI

nrf = NRF24L01(spi, csn, ce, channel=76, payload_size=16) # Configuración del NRF24L01
address = b'4node'  # Dirección del pipe de recepción 

nrf.open_rx_pipe(0, address) # Abrir canal de recepción

nrf.start_listening() # Poner el módulo en modo de escucha


#def get_html(html_name):
#    with open(html_name, 'r') as file:
#        html = file.read()

def oled_pantalla(mensaje_limpio): #Funcion para poner algo en la OLED
    oled.fill(0)
    oled.text("SpO2",5,8)
    oled.text(mensaje_limpio,45,18) #Muestra el mensaje recibido en la OLED
    oled.show() # Imprime en la OLED
    utime.sleep(1)
 


def recibir_mensaje(): #Funcion para recibir mensajes
    if nrf.any():  # Si hay datos disponibles
        mensaje = nrf.recv()  # Recibe el mensaje
        mensaje_limpio = mensaje.rstrip(b'\x00')  # Elimina los bytes nulos
        print("Mensaje recibido: ", mensaje_limpio) # Imprime en la consola el mensaje
        oled_pantalla(mensaje_limpio) #Llama a la funcion de la OLED


# Ciclo de recepción continuo
while True:
    recibir_mensaje()
    utime.sleep(0.1)  #Delay