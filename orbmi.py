import time
from thread import *
import RPi.GPIO as GPIO

import pygame
from message_manager import *
from message_queue import *
import serial
import RPi.GPIO as GPIO
from unipath import Path

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = Path(BASE_DIR).child('audio_output')

os.chdir(OUTPUT_DIR)
with open('player_status.json',"w") as f:           
    json.dump({'status':0}, f)
    f.close()   

print ("updating messages")
a = message_manager()
print ("messages updated")
mq = message_queue()




ser = serial.Serial('/dev/ttyAMA0', 19200, timeout=1)



pygame.mixer.init()
start_new_thread(a.update_loop,())

print ("Init")

mq.queued_filename = 0



def set_color(value):

    value = value.lstrip('#')
    lv = len(value)
    y = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    red=y[0]
    grn=y[1]
    blu=y[2]

    color_to_write = str(red) + " " + str(grn) + " " + str(blu) + " 0\n"
    print (color_to_write)
    ser.write(color_to_write)



while True:

    
    serread = ser.readline()
    print ("top of while")
    print (serread)
    print mq.check_alert_new_messages()
    #if mq.check_alert_new_messages():
        # loop through the colors of the new messages
	
 	#print mq.color_queue()
	#set_color(mq.color_queue())
	
        #mq.load_stored_message_json()
        #mq.silence_alert_new_messages()

    if serread is '2' or serread is '3' or (mq.queued_filename != 0 and mq.queued_filename != "no new messages"):
        print (serread)
        start = time.time()	
        #update status file to playing
        if serread is '3':
            mq.queue_previous()
        else:
            mq.queue_next()

        serread = ""

        print (mq.queued_filename)

        if(mq.queued_filename != 0 and mq.queued_filename != "no new messages" and mq.queued_filename != "start of queue"):
            pygame.mixer.music.load(mq.queued_filename)
            set_color(mq.queued_color)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():

                press = ser.readline()                
                print (press)
                print (len(press))
                timer = time.time()
                
                if press == '2':
                    print ("play next message")
                    pygame.mixer.music.stop()
                    start = time.time() 
                    mq.queue_next()
                    if mq.queued_filename == "no new messages":
                        break
                    pygame.mixer.music.load(mq.queued_filename)
                    set_color(mq.queued_color)
                    pygame.mixer.music.play()                
                       
                if press == '4':
                    pygame.mixer.music.stop()
                    mq.set_status_json_to_stopped()
                    ser.write("255 0 0 1\n")
                    mq.queued_filename = 0
                    break

                if ((timer-start)>=8) & (press is '3'):
                    print ("replay current message")
                    pygame.mixer.music.stop()
                    start = time.time() 
                    pygame.mixer.music.rewind()
                    pygame.mixer.music.play()
                    press = 2   
                    
                if ((timer-start)<8) & (press is '3'):
                    print ("play previous message")
                    pygame.mixer.music.stop()
                    start = time.time() 
                    mq.queue_previous()
                    if mq.queued_filename == "start of queue":
                        pygame.mixer.music.stop()
                        start = time.time() 
                        pygame.mixer.music.rewind()
                        pygame.mixer.music.play()

                    pygame.mixer.music.load(mq.queued_filename)
                    set_color(mq.queued_color)
                    pygame.mixer.music.play()    
    
            print ("end of while")
            
        if mq.queued_filename == "no new messages":
            print ("in no new messages statement")
            ser.write("0 0 0 0\n")


            mq.queued_filename = 0
            mq.set_status_json_to_stopped()
            
