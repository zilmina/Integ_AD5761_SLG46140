# spitest.py
# A brief demonstration of the Raspberry Pi SPI interface, using the Sparkfun
# Pi Wedge breakout board and a SparkFun Serial 7 Segment display:
# https://www.sparkfun.com/products/11629
import os
import time
import pigpio
import spidev
import math

pi = pigpio.pi()
pi.set_mode(7, pigpio.OUTPUT) # Counter
pi.set_mode(8, pigpio.OUTPUT) # DAC

pi.set_mode(22, pigpio.OUTPUT)
pi.set_mode(23, pigpio.OUTPUT)
pi.set_mode(24, pigpio.OUTPUT)
pi.set_mode(25, pigpio.INPUT)

pi.write(22, 1)  # set pin#22 to HIGH
pi.write(23, 1)  # set pin#22 to HIGH
pi.write(24, 1)  # set pin#22 to HIGH
time.sleep(0.01)
pi.write(24, 0)  # set pin#22 to HIGH
time.sleep(0.01)
pi.write(24, 1)  # set pin#22 to HIGH

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 0

# Enable SPI
spi = spidev.SpiDev() #

# Open a connection to a specific bus and device (chip select pin)
spi.open(0, 0)
spi.no_cs  = True

# Set SPI speed and mode
spi.max_speed_hz = 50000
spi.mode = 1

# RESET commands
#################################
to_send = [0b00001111, 0x00, 0x00]
pi.write(8, 0)
spi.writebytes(to_send)
pi.write(8, 1)
time.sleep(0.0001)
print("RESET")
# time.sleep(1)

CV	= 0b01
OVR	= 0b0
B2C	= 0b0
ETS	= 0b1
PV	= 0b01
RA	= 0b000
to_send = [0b00000100, 0b00000 << 3 | CV << 1 | OVR, B2C << 7 | ETS << 6 | 0b0 << 5 | PV << 3 | RA]
print("Load Control Register")
pi.write(8, 0)
spi.writebytes(to_send)
pi.write(8, 1)
time.sleep(0.0001)
#################################

time.sleep(1)
# Turn on one segment of each character to show that we can
# address all of the segments
print("START\n")
while 1:

    # Read Count command
    #################################
    pi.write(7, 0)
    result = spi.readbytes(2)
    pi.write(7, 1)
    time.sleep(0.0001)    
    #################################

    # Compute Output
    Vout =10*math.sin((result[1]+result[0]*2**8)/768*2*math.pi)
    print(f"Count: {result[1]+result[0]*2**8:10}, OUTPUT(pm 2LSB = {20/2**16:12.5E} V): {Vout:12.5E} ({Vout-20/2**16:12.5E} - {Vout+20/2**16:12.5E})")

    Vref = 2.5
    C = 4
    M = 8
    N = 16
    D = min(int((Vout/Vref + C)*2**N/M),0xffff)
    byteLowD = D & 0xff
    byteHighD = (D >> 8) & 0xFF
    
    print(f"raw D: {D:5}High D:{hex(byteHighD)}, Low D:{hex(byteLowD)}")

    # Set V out commands
    #################################
    to_send = [0b00000011, byteHighD, byteLowD]
    pi.write(8, 0)
    spi.writebytes(to_send)
    pi.write(8, 1)
    time.sleep(0.0001)
    #################################

    # Pause 
    time.sleep(0.01)


spi.close()
pi.stop()