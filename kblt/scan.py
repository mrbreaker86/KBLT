#!/usr/bin/python

#from picamera.array import PiRGBArray
#from picamera import PiCamera
import cv2
#import imutils
from time import sleep, time, time
import time
import datetime
import PIL.Image
import RPi.GPIO as GPIO
import os
from sys import exit
import numpy as np
import pandas as pd
from pygame import mixer

####### packages needed for the email service ####
import smtplib

####### packages needed for connecting to samba server for storage of the files ####
#import smb
#from smb.SMBConnection import SMBConnection
#import tempfile

####### attach images to emails
#from email.MIMEImage import MIMEImage

####### package for threading
import threading

####### copy files
#from shutil import copyfile
import shutil

import tifffile as tiff
from tifffile import imsave

emergency_stop = False

#global lightson
lightson = False

stageon = False
transon = False

#global no_flats
#global no_darks
#global tomo_reps
no_flats = 10
no_darks = 10

global sample_name_text
#global lang
lang = "English f"

def setlang(language):
    global lang
    lang = language
    print('Language set: ' + language)

def printparam(sample_name_text):
    print(sample_name_text)

def AudioMessage(lang):

    """
    Set the language of the warning message. The input is just a string, e.g. "English f" or "English m", where f and m stand for female and male voice, respectively.
    
    Pre-recorded mp3 audio files are read in and played for the user via the speakers.
    
    Note: Personal audio files in any given language can be recorded with e.g. Windows Voice Recorder and saved down in m4a format.
    m4a files can then be conerted to mp3 format using the pydub package. For more info please see: https://pypi.org/project/pydub/

    Parameters
    ----------
    lang : text
        lang string
     
    """
    mixer.init()
    #audio_path = '/home/pi/KBLT_scanner/audio/mp3/'
    audio_path = os.path.join(os.path.dirname(__file__), '..', 'audio/mp3/')
    audio_path = audio_path + lang + '.mp3'
    print(audio_path)
    mixer.music.load(audio_path)
    mixer.music.play()
    #sleep(5)
    print("Audio message done!")

def emergencyThread():
        try:
                #global t3
                t3 = threading.Thread(name="Hello5", target=emergency())
                t3.start()
                
        except KeyboardInterrupt:
                close()
        except:
                print("Error with Emergency button Thread! Event ignored!")

def emergency():
        try:
                global emergency_stop

                print("The Emergency Button has been pressed! Stopping all active motors.")
                emergency_stop = True
                GPIO.cleanup()

                print("Emergency Button will be automatically released in 5 seconds!")
                for x in range(5):
                        sleep(x)
                        print("...")
                        
                emergency_stop = False
                print("Emergency Button automatically released! All motors can now be used.")

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Emergency button! Event ignored!")

def relay_switch_trans(send, pinact, pininact2, pininact3, pininact4):
        try:
                #pins connected to the 8 relay channel 8 module
                pinsact = [pinact, pininact2, pininact3, pininact4]
                GPIO.setmode(GPIO.BCM)
                #GPIO.setup(pinact, GPIO.OUT)
                for i in pinsact:
                        GPIO.setup(i, GPIO.OUT)
                
                global transon
    
                #turn on
                if send is True and transon is False:
                        #inactivate all first (just to be sure), in case a GPIO pin would be on due to OS dependent issues.
                        for i in pinsact[1:4]:
                                GPIO.output(i, GPIO.LOW)
                                print("...")
                                sleep(0.51)
                        #activate the given relay
                        GPIO.output(pinsact[0], GPIO.HIGH)
                        sleep(0.51)
                        print("...")
                        #inform other functions that translation stage is on
                        transon = True
                        print("The given translation motor is ON!")
                elif send is True and transon is True:
                        print("A translation motor  is already ON! Please turn OFF before switching motor!")
                elif send is False:# and transon is True:
													 
								  
									
                        #inactivate all (just to be sure)
                        for i in pinsact[0:4]:
                                GPIO.output(i, GPIO.LOW)
                                print("...")
                                sleep(0.51)
                        #inform other functions that translation stage is off
                        transon = False
                        print("All translation motors are OFF!")
                #elif send is False and transon is False:
                #        print("Translation stage is already OFF!")

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Relay for translation stage! Event ignored!")

def relay_switch(send):
        try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(24, GPIO.OUT)

                #print(lightson)

                global lightson

                #turn on and off quickly
                if send is True and lightson is False:
                        AudioMessage(lang)
                        GPIO.output(24, GPIO.HIGH)
                        sleep(0.51)
                        print("...")
                        GPIO.output(24, GPIO.LOW)
                        sleep(0.51)
                        #inform other functions that light is on
                        lightson = True
                        print("Light is ON!")
                        #aqcuire 20 projection images to make sure that the camera adjusts to the lightning conditions
                        for x in range(20):
                                rettest, frametest = cap.read()
                                sleep(delay)
                        print("Camera adjusted to correct lightning conditions!")
                elif send is True and lightson is True:
                        print("Light is already ON!")
                elif send is False and lightson is True:
                        buttonpress = 3
                        for x in range(buttonpress):
                                GPIO.output(24, GPIO.HIGH)
                                sleep(0.51)
                                print("...")
                                GPIO.output(24, GPIO.LOW)
                                sleep(0.51)
                                print("...")
                        #inform other functions that light is off
                        lightson = False
                        print("Light is OFF!")
                elif send is False and lightson is False:
                        print("Light is already OFF!")

        except KeyboardInterrupt:
                close()
        #except:
        #        print("Please select language first, in order to turn ON the lamp!")

def relay_switch_manual():
        try:
                global lightson
                
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(24, GPIO.OUT)

                GPIO.output(24, GPIO.HIGH)
                sleep(0.51)
                print("...")
                GPIO.output(24, GPIO.LOW)
                sleep(0.51)
                print("Resetting the Light!")
                lightson = False

        except KeyboardInterrupt:
                close()
        except:
                print("Error with manually resetting the Light via the Relay! Event ignored!")

def iot_switch(send):
        try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(17, GPIO.OUT)

                global stageon

                #turn switch and rotation stage on
                if send is True and stageon is False:
                        GPIO.output(17, GPIO.HIGH)
                        sleep(0.01)
                        #inform other functions that the stage is on
                        stageon = True
                        print("Rotation stage is ON!")
                elif send is True and stageon is True:
                        print("Rotation stage is already ON!")
                elif send is False and stageon is True:
                        GPIO.output(17, GPIO.LOW)
                        sleep(0.01)
                        #inform other functions that the stage is off
                        stageon = False
                        print("Rotation stage is OFF!")
                elif send is False and stageon is False:
                        print("Rotation stage is already OFF!")                      

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Switch! Event ignored! Please turn the stage ON first!")

led_port = int(22)

def led_blinking_green(c):

    """
    An LED light connected to the given port number on the GPIO board will blink when this function is called from a loop.

    Parameters
    ----------
    led_port : int
        led_port integer
     
    """

    try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(led_port, GPIO.OUT)

            GPIO.output(led_port, GPIO.HIGH)
            sleep(0.01)
            GPIO.output(led_port, GPIO.LOW)
            sleep(0.01)
    except KeyboardInterrupt:
            close()
    except:
            print("Error with LED Blinking! Event ignored!")
            #close()

def led_onoff_green(ledpower, led_port):

    """
    An LED light connected to the given port number on the GPIO board will turn on or off when this function is called.
    We turned on the LED will have a solid light. The LED is turned on and off using the ledpower parameter which can be set to either True (on) or False (off).

    Parameters
    ----------
    led_port : int
        led_port integer
    ledpower : boolean
        ledpower boolean    
     
    """

    try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(led_port, GPIO.OUT)

            if ledpower is True:
                    GPIO.output(led_port, GPIO.HIGH)
                    sleep(0.01)
            elif ledpower is False:
                    GPIO.output(led_port, GPIO.LOW)
                    sleep(0.01)
    except KeyboardInterrupt:
            close()
    except:
            print("Error with LED Blinking! Event ignored!")
            #close()
 
def Initiate_new_scan(manual_sample_name):

        try:
                localtime = time.localtime(time.time())
                #save the files in the following folder
                global sample_folder_date
                sample_folder_date = str("%04d" % (localtime.tm_year,)) + str("%02d" % (localtime.tm_mon, )) + str("%02d" % (localtime.tm_mday,))
                print(sample_folder_date)

                global sample_folder

                sample_folder = '/home/pi/KBLT/raw/' + sample_folder_date + '/' + manual_sample_name
                if not os.path.exists(sample_folder):
                        os.makedirs(sample_folder)

        except KeyboardInterrupt:
                close()
        except:
                print("Error with creating new sample folder! Exiting program.")
                close()

def TranslationStageThread(direction, trans_step):
        try:
                #global t2
                t2 = threading.Thread(name="Hello2", target=Initiate_translation_stage(direction, trans_step))
                t2.start()

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Threading for the Translation Stage! Exiting program!")
                close()

#COMMAND IN TERMINAL: pinout
#GPIO26 - PIN37
#GPIO19 - PIN35
#GPIO6 - PIN31
#GPIO5 - PIN29  
GPIOno_trans_on = [26,0,11,9]
GPIOno_trans_off = [9,11,0,26]           

def Initiate_translation_stage(direction, trans_step, GPIOno_trans_on, GPIOno_trans_off):

    """
    Initiates the translation stages using the relay board, using 4 different inputs.
    
    Direction is either True or False depending on the direction of the rotation of the given stepper motor.

    Translation steps defines the total lenght of travel in cm.
    
    GPIOno_trans_on and GPIOno_trans_off contain 4 given port numbers on the GPIO board connected to a given stepper motor via the relay board.

    Parameters
    ----------
    direction : boolean
        direction boolean

    trans_step : boolean
        trans_step boolean
        
    GPIOno_trans_on : ndarray
        GPIOno_trans_on ndarray
    
    GPIOno_trans_off : ndarray
        GPIOno_trans_off ndarray
     
    """

    try:
            #global emergency_stop
            #emergency_stop = False
            
            #GPIO.setmode(GPIO.BOARD)
            GPIO.setmode(GPIO.BCM)
            
            #go front
            if direction is True:
                    GPIOno = GPIOno_trans_on
            #go back
            elif direction is False:
                    GPIOno = GPIOno_trans_off

            for no in GPIOno:
                    GPIO.setup(no,GPIO.OUT)
                    GPIO.output(no,0)
                   
            seq = [ [1,0,0,0],
                    [1,1,0,0],
                    [0,1,0,0],
                    [0,1,1,0],
                    [0,0,1,0],
                    [0,0,1,1],
                    [0,0,0,1],
                    [1,0,0,1] ]

            #8 x 64 = 512 (one  row!), 2 rows 1024
            for i in range(int(trans_step)):
                    if i % 5 == 0:
                            led_blinking_green() 
                    for halfstep in range(8):
                            for no in range(4):
                                    GPIO.output(GPIOno[no], seq[halfstep][no])
                                    if emergency_stop is True:
                                            print("Emergency button pressed! Translation motor stopped!")
                                            break
                            time.sleep(0.001)

            #GPIO.cleanup()

    except KeyboardInterrupt:
            close()
    except:
            print("Error with initiating the translation stage! Exiting program.")
            close()

def Initiate_rotation_stage(scan_mode, no_projections):

    """
    Initiates the rotation stage.

    Scan mode accepts the following integer values 1, 2, 4, 8, 16, and 32.

    No. projections is usually set to 200 over 360 degrees.
    By using 200 projections and scan mode 1, the angular step over 360 degrees is 1.8 degrees per projection.
    By using 200 projections and scan mode 2, the angular step over 360 degrees is 0.9 degrees per projection, which in turn results in 400 projections over 360 degrees.

    Parameters
    ----------
    scan_mode: accepts the following integer values 1, 2, 4, 8, 16, and 32.
        scan mode integer
    no_projections: usually set to 200 over 360 degrees.
        no_projections integer
    SPR : Steps per revolution over 360 degrees
        SPR integer
    
    
    
    """

    try:
            global DIR
            global STEP
            global CW
            global CCW
            DIR = 20 # Direction GPIO Pin
            STEP = 21 # Step GPIO Pin
            CW = 1 # Clockwise Rotation
            CCW = 0 # Couterclockwise Rotation
            SPR = no_projections #200 #48 # Steps per Revolution (360 / 7.5)

            global GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(DIR, GPIO.OUT)
            GPIO.setup(STEP, GPIO.OUT)

            MODE = (13, 16, 18) #Microstep Resolution GPIO Pins
            GPIO.setup(MODE, GPIO.OUT)
            RESOLUTION = {'Full': (0,0,0),
                          'Half': (1,0,0),
                          '1/4': (0,1,0),
                          '1/8': (1,1,0),
                          '1/16': (0,0,1),
                          '1/32': (1,0,1)}

            if scan_mode == 1:
                    GPIO.output(MODE, RESOLUTION['Full'])
                    no_step = 1

            if scan_mode == 2:
                    GPIO.output(MODE, RESOLUTION['Half'])
                    no_step = 2

            if scan_mode == 4:
                    GPIO.output(MODE, RESOLUTION['1/4'])
                    no_step = 4

            if scan_mode == 8:
                    GPIO.output(MODE, RESOLUTION['1/8'])
                    no_step = 8

            if scan_mode == 32:
                    GPIO.output(MODE, RESOLUTION['1/32'])
                    no_step = 32

            global step_count
            global delay

            step_count = int(SPR * no_step)
            delay = 0.0208 / no_step

            print("Set no. projections: " + str(no_projections))
            print("Scan mode: " + str(scan_mode))
            print("No steps: " + str(no_step))
            print("SPR: " + str(SPR))
            print("step count: " + str(step_count))
            
            proj_skip = round(200/step_count)
            
            return proj_skip
            
            #print("Rotation stage initiated!")
    except KeyboardInterrupt:
            close()
    except:
            print("Error with initiating the rotation stage! Exiting program.")
            close()

def Rotate90deg(step_count, direction):
        try:
                #Turn Rotate Stage ON if OFF
                if stageon is False:
                        print("Rotation stage was OFF. Now turning it back ON!")
                        iot_switch(send = True)
                        sleep(3)

                #Set rotation parameters, scan mode changes:
                proj_skip = Initiate_rotation_stage(scan_mode = 4, no_projections=800)
                #proj_skip = Initiate_rotation_stage(scan_mode = 1, no_projections=200)

                #CW = 1 # Clockwise Rotation
                #CCW = 0 # Couterclockwise Rotation
                if direction == 1:
                        GPIO.output(DIR, CW)                    
                elif direction == 0:
                        GPIO.output(DIR, CCW)
                
                for x in range(step_count):
                        GPIO.output(STEP, GPIO.HIGH)
                        #normal delay needed for light samples. scan mode 4 or 1
                        sleep(delay)
                        #long delay needed for high torque for heavy samples, to avoid backlash. scan mode 1.
                        #sleep(0.2)
                        GPIO.output(STEP, GPIO.LOW)
                        if x % 10 == 0:
                                led_blinking_green()                        
                        
        except KeyboardInterrupt:
                close()
        except:
                print("Error with rotating the rotation stage! Exiting program.")
                close()
           
def CamAreaOnThread(x0, xw, y0, yh):
        try:
                global t1
                t1 = threading.Thread(name="Hello", target=lambda: CamAreaCheck(x0, xw, y0, yh))
                t1.start()
        except KeyboardInterrupt:
                #time.sleep(2)
                #t1.raise_exception() 
                #t1.join()
                close()
        except:
                print("Error with Threading for the web camera! Exiting program!")
                #t1.raise_exception() 
                #t1.join()
                close()

def PiCamOnThread():
        try:
                global t2
                t2 = threading.Thread(name="Hello3", target=PiCamCheck)
                t2.start()
                #sleep(10)
                #t2.join(None)
                #print("just closed the camera thread!")
        except KeyboardInterrupt:
                #t2.join(None)
                close()
        except:
                print("Error with Threading for the Pi camera! Exiting program!")
                #t2.join(None)
                close()

def CamInit(cam_no, x_res, y_res):
        try:
                global cap
                cap = cv2.VideoCapture(cam_no)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, x_res)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y_res)
                cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))

                print("Camera initiated!")
                
        except KeyboardInterrupt:
                close()
        except:
                print("Error with initiating the camera! Exiting program!")
                close()
    
def CamAreaCheck(x0, xw, y0, yh):
        try:
                #Initiate web camera
                #set cam no to either 0 or 1 etc. depending on which port the USB or piwebcam is using
                CamInit(cam_no=0, x_res=720, y_res=480)

                print("camera coordinates", y0,yh,x0,xw)
                print("Is the camera thread on or off?", t1.is_alive())
               
                while(True):
                    # Capture frame-by-frame
                    vret, vframe = cap.read()
                    vframe = vframe[y0:yh, x0:xw]

                    # Our operations on the frame come here.
                    # If used, changes the frame from color to black and white. 
                    #vframe = cv2.cvtColor(vframe, cv2.COLOR_BGR2GRAY)
                    
                    # Display the resulting vframe
                    cv2.imshow('Acquisition Camera',vframe)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # When everything done, release the capture
                #t1.join()
                #cap.release()
                cv2.destroyAllWindows()
                print("Camera stopped!")
                #t1.join()
                print("Is the camera thread on or off?", t1.is_alive())

        except KeyboardInterrupt:
                close()
        except:
                print("2nd Error with Live view of the camera! Exiting program!")
                close()

# def PiCamCheck():
        # try:
                # # initialize the camera and grab a reference to the raw camera capture
                # global picamera
                # picamera = PiCamera()
                # width = 320#640#320
                # height = 240#480#240
                # picamera.resolution = (width, height)
                # picamera.framerate = 32
                # rawCapture = PiRGBArray(picamera, size=(width, height))
                
                # # allow the camera to warmup
                # time.sleep(0.1)
                               
                # # capture frames from the camera
                # for pframe in picamera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                        # # grab the raw NumPy array representing the image, then initialize the timestamp
                        # # and occupied/unoccupied text
                        # pimage = pframe.array

                        # #rotate image 180 degrees
                        # #rows, cols, extra = pimage.shape
                        # #M = cv2.getRotationMatrix2D((width/2,height/2),180,1)
                        # #pimage = cv2.warpAffine(pimage,M,(width,height))
                 
                        # # show the frame
                        # cv2.imshow("Surveillance Camera", pimage)
                        # key = cv2.waitKey(1) & 0xFF
                 
                        # # clear the stream in preparation for the next frame
                        # rawCapture.truncate(0)
                 
                        # # if the `q` key was pressed, break from the loop
                        # if key == ord("q"):
                                # print("Ending picamera loop")
                                # break

                # print("Closed the Picamera window and cleaned up!")
                # #release the camera
                # #cv2.destroyAllWindows()
                # pframe.close()
                # rawCapture.close()
                # picamera.close()
                
        # except KeyboardInterrupt:
                # close()
        # except:
                # print("Error with Pi camera! Exiting program!")
                # close()

def StartAllScans(x0, xw, y0, yh, manual_sample_name, noproj_acq, tomo_reps, time_diff, tomo_count_from, email_recipent):

    """
    Starts all scans (both single and repetitive ones) with the respective scanning parameters.

    Parameters
    ----------
    y0 : ndarray
        y coordinate
        
    """
    
    try:
            #the user can specify the number of projections for each scan.
            #Maximum is 200 per rotation
            #the step motor will still rotate 200 steps, but images 
            #will only be acquired at each specified projection
            #proj_skip = round(200/noproj_acq)
            
            #for normal scanning, please use scan mode 1
            proj_skip = Initiate_rotation_stage(scan_mode = 1, no_projections=noproj_acq)
            #scan mode 4 is too slow for real scanning.
            #proj_skip = Initiate_rotation_stage(scan_mode = 4, no_projections=noproj_acq)
            
            #create new folder
            Initiate_new_scan(manual_sample_name)
            #Turn Rotate Stage ON if OFF
            if stageon is False:
                    print("Rotation stage was OFF. Now turning it back ON!")
                    iot_switch(send = True)

            if tomo_reps == 1:
                    if lightson is False:
                            #lamp ON via Relay 
                            relay_switch(send = True)
                            print("Waiting 5 seconds for brightness adjustment of the camera.")
                            print("To reduce waiting time, please turn the lights ON, prior to starting the scan.")
                            sleep(5)
                    elif lightson is True:
                            print("Camera already adjusted to the correct brightness, since the lights were on, prior to the start of the scan.")                
                    StartScan(x0, xw, y0, yh, proj_skip)
                    #StartScanRedOutEnd(x0, xw, y0, yh, proj_skip)
                    #StartRefScan(x0, xw, y0, yh)
            elif tomo_reps > 1:
                    if lightson is False:
                            #lamp ON via Relay
                            relay_switch(send = True)
                            print("Waiting 5 seconds for brightness adjustment of the camera.")
                            print("To reduce waiting time, please turn the lights ON, prior to starting the scan.")
                            sleep(5)
                    elif lightson is True:
                            print("Camera already adjusted to the correct brightness, since the lights were ON, prior to the start of the scan.")
                    StartRepScan(x0, xw, y0, yh, proj_skip, tomo_reps, time_diff, tomo_count_from)

            #Turn OFF Rot Stage
            iot_switch(send = False)
            #turn OFF lamp
            relay_switch(send = False)

            #if tomo_reps == 1:
            #        send_email(email_recipent, 'KBLT standard scan of %s finished' % manual_sample_name, 'KBLT standard scan of %s just finished! /KBLT team' % manual_sample_name)
            #elif tomo_reps > 1:
            #        send_email(email_recipent, 'KBLT Repetition scans of %s finished' % manual_sample_name, 'KBLT Repetition scans of %s just finished! /KBLT team' % manual_sample_name)
    except KeyboardInterrupt:
            close()
    #except:
            #print("Error with Full Scan! Exiting program!")
            #close()

def StartScan(x0, xw, y0, yh, proj_skip):

    """
    Starts the scan with the respective scanning parameters.

    Parameters
    ----------
    x0 : ndarray
        x coordinate
        
    """

    try:
            d = 0
            rotation_angles = pd.DataFrame([["tomo_%04d" % (d,),0]], columns=["Projection","Angle"])
            time_start = datetime.datetime.now()

            #TranslationStageThread(direction = True)5ting 3D tomography scan.")
            GPIO.output(DIR, CW)
            led_onoff_green(ledpower = True)
            
            for x in range(step_count):
                    GPIO.output(STEP, GPIO.HIGH)
                    
                    #aqcuire every n steps
                    if x % proj_skip == 0:
                            # real acquisition
                            retproj, frameproj = cap.read()
                            #crop image                
                            frameproj = frameproj[y0:yh, x0:xw]
                            d = d + 1
                            
                            # modified by Stefanos
                            angle = d*(360/step_count)
                            rotation_step = pd.DataFrame([["tomo_%04d" % (d,),angle]], columns=["Projection","Angle"])
                            rotation_angles = rotation_angles.append(rotation_step)
                            
                            cv2.imwrite(sample_folder + "/" + "tomo_%04d" % (d,) + ".tif", frameproj)
                            sleep(delay)
                            
                    GPIO.output(STEP, GPIO.LOW)
                    #normal delay needed for light samples. scan mode 4.
                    sleep(delay)
                    #long delay needed for high torque for heavy samples, to avoid backlash. scan mode 1.
                    #sleep(0.2)
                    
                    #led_blinking_green()
                    #string = "Proj. no. " + str(x) + "/" + str(step_count)
                    #print(string)

                    if x % 50 == 0:
                    #if x % 20 == 0:
                            string = "Proj. no. " + str(x) + "/" + str(step_count)
                            print(string)

            rotation_angles.to_csv(sample_folder + "/" + "rotation_angles.csv",index=False) # added by Stefanos
            time_end = datetime.datetime.now()
            time_total = time_end - time_start
            print("Tomo scanning toke: ")
            print(time_total)
            myDisplay.quit()
            led_onoff_green(ledpower = False)

    except KeyboardInterrupt:
            print("Scan interrupted via Ctrl+C command!")
            close()
    except NameError:
            if sample_folder is None:
                    print("Please create a new sample folder, prior to starting a scan!")

def StartRepScan(x0, xw, y0, yh, proj_skip, tomo_reps, time_diff, tomo_count_from):
        try:
                print("Starting 4D tomography scan.")
                GPIO.output(DIR, CW)
                led_onoff_green(ledpower = True)

                k = 0
                d = 0
                
                for u in range(tomo_count_from, tomo_count_from + tomo_reps):
                        #create each specific sub-folder per tomo
                        #make a def function for this and reuse!
                        sample_sub_folder = sample_folder + "/" + "rep_" + str(u+1) + "/"
                        if not os.path.exists(sample_sub_folder):
                                os.makedirs(sample_sub_folder)

                        time_start = datetime.datetime.now()
                        
                        for x in range(step_count):
                                GPIO.output(STEP, GPIO.HIGH)
                                # real acquisition

                                #aqcuire every n steps
                                if x % proj_skip == 0:
                                        retrep, framerep = cap.read()
                                        framerep = framerep[y0:yh, x0:xw]
                                        d = d + 1
                                        cv2.imwrite(sample_sub_folder + "/" + "tomo_%04d" % (d,) + ".tif", framerep)
                                        sleep(delay)
                                        
                                GPIO.output(STEP, GPIO.LOW)
                                #normal delay needed for light samples. scan mode 4.
                                sleep(delay)
                                #long delay needed for high torque for heavy samples, to avoid backlash. scan mode 1.
                                #sleep(0.2)
                                #led_blinking_green()
                        
                        d = 0
                        print("Tomo" + str(u+1) + "of" + str(tomo_reps) + "done!")

                        time_end = datetime.datetime.now()
                        time_total = time_end - time_start
                        print("Tomo scanning toke: ")
                        print(time_total)

                        k = k + 1

                        #delay time in seconds between each repeated scan
                        #if time_diff is not 0 and u is not tomo_reps:
                        if k < tomo_reps:
                            print("Delay time for next scan is: %s seconds." % time_diff)
                            for i in range(time_diff):
                                print(str(time_diff-i) + " seconds remaining.")
                                sleep(1)

                myDisplay.quit()
                led_onoff_green(ledpower = False)

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a new sample folder, prior to starting a scan!")

def ManualRefScan(x0, xw, y0, yh, manual_sample_name):
        
        try:

                print("Starting Manual Reference scan.")

                #create new folder
                Initiate_new_scan(manual_sample_name)
                
                for y in range(no_flats+10):
                        # real acquisition
                        retflat, frameflat = cap.read()
                        frameflat = frameflat[y0:yh, x0:xw]
                        d = y + 1
                        cv2.imwrite(sample_folder + "/" + "flat_%04d" % (d,) + ".tif", frameflat) 
                        sleep(delay)

                print("Manual Reference scanning done!")
                
                myDisplay.quit()

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a  new sample folder, prior to starting a scan!")

def ManualDarkScan(x0, xw, y0, yh, manual_sample_name):
        
        try:

                print("Starting Manual Dark scan.")

                #create new folder
                Initiate_new_scan(manual_sample_name)
                
                for y in range(no_darks+10):
                        # real acquisition
                        retdark, framedark = cap.read()
                        framedark = framedark[y0:yh, x0:xw]
                        d = y + 1
                        cv2.imwrite(sample_folder + "/" + "dark_%04d" % (d,) + ".tif", framedark) 
                        sleep(delay)

                print("Manual Dark scanning done!")
                
                myDisplay.quit()

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a  new sample folder, prior to starting a scan!")

def StartRefScan(x0, xw, y0, yh):
        try:

                print("Starting Reference scan.")
                #deactive translation stage, just to make sure the wrong motor is not active, i.e. wrong info via transon
                #correct this in later release!
                relay_switch_trans(send = False, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                #activate translation sample stage
                relay_switch_trans(send = True, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                #move out translation sample stage
                TranslationStageThread(direction = False, trans_step = 2000)#1000)#)768)

                led_onoff_green(ledpower = True)

                #sleep 1 second to allow translation stage to finish.
                sleep(1)
                
                for y in range(no_flats):
                        # real acquisition
                        retflat, frameflat = cap.read()
                        frameflat = frameflat[y0:yh, x0:xw]
                        d = y + 1
                        cv2.imwrite(sample_folder + "/" + "flat_%04d" % (d,) + ".tif", frameflat) 
                        sleep(delay)

                        #show image on screen
                        #cv2.imshow('image',frame)
                        #string = "Flat no. " + str(y) + "/" + str(no_flats)
                        #print(string)
                        #frame.drawText(string)
                        #frame.show()

                print("Reference scanning done!")
                led_onoff_green(ledpower = False)

                print("Translating sample back to position...")
                #move translation sample stage in
                TranslationStageThread(direction = True, trans_step = 768)
                #deactivate translation sample stage
                relay_switch_trans(send = False, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                sleep(5*delay)
                myDisplay.quit()

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a  new sample folder, prior to starting a scan!")

##def my_login_email():
##        global GMAIL_USER
##        global GMAIL_PASS
##        global SMTP_SERVER
##        global SMTP_PORT

#file1 = open("/home/pi/Documents/Credentials/email_credentials.txt","r")
file1 = open( os.path.join(os.path.dirname(__file__), '..', 'credentials', 'email_credentials.txt') )

txt = []
for line in file1:
    text = line.split("=")
    txt.append(text[1])

file1.close()

global GMAIL_USER
global GMAIL_PASS
global SMTP_SERVER
global SMTP_PORT

GMAIL_USER = txt[0].rstrip()
GMAIL_PASS = txt[1].rstrip()
SMTP_SERVER = txt[2].rstrip()
SMTP_PORT = txt[3].rstrip()

def send_email(recipient, subject, text):
        try:
                smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo
                smtpserver.login(GMAIL_USER, GMAIL_PASS)
                header = 'To: ' + recipient + '\n' + 'From: ' + GMAIL_USER
                header = header + '\n' + 'Subject:' + subject + '\n'
                msg = header + '\n' + text + ' \n\n'
                # attach image to message body
                #https://code.tutsplus.com/tutorials/sending-emails-in-python-with-smtp--cms-29975
                #msg.attach(MIMEImage(file("/home/pi/KBLT/raw/2019118/Lova/tomo_0001.tif").read()))
                #https://temboo.com/python/upload-to-dropbox
                smtpserver.sendmail(GMAIL_USER, recipient, msg)
                smtpserver.close()
                print("E-mail successfully sent to: %s" % recipient)
        except KeyboardInterrupt:
                print("Program closed via Ctrl+C command!")
        #except:
        #        print("There was a problem with sending the email! Email not sent!")

#def send_email_message(destination_email, subject, text):
        #my_login_email()
#        send_email(destination_email, subject, text)

def close():
    # when clicking the exit button, clean up GPIO, close windows, close myDisplay, 
    try:
        #shuts down rotation stage
        iot_switch(send = False)
        #shuts down the lamp
        relay_switch(send = False)
        #shuts down the LED
        led_onoff_green(ledpower = False)
        #shut off relay for translation stage
        relay_switch_trans(send = False, pinact = 15, pininact2 = 12, pininact3 = 27, pininact4 = 25)
        #clean up
        GPIO.cleanup()
        #exit cleanly, i.e. if the LED is on it shuts down when exiting
        win.destroy()
        #close the display
        #myDisplay.quit()
        #close active threads
        cleanup_stop_thread()
        #Close the Pi Camera window, MAYBE WORKING!?
        cv2.destroyAllWindows()
        frameflat.close()
        framerep.close()
        frametest.close()
        vframe.close()
        frameproj.close()
        rawCapture.close()
        #picamera.close()
        print("Program closed correctly!")
    except KeyboardInterrupt:
        print("Program closed via Ctrl+C command!")
    except:
        print("Nothing to clean up!")
        
    print("Script closed!")
    exit()
