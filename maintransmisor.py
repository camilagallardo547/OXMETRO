from time import sleep
from machine import I2C, Pin, SPI
from utime import ticks_diff, ticks_us
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
from nrf24l01 import NRF24L01 

csn = Pin(5, Pin.OUT) #Pines CSN y CE de la NRF
ce = Pin(17, Pin.OUT)

i2c = I2C(0, sda=Pin(8),scl=Pin(9), freq=100000) #Pines sensor MAX30102	

spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)) # Configuración del bus SPI

nrf = NRF24L01(spi, csn, ce, channel=76, payload_size=16) #Configuracion nrf
address = b'4node'  # Dirección del pipe de transmisión 

nrf.open_tx_pipe(address) # Abrir canal de transmisión

sensor = MAX30102(i2c=i2c)  # Instancia sensor

def leer(): #Funcion para leer los datos del sensor
    sleep(1)
    while True:
            sleep(1)
            sensor.check()
            if sensor.available():
                red_reading = sensor.pop_red_from_storage() #Se lee el residuo de la luz roja
                ir_reading = sensor.pop_ir_from_storage() #Se lee el residuo de la luz infraroja
                float(red_reading) #Se convierten en datos tipo float
                float(ir_reading)
                ratio = red_reading / ir_reading #Se aplica la formula 
                ratio2 = 25 * ratio
                spo2 = 110 - ratio2
                spo2 = spo2 * 1.1
                if red_reading >200: #Si no hay un dedo en el sensor no envia ni imprime nada
                    spo2 = int(spo2) #Se convierte en dato tipo entero para no tener decimales
                    print("Spo2: ",spo2) #Se imprime en la consola
                    spo2 = str(spo2) #Se convierte en dato tipo string para su posterior envio por NRF
                    enviar_mensaje(spo2) #Se llama la funcion para enviar el mensaje
                    sleep(1)

def enviar_mensaje(spo2): #Funcion para enviar el mensaje
    sleep(1)
    try: #Si se puede
        nrf.send(spo2)  #Envia el mensaje
        print("Mensaje enviado: ", spo2) #Se confirma el envio
        estado = nrf.reg_read(0x07)  #se lee el estado del envio
        print("Estado del registro STATUS: ", bin(estado)) #Se muestra el estado del envio
        sleep(2)
        leer() #Vuelve a leer datos
        
    except OSError: #Si no se puede enviar 
        print("Error al enviar el mensaje") #Se confirma la imposibilidad de enviar el mensaje
        sleep(3)
        leer() #vuele a leer datos


def main(): #Funcion main para inicializar el sensor
    if sensor.i2c_address not in i2c.scan():
        print("Sensor not found.") #No se encuentra el sensor
        return
    elif not (sensor.check_part_id()):
        print("I2C device ID not corresponding to MAX30102") #El sensor no es MAX30102 
        return
    else:
        print("Sensor connected and recognized.") #Confirmacion de la conexion con el snsor

    print("Inicializando sensor con configuracion por defecto", '\n')
    sensor.setup_sensor()

    # Frecuencia de las muestras
    sensor.set_sample_rate(50)
    # Promedio de muestras por lectura
    sensor.set_fifo_average(8)
    # Brillo de los leds (R y IR)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    sleep(1)

    # Si se quiere calcular la frecuencia de muestreo
    compute_frequency = True

    print("Starting data acquisition from RED & IR registers...", '\n')
    sleep(1)

    t_start = ticks_us()  # Inicio de tiempo de muestreo
    samples_n = 0  # Numero de muestras obtenidad
    leer() #Leer datos del sensor

if __name__ == '__main__': #Volver a la funcion main
    main()