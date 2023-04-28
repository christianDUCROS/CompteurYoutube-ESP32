'''
Projet fabriquer-un-compteur-dabonnes-youtube/
ESP32 +  raspberry pi pico W
'''
import time  #tempo
import machine #reset
import parametres #Parametres wifi + lienAPI + horaire
#configuration matrice leds 
import max7219
from machine import Pin, SoftSPI
spi = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
ss = Pin(15, Pin.OUT)
     
screen = max7219.Max7219(64, 8, spi, ss)  #8 matrices d'où 64   + ligne 160
screen.brightness(parametres.luminosite)
#*********************affichage MAX7219************************
screen.fill(0)  #effacer
screen.text('INIT',0,1)
screen.show()
time.sleep(1)

#Configuration wifi STATION
import network
#connexion  wifi qui renvoie une erreur en absence de connexion
wlan_sta = network.WLAN(network.STA_IF)

ssid= parametres.ssid
password= parametres.password

print("Borne wifi : ", ssid)

wlan_sta.active(True)
if wlan_sta.isconnected():
    pass
print('Trying to connect to %s...' % ssid)
wlan_sta.connect(ssid, password)
for retry in range(100):
    connected = wlan_sta.isconnected()
    if connected:
        break
    time.sleep(0.1)
    print('.', end='')
if connected:
    print('\nConnected. Network config: ', wlan_sta.ifconfig())
else:
    print('\nFailed. Not Connected to: ' + ssid)
    #*********************affichage MAX7219************************
    screen.fill(0)  #effacer
    screen.text('Pb WIFI',0,1)
    screen.show()
    #*****************reset****************
    time.sleep(5)
    machine.reset()
    
    
#******************Mise à l'heure******************
import ntptime
import utime
from machine import RTC
rtc = RTC()
if parametres.horaire_ETE_HIVER =='ETE':
    utc_shift = 2
else :
    utc_shift = 1
try:
    # update system time from NTP server
    ntptime.settime()
    print("NTP server query successful.")
    print("System time updated:", utime.localtime())
    #Décalage horaire 
    tm = utime.localtime(utime.mktime(utime.localtime()) + utc_shift*3600)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)  #Format RTC
    rtc.datetime(tm) # Mise à jour de l’heure sur RTC
    print(rtc.datetime())
    temps = rtc.datetime() # get date and time
    temps2 = str(temps[4])+'h'+ str(temps[5])+'min'
    print(temps2)
    #*********************affichage MAX7219 date heure************************
    screen.fill(0)  #effacer
    screen.text(temps2,0,1)
    screen.show()
    #*****************sommeil****************
    time.sleep(1)
except:
    print("NTP server query failed.")
    #*********************affichage MAX7219 date heure************************
    screen.fill(0)  #effacer
    screen.text('Pb Heure',0,1)
    screen.show()
    #*****************reset****************
    time.sleep(5)
    machine.reset()




#***********************************************
    
Pb_API = 0    
start = time.ticks_ms() # get millisecond counter
abonnes = 0 
#******************connexion à google*******************
#***********lecture de l'api et calcul en k************
import ujson
import urequests

def connexion_google() :
    try  : 
        response = urequests.get(parametres.lien_API)
        print(response.text)
        parsed = response.json()
        abonnes = parsed["items"][0]['statistics']['subscriberCount']
        Pb_API = 0
        return (abonnes, Pb_API) 
    except :
        abonnes = 0
        Pb_API = 1 
        return (abonnes, Pb_API) 
    
abonnes, Pb_API = connexion_google()
start = time.ticks_ms() # get millisecond counter
while True :
    delta = time.ticks_diff(time.ticks_ms(), start) # compute time difference
    #***************connexion google toutes les x min****************
    if  delta > 1000*3600*parametres.temps_API : 
        start = time.ticks_ms() # get millisecond counter
        abonnes, Pb_API = connexion_google()
   
    #***********controle horaires  (variable  : fct)*********************
    #***********lecture horaire*******************
    H_debut_split = parametres.H_debut.split(':')
    H_fin_split = parametres.H_fin.split(':')
    
    temps = rtc.datetime()
    print(temps)
    if (temps[4] < int(H_debut_split[0]) or (temps[4]== int(H_debut_split[0]) and temps[5] < int(H_debut_split[1]))) or(temps[4] > int(H_fin_split[0])  or (temps[4] == int(H_fin_split[0]) and temps[5]+1 > int(H_fin_split[1]))) : 
        fct = 0
        time.sleep(1)
    else :
        fct = 1
    print(fct)
    
    if Pb_API == 0 and fct == 1 : #pas de problème API et dans plage horaire
        #*********************affichage MAX7219************************
        screen.fill(0)  #effacer
        #logo youtube
        screen.fill_rect(2,0,10,8,1)
        screen.pixel(2,0,0)  #x=0, y=0  1pour led allumée
        screen.pixel(2,7,0)  #x=0, y=0  1pour led allumée
        screen.pixel(11,0,0)  #x=0, y=0  1pour led allumée
        screen.pixel(11,7,0)  #x=0, y=0  1pour led allumée
        screen.vline(4,1,6,0)
        screen.vline(5,1,6,0)
        screen.vline(6,2,4,0)
        screen.vline(7,2,4,0)
        screen.vline(8,3,2,0)
        screen.vline(9,3,2,0)
        #screen.pixel(63,8,1) #pixel pour la tempo 
        #affichage abonnés
        screen.text(abonnes,64-8*len(abonnes),0,1)  #décaler à droite  8 matrices d'où 64
        screen.show()
        #tempo pour faire clignoter une led en bas à droite
        time.sleep (1)
        #*********************affichage MAX7219************************
        screen.fill(0)  #effacer
        #logo youtube
        screen.fill_rect(2,0,10,8,1)
        screen.pixel(2,0,0)  #x=0, y=0  1pour led allumée
        screen.pixel(2,7,0)  #x=0, y=0  1pour led allumée
        screen.pixel(11,0,0)  #x=0, y=0  1pour led allumée
        screen.pixel(11,7,0)  #x=0, y=0  1pour led allumée
        screen.vline(4,1,6,0)
        screen.vline(5,1,6,0)
        screen.vline(6,2,4,0)
        screen.vline(7,2,4,0)
        screen.vline(8,3,2,0)
        screen.vline(9,3,2,0)
        screen.pixel(0,7,1) #pixel pour la tempo 
        #affichage abonnés
        screen.text(abonnes,64-8*len(abonnes),0,1)  #décaler à droite
        screen.show()
        #tempo pour faire clignoter une led en bas à droite
        time.sleep (1)
    elif Pb_API == 0 and fct == 0 :
        screen.fill(0)  #effacer
        screen.show()
        
    else :
        #*********************affichage MAX7219************************
        screen.fill(0)  #effacer
        screen.text('Pb API',0,1)
        screen.show()
        #*****************reset****************
        time.sleep(5)
        machine.reset()