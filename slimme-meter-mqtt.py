#!/usr/bin/env python
# Python script om P1 telegram weer te geven

import datetime
import re
import serial
import paho.mqtt.client as paho

#broker="controller.local"
#port=1883

def on_publish(client,userdata,result): #create function for callback
  print("data published \n")
  pass

#client1=paho.Client("control1") #create client object
#client1.on_publish = on_publish #assign function to callback
#client1.connect(broker,port) #establish connection

# Seriele poort confguratie
ser = serial.Serial()

# DSMR 2.2 > 9600 7E1:
ser.baudrate = 9600
ser.bytesize = serial.SEVENBITS
ser.parity = serial.PARITY_EVEN
ser.stopbits = serial.STOPBITS_ONE

# DSMR 4.0/4.2 > 115200 8N1:
#ser.baudrate = 115200
#ser.bytesize = serial.EIGHTBITS
#ser.parity = serial.PARITY_NONE
#ser.stopbits = serial.STOPBITS_ONE

ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = "/dev/ttyUSB0"
ser.close()

kwhtot = 0
kwhoud = 0
kwhverschil = 0

gastot = 0
gasoud = 0
gasverschil = 0

# Telegram
# 
# /KMP5 KA6U001660740912
# 
# 0-0:96.1.1(204B413655303031363630373430393132)
# 1-0:1.8.1(13629.373*kWh)
# 1-0:1.8.2(14700.866*kWh)
# 1-0:2.8.1(00000.000*kWh)
# 1-0:2.8.2(00000.000*kWh)
# 0-0:96.14.0(0001)
# 1-0:1.7.0(0000.64*kW)
# 1-0:2.7.0(0000.00*kW)
# 0-0:96.13.1()
# 0-0:96.13.0()
# 0-1:24.1.0(3)
# 0-1:96.1.0(3238313031353431303037343732343132)
# 0-1:24.3.0(180428140000)(08)(60)(1)(0-1:24.2.1)(m3)
# (03862.650)
# !

while True:
  ser.open()
  checksum_found = False
  gasflag = 0

  while not checksum_found:
    telegram_line = ser.readline() # Lees een seriele lijn in.
    telegram_line = telegram_line.decode('ascii').strip() # Strip spaties en blanke regels

    print (telegram_line) #debug

#    if re.match(b'(?=1-0:1.7.0)', telegram_line): #1-0:1.7.0 = Actueel verbruik in kW
      # 1-0:1.7.0(0000.54*kW)
#      kw = telegram_line[10:-4] # Knip het kW gedeelte eruit (0000.54)
#      watt = float(kw) * 1000 # vermengvuldig met 1000 voor conversie naar Watt (540.0)
#      watt = int(watt) # rond float af naar heel getal (540)

#    if re.match(b'(?=1-0:1.8.1)', telegram_line): #1-0:1.8.1 - Hoog tarief / 1-0:1.8.1(13579.595*kWh)
#      kwh1 = telegram_line[10:-5] # Knip het kWh gedeelte eruit (13579.595)

#    if re.match(b'(?=1-0:1.8.2)', telegram_line): #1-0:1.8.2 - Laag tarief / 1-0:1.8.2(14655.223*kWh)
#      kwh2 = telegram_line[10:-5] # Knip het kWh gedeelte eruit (14655.223)

#    if gasflag == 1:
#      gas = telegram_line[1:-1]
#      gasflag = 0
   
#    if re.match(b'(?=0-1:24.3.0)', telegram_line): #0-1:24.3.0 - Gasverbruik
#      gasflag = 1

    # Check wanneer het uitroepteken ontavangen wordt (einde telegram)
#    if re.match(b'(?=!)', telegram_line):
#      checksum_found = True

  ser.close()

#######################################
  if kwhoud < 1: #Script eerste keer opgestart, sla waarde op
    kwhoud = kwhtot

  kwhtot = float(kwh1) + float(kwh2)
  kwhverschil = round(float(kwhtot) - float(kwhoud), 3)

  if gasoud < 1: #Script eerste keer opgestart, sla waarde op
    gasoud = gas
    gasouduur = gas

  gasverschil = round(float(gas) - float(gasoud), 3)
  gasverschiluur = round(float(gas) - float(gasouduur), 3)

# Reset tellers

  tijd = str(datetime.datetime.now().time())[0:-10]
  tijdmin = str(datetime.datetime.now().time())[3:-10]

  if tijd == "00:00": # Reset de counter van de dag
    kwhoud = kwhtot
    gasoud = gas

  if tijdmin == "00": # Reset de counter van het uur
    gasouduur = gas

######################################
# MQTT PUBLISH
######################################

#  client1.publish("elektra\w", watt)
#  client1.publish("elektra\kwh", kwhverschil)
#  client1.publish("gas", gasverschil)
#  client1.publish("gas\uur", gasverschiluur)