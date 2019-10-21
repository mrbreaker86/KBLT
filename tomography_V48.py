#!/usr/bin/python

#to do
#adjust exposure time:
#https://github.com/sightmachine/simplecv-examples/blob/master/code/long-exposure.py
#measure the time for one program (def)
#https://github.com/sightmachine/simplecv-examples/blob/master/code/timing.py

#luvcview -d /dev/video0

from SimpleCV import Camera, Display, DrawingLayer
from SimpleCV import *
from picamera.array import PiRGBArray
from picamera import PiCamera
#Open CV
import cv2
from time import sleep, time, time
import time
#from datetime import datetime
import datetime
#from PIL import Image
import PIL.Image
import RPi.GPIO as GPIO
import os
from sys import exit
import numpy
from pygame import mixer # Load the required library

####### packages needed for the GUI ####
#python2
from Tkinter import *
#import Tkinter.font
import tkFont
#python3
#from tkinter import *
#import tkinter.font

####### packages needed for the email service ####
import smtplib

####### packages needed for connecting to samba server for storage of the files ####
import smb
from smb.SMBConnection import SMBConnection
import tempfile

####### package for threading
import threading

####### copy files
#from shutil import copyfile
import shutil

####### dxchange
#import dxchange
#import dxchange.reader as dxreader
import tifffile as tiff
from tifffile import imsave

## GUI DEFINITIONS ##
# this creates the GUI object in which we can put other stuff
win = Tk()
win.title("KBLT")
# definition
#python2
myFont = tkFont.Font(family = 'Helvetica', size = 12, weight = "bold")
#myFont = Tkinter.font.Font(family = 'Helvetica', size = 12, weight = "bold")
#python3
#my = tkinter.font.Font(family = 'Helvetica', size = 12, weight = "bold")

################

#global area
# = area
#break

emergency_stop = False
lightson = False
stageon = False
transon = False
#global no_flats
#global no_darks
#global tomo_reps
no_flats = 10
no_darks = 10

def read_rgb_convert(fname, name, save_out):

    fname = os.path.abspath(fname)
    data_name = os.path.join(fname, name)
#    print(data_name)

#    for m, fname in enumerate(data_name):
    data = tiff.imread(data_name)
#    data = data.astype(np.int16)
    #data = rgb2gray(data) * 32767
#    data = rgb2gray(data) * 65536
    #data = data.astype(np.int16)
    
    #data = np.average(data, axis=3)

    #print('data type: ')
    #print(len(data[0]))
    #print(type(data[0]))
    
    if save_out is True:
        fname_out = os.path.join(fname, '16bit')    
        if not os.path.exists(fname_out):
            os.makedirs(fname_out)
        
        for i in range(len(data)):
            imsave(fname_out + '/' + name + '_' + "%04d" % (i+1,) + '.tif', data[i])
        
        print("Saved down 16bit converted %s!" %name)
            
    return data

#not used
def read_rgb(fname, name):

    fname = os.path.abspath(fname)
    data_name = os.path.join(fname, name)
#    print(data_name)

    data = tiff.imread(data_name)
    
    return data

#not used
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def AudioMessage():
        mixer.init()
        mixer.music.load('/home/pi/Music/LightsOn.mp3')
        mixer.music.play()
        #sleep(5)
        print("Audio message done!")

def restartprogram():
        try:
                #not working properly, due to Cameras, which do not restart properly
                print("Restarting KBLT program.")
                #os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
                #cleanup_stop_thread()
                python = sys.executable
                os.execl(python, python, * sys.argv)
                #reload(my_module)
                #close()

        except KeyboardInterrupt:
                close()
        except:
                print("Error Restarting program! Event ignored!")

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

def reset_relay_switch_trans_manual(pin):
        try:
                global transon
                
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.OUT)

                GPIO.output(pin, GPIO.LOW)
                sleep(0.51)
                print("Resetting the Translation stage!")
                transon = False

        except KeyboardInterrupt:
                close()
        except:
                print("Error with manually resetting the Translation stage via the Relay! Event ignored!")

def relay_switch_trans(send, pinact, pininact2, pininact3, pininact4):
        try:
                pininact234 = [pininact2, pininact3, pininact4]
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pinact, GPIO.OUT)
                for i in pininact234:
                        GPIO.setup(i, GPIO.OUT)
                
                global transon
    
                #turn on
                if send is True and transon is False:
                        #inactive (just to be sure) the other serially connected relay
                        for i in pininact234:
                                GPIO.output(i, GPIO.LOW)
                                print("...")
                                sleep(0.51)
                        #active the given relay
                        GPIO.output(pinact, GPIO.HIGH)
                        sleep(0.51)
                        print("...")
                        #inform other functions that translation stage is on
                        transon = True
                        print("Translation stage is ON!")
                elif send is True and transon is True:
                        print("Translation stage is already ON!")
                elif send is False and transon is True:
                        GPIO.output(pinact, GPIO.LOW)
                        sleep(0.51)
                        print("...")
                        #inactive (just to be sure) the other serially connected relay
                        for i in pininact234:
                                GPIO.output(i, GPIO.LOW)
                                print("...")
                                sleep(0.51)
                        #inform other functions that translation stage is off
                        transon = False
                        print("Translation stage is OFF!")
                elif send is False and transon is False:
                        print("Translation stage is already OFF!")

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Relay for translation stage! Event ignored!")

def relay_switch(send):
        try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(24, GPIO.OUT)

                global lightson

                #turn on and off quickly
                if send is True and lightson is False:
                        AudioMessage()
                        GPIO.output(24, GPIO.HIGH)
                        sleep(0.51)
                        print("...")
                        GPIO.output(24, GPIO.LOW)
                        sleep(0.51)
                        #inform other functions that light is on
                        lightson = True
                        print("Light is ON!")
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
        except:
                print("Error with Relay! Event ignored! Please turn the lamp ON first!")

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

                #turn switch on rotation stage
                if send is True and stageon is False:
                        GPIO.output(17, GPIO.HIGH)
                        sleep(0.01)
                        #inform other functions that the light is on
                        stageon = True
                        print("Rotation stage is ON!")
                elif send is True and stageon is True:
                        print("Rotation stage is already ON!")
                elif send is False and stageon is True:
                        GPIO.output(17, GPIO.LOW)
                        sleep(0.01)
                        #inform other functions that the light is off
                        stageon = False
                        print("Rotation stage is OFF!")
                elif send is False and stageon is False:
                        print("Rotation stage is already OFF!")                      

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Switch! Event ignored! Please turn the stage ON first!")

def led_blinking_green():
        try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(22, GPIO.OUT)

                GPIO.output(22, GPIO.HIGH)
                sleep(0.01)
                GPIO.output(22, GPIO.LOW)
                sleep(0.01)
        except KeyboardInterrupt:
                close()
        except:
                print("Error with LED Blinking! Event ignored!")
                #close()

def led_onoff_green(ledpower):
        try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(22, GPIO.OUT)

                if ledpower is True:
                        GPIO.output(22, GPIO.HIGH)
                        sleep(0.01)
                elif ledpower is False:
                        GPIO.output(22, GPIO.LOW)
                        sleep(0.01)
        except KeyboardInterrupt:
                close()
        except:
                print("Error with LED Blinking! Event ignored!")
                #close()
 
def Initiate_new_scan():

        try:
                localtime = time.localtime(time.time())
                #save the files in the following folder
                global sample_folder_date
                sample_folder_date = str(localtime.tm_year) + str(localtime.tm_mon) + str(localtime.tm_mday) + '_' + str(localtime.tm_hour) + '_' + str(localtime.tm_min) + '_' + str(localtime.tm_sec)
                print(sample_folder_date)

                global sample_folder

                sample_folder = '/home/pi/KBLT/' + sample_folder_date
                if not os.path.exists(sample_folder):
                        os.makedirs(sample_folder)

        except KeyboardInterrupt:
                close()
        #except:
                #print("Error with creating new sample folder! Exiting program.")
                #close()

def TranslationStageThread(direction):
        try:
                #global t2
                t2 = threading.Thread(name="Hello2", target=Initiate_translation_stage(direction))
                t2.start()

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Threading for the Translation Stage! Exiting program!")
                close()

def Initiate_translation_stage(direction):
        try:
                #global emergency_stop
                #emergency_stop = False
                
                #GPIO.setmode(GPIO.BOARD)
                GPIO.setmode(GPIO.BCM)
                
                #go front
                if direction is True:
                        #ControlPin = [37,35,31,29]
                        GPIOno = [26,19,6,5]
                #go back
                elif direction is False:
                        #ControlPin = [29,31,35,37]
                        GPIOno = [5,6,19,26]

                #COMMAND IN TERMINAL: pinout
                #GPIO26 - PIN37
                #GPIO19 - PIN35
                #GPIO6 - PIN31
                #GPIO5 - PIN29

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
                for i in range(512):
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

                step_count = SPR * no_step
                delay = 0.0208 / no_step

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
                #Set rotation parameters
                Initiate_rotation_stage(scan_mode = 4, no_projections=800)

                #CW = 1 # Clockwise Rotation
                #CCW = 0 # Couterclockwise Rotation
                if direction == 1:
                        GPIO.output(DIR, CW)                    
                elif direction == 0:
                        GPIO.output(DIR, CCW)
                
                for x in range(step_count):
                        GPIO.output(STEP, GPIO.HIGH)
                        sleep(delay)
                        GPIO.output(STEP, GPIO.LOW)
                        if x % 10 == 0:
                                led_blinking_green()                        
                        
        except KeyboardInterrupt:
                close()
        except:
                print("Error with rotating the rotation stage! Exiting program.")
                close()
           
def CamAreaOnThread():
        try:
                global t1
                t1 = threading.Thread(name="Hello", target=CamAreaCheck)
                t1.start()
                #sleep(10)
                #t1.join(None)
                #print("just closed the camera thread!")
        except KeyboardInterrupt:
                #t1.join(None)
                close()
        except:
                print("Error with Threading for the camera! Exiting program!")
                #t1.join(None)
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
                #t1.join(None)
                close()
        except:
                print("Error with Threading for the Pi camera! Exiting program!")
                #t2.join(None)
                close()
    
#area = (0, 0, 640, 480)
#Set capture area

def ReleaseCam():
        try:
                #not working!
                #trying to release the camera
                #myDisplay.lock.release()
                #myCamera.lock.release()
                print("hej")

        except KeyboardInterrupt:
                close()
        except:
                print("Error with Releasing Camera! Event ignored!")
                
def CamAreaCheck():
        try:
                #backup, if webcamera is already on, we close it first.
                #if myDisplay.isDone():
                #        myDisplay.quit()
                
                #needed to reload the online view of the camera, after closing by StartScan or RefScan
                #myCamera = Camera(0)
                #myDisplay = Display(resolution=(640, 480))
                #initCamera()
                #CamButton["text"] = "Start Camera!"

                #try either e.g. Camera(0) or Camera(1) depending on which USB-port is connnected, update this on all places below in the script.
                global myCamera
                global myDisplay
                global img
                print("test1")
                #myCamera = Camera(0)
                myCamera = Camera(1)
                print("test2")
                #del myCamera
                #del(myCamera)
                print("test3")
                #Logitech HD 720p Webcam C310
                #myDisplay = Display(resolution=(640, 480))
                #Logitech HD Webcam B525
                myDisplay = Display(resolution=(1920, 1080))
                #myDisplay = Display(resolution=(1280, 720))
                print("test4")

                global area
                #Logitech HD 720p Webcam C310
                #area = (0, 0, 640, 480)
                #Logitech HD Webcam B525
                area = (0, 0, 1920, 1080)
                #area = (0, 0, 1280, 720)
                #area = (300, 70, 70, 300)
                #area = (pos_x, pos_y, width_x, width_y)

                #size depends on the USB-camera used
                # area = (250, 150, 350, 390)

                #down scale the image shown on the screen, convert tuple to integers, and round up
                global scale_factor
                #Logitech HD 720p Webcam C310
                #scale_factor = 2
                #Logitech HD Webcam B525
                scale_factor = 6

                global scale_x_width
                global scale_y_width
                scale_x_width = int(int(area[2]) / scale_factor)
                scale_y_width = int(int(area[3]) / scale_factor)

                print(scale_x_width)
                print(scale_y_width)
                print("Camera initiated!")
              
                while not myDisplay.isDone():
                    #CamButton["text"] = "The camera is now on!"
                    img = myCamera.getImage().crop(area)#.save(myDisplay)
                    #img = myCamera.getImage().save(myDisplay)

                    #downscale image to better fit the screen
                    img.scale(scale_x_width,scale_y_width).show()
                    sleep(.1)

                    #means if right mouse button is click ("True"), then do...
                    if myDisplay.mouseWheelDown:
                            #CamButton["text"] = "The Cam is off!"
                            myDisplay.quit()
                            #to test!!!, raise bool error
                            #myDisplay.isDone = True
                            #if no cropping is done, b is set to the original area.
                            #If cropping has been done b is set to the cropped area.
                            global area_cr
                            area_cr = area
                            #del myCamera
                            break

                    if myDisplay.mouseLeft:
                            x_0 = myDisplay.mouseRawX
                            y_0 = myDisplay.mouseRawY

                            print("Mouse RawX and RawY (start): ")
                            print(x_0, y_0)

                    if myDisplay.mouseRight:
                            x_end = myDisplay.mouseRawX
                            y_end = myDisplay.mouseRawY

                            print("Mouse RawX and RawY (end): ")
                            print(x_end, y_end)

                    if myDisplay.mouseWheelUp:
                            #update value in tuple, via conversion to list and reconversion to tuple
                            print("Sum up the area values!")
                            lst = list(area)
                            print(lst)
                            lst[0] = x_0 * 2# scale_factor
                            print(lst[0])
                            lst[1] = y_0 * 3# scale_factor
                            print(lst[1])
                            lst[2] = abs(x_end - x_0) * 2# scale_factor
                            print(lst[2])
                            lst[3] = abs(y_end - y_0) * 3#scale_factor
                            print(lst[3])
                            area = tuple(lst)
                            print(list(area))
                            
                            #global area_cr
                            print("hej")
                            #area = (300, 70, 70, 300)
                            area_cr = area
                            print("hej2")
        except KeyboardInterrupt:
                close()
        except:
                print("Error with Defining the croped region of the camera! Exiting program!")
                close()

def PiCamCheck():
        try:
                # initialize the camera and grab a reference to the raw camera capture
                global picamera
                picamera = PiCamera()
                width = 320#640
                height = 240#480
                picamera.resolution = (width, height)
                picamera.framerate = 32
                rawCapture = PiRGBArray(picamera, size=(width, height))
                 
                # allow the camera to warmup
                time.sleep(0.1)
                 
                # capture frames from the camera
                for frame in picamera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                        # grab the raw NumPy array representing the image, then initialize the timestamp
                        # and occupied/unoccupied text
                        image = frame.array

                        #rotate image 180 degrees
                        #rows, cols, extra = image.shape
                        #M = cv2.getRotationMatrix2D((width/2,height/2),180,1)
                        #image = cv2.warpAffine(image,M,(width,height))
                 
                        # show the frame
                        cv2.imshow("Frame", image)
                        key = cv2.waitKey(1) & 0xFF
                 
                        # clear the stream in preparation for the next frame
                        rawCapture.truncate(0)
                 
                        # if the `q` key was pressed, break from the loop
                        if key == ord("q"):
                                print("Ending picamera loop")
                                break

                print("Closed the Picamera window and cleaned up!")
                #release the camera
                cv2.destroyAllWindows()
                frame.close()
                rawCapture.close()
                picamera.close()
                
        except KeyboardInterrupt:
                close()
        except:
                print("Error with Pi camera! Exiting program!")
                close()

def Histogram():
        #not working
        try:
                #plot histogram
                #imghisto = photo.toGray()
                #histo = imghisto.histogram(255)
                #plot(histo)

                photo = Image('simplecv')
                gray = photo.toGray()
                histogram = gray.histogram()
                len(histogram)
                plot(histogram)

        except KeyboardInterrupt:
                close()
        #except:
        #        print("Error with Histogram! Exiting program!")
        #        close()

def CameraOff():
        #del(myCamera)
        myDisplay.quit()

def CamAreaCrop(area,xw,yw):
        try:
                lst = list(area)
                lst[0] = lst[0] + xw
                lst[1] = lst[1] + yw
                lst[2] = lst[2] - xw
                lst[3] = lst[3] - yw
                print(lst[3])
                area = tuple(lst)
                print(list(area))
                area_cr = area
        except KeyboardInterrupt:
                close()
        except:
                print("Error with GUI cropping! Exiting program!")
                close()

def StartAllScans(area, scale_x_width, scale_y_width, tomo_reps):

        try:
                #create new folder
                Initiate_new_scan()
                #Turn Rotate Stage ON if OFF
                if stageon is False:
                        print("Rotation stage was OFF. Now turning it back ON!")
                        iot_switch(send = True)
                #Set rotation parameters
                Initiate_rotation_stage(scan_mode = 1, no_projections=200)
                #start camera
                #CamAreaOnThread()

                if tomo_reps == 1:
                        if lightson is False:
                                #lamp ON via Relay 
                                relay_switch(send = True)
                                print("Waiting 5 seconds for brightness adjustment of the camera.")
                                print("To reduce waiting time, please turn the lights ON, prior to starting the scan.")
                                sleep(5)
                        elif lightson is True:
                                print("Camera already adjusted to the correct brightness, since the lights were on, prior to the start of the scan.")                
                        StartScan(area, scale_x_width, scale_y_width)
                elif tomo_reps > 1:
                        if lightson is False:
                                #lamp ON via Relay
                                relay_switch(send = True)
                                print("Waiting 5 seconds for brightness adjustment of the camera.")
                                print("To reduce waiting time, please turn the lights ON, prior to starting the scan.")
                                sleep(5)
                        elif lightson is True:
                                print("Camera already adjusted to the correct brightness, since the lights were ON, prior to the start of the scan.")
                        StartRepScan(area, scale_x_width, scale_y_width, tomo_reps)
                StartRefScan(area, scale_x_width, scale_y_width)

                #Turn OFF Rot Stage
                iot_switch(send = False)
                #turn OFF lamp
                relay_switch(send = False)

                if tomo_reps == 1:
                        send_email(GMAIL_USER, 'KBLT scan finished', 'Scan just finished! /KBLT team')
                elif tomo_reps > 1:
                        send_email(GMAIL_USER, 'KBLT Repetition scans finished', 'Repetition scans just finished! /KBLT team')
                   
        except KeyboardInterrupt:
                close()
        #except:
                #print("Error with Full Scan! Exiting program!")
                #close()         

def StartScan(area, scale_x_width, scale_y_width):

        try:
                time_start = datetime.datetime.now()

                #TranslationStageThread(direction = True)

                print("Starting 3D tomography scan.")
                GPIO.output(DIR, CW)
                led_onoff_green(ledpower = True)
                
                for x in range(step_count):
                        GPIO.output(STEP, GPIO.HIGH)
                        # real acquisition
                        frame = myCamera.getImage()
                        d = x + 1
                        frame = frame.crop(area)
                        #convert color image to grey image
                        frame = frame.toGray()
                        frame.save(sample_folder + "/" + "tomo_%04d" % (d,) + ".tif")
                        sleep(3*delay)
                        GPIO.output(STEP, GPIO.LOW)
                        sleep(3*delay)
                        #led_blinking_green()

                        if x % 20 == 0:
                                string = "Proj. no. " + str(x) + "/" + str(step_count)
                                print(string)
                        
                        #show every 20th image on the screen
                        if x % 20 == 0:
                                #frame.save(myDisplay)
                                frame.scale(scale_x_width, scale_y_width)
                                frame.drawText(string)
                                frame.show()

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
                elif area is None:
                        print("Please set capture area (by Turning on the camera), prior to starting a scan!")

def StartRepScan(area, scale_x_width, scale_y_width, tomo_reps):
        try:
                print("Starting 4D tomography scan.")
                GPIO.output(DIR, CW)
                led_onoff_green(ledpower = True)
                
                for u in range(tomo_reps):
                        #create each specific sub-folder per tomo
                        #make a def function for this and reuse!
                        sample_folder2 = sample_folder + "/" + "rep_" + str(u+1) + "/"
                        if not os.path.exists(sample_folder2):
                                os.makedirs(sample_folder2)

                        time_start = datetime.datetime.now()
                        
                        for x in range(step_count):
                                GPIO.output(STEP, GPIO.HIGH)
                                # real acquisition
                                frame = myCamera.getImage()
                                d = x + 1
                                frame = frame.crop(area)
                                #convert color image to grey image
                                frame = frame.toGray()
                                frame.save(sample_folder2 + "/" + "tomo_%04d" % (d,) + ".tif")
                                sleep(delay)
                                GPIO.output(STEP, GPIO.LOW)
                                sleep(delay)
                                #led_blinking_green()

                                #show every 49th image on the screen
                                #if x % 50 == 0:
                                #        string = "Proj. no. " + str(x) + "/" + str(step_count)
                                #        print(string)
                        
                        print("Tomo" + str(u+1) + "of" + str(tomo_reps) + "done!")

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
                elif area is None:
                        print("Please set capture area (by Turning on the camera), prior to starting a scan!")

def StartRefScan(area, scale_x_width, scale_y_width):
        try:

                print("Starting Reference scan.")
                #deactive translation stage, just to make sure the wrong motor is not active, i.e. wrong info via transon
                #correct this in later release!
                relay_switch_trans(send = False, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                #activate translation sample stage
                relay_switch_trans(send = True, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                #move out translation sample stage
                TranslationStageThread(direction = False)

                led_onoff_green(ledpower = True)
                
                for y in range(no_flats):
                        frame = myCamera.getImage()
                        d = y + 1
                        frame = frame.crop(area)
                        #convert color image to grey image
                        frame = frame.toGray()
                        frame.save(sample_folder + "/" + "flat_%04d" % (d,) + ".tif")  
                        sleep(delay)

                        #show image on screen
                        frame.scale(scale_x_width, scale_y_width)
                        string = "Flat no. " + str(y) + "/" + str(no_flats)
                        print(string)
                        frame.drawText(string)
                        frame.show()

                print("Reference scanning done!")
                led_onoff_green(ledpower = False)

                print("Translating sample back to position...")
                #move translation sample stage in
                TranslationStageThread(direction = True)
                #deactivate translation sample stage
                relay_switch_trans(send = False, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4)
                frame = myCamera.getImage()
                frame = frame.crop(area)
                frame.scale(scale_x_width, scale_y_width)
                frame.show()
                sleep(5*delay)
                myDisplay.quit()

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a new sample folder, prior to starting a scan!")
                elif area is None:
                        print("Please set capture area (by Turning on the camera), prior to starting a scan!")

def StartDarkScan(area, scale_x, scale_y):
        try:
                for y in range(no_darks):
                        frame = myCamera.getImage()
                        d = y + 1
                        frame = frame.crop(area)
                        #convert color image to grey image
                        frame = frame.toGray()
                        frame.save(sample_folder + "/" + "dark_%04d" % (d,) + ".tif")
                        sleep(delay)

                        #show image on screen
                        frame.scale(scale_x,scale_y)
                        string = "Dark no. " + str(y) + "/" + str(no_darks)
                        print(string)
                        frame.drawText(string)
                        frame.show()

                print("Scanning darks done!")
                myDisplay.quit()

        except KeyboardInterrupt:
                print("Scan interrupted via Ctrl+C command!")
                close()
        except NameError:
                if sample_folder is None:
                        print("Please create a new sample folder, prior to starting a scan!")
                elif area is None:
                        print("Please set capture area (by Turning on the camera), prior to starting a scan!")
  
##def my_login_email():
##        global GMAIL_USER
##        global GMAIL_PASS
##        global SMTP_SERVER
##        global SMTP_PORT

file1 = open("/home/pi/Documents/Credentials/email_credentials.txt","r")

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
                smtpserver.sendmail(GMAIL_USER, recipient, msg)
                smtpserver.close()
                print("E-mail successfully sent!")
        except KeyboardInterrupt:
                print("Program closed via Ctrl+C command!")
        #except:
        #        print("There was a problem with sending the email! Email not sent!")

#def send_email_message(destination_email, subject, text):
        #my_login_email()
#        send_email(destination_email, subject, text)

def copy_local_to_smb():

        try:

                file2 = open("/home/pi/Documents/Credentials/smbcredentials.txt","r")

                txt2 = []
                for line in file2:
                    text2 = line.split("=")
                    txt2.append(text[1])

                file2.close()

                SMB_USER = str(txt2[0].rstrip())
                SMB_PASS = str(txt2[1].rstrip())
                SMB_SERVER = str(txt2[2].rstrip())
                SMB_SHARE = str(txt2[3].rstrip())
                SMB_IP = str(txt2[4].rstrip())
                
                #Initiate_new_scan()
                #sample_folder_date = "2019108_18_12_5"
                sample_folder = '/home/pi/KBLT/' + sample_folder_date + "/"
                sample_folder = os.path.abspath(sample_folder)
                #sample_folder = os.path.join(sample_folder, '*.tiff')
                #sample_folder = os.path.join(sample_folder, 'tomo_0001.tiff')
                print(sample_folder)

                path = '/KBLT/DATA_SETS/'
                sample_folder_out = SMB_IP + '/' + SMB_SHARE + path + sample_folder_date + '/'
                sample_folder_out = os.path.abspath(sample_folder_out)
                print(sample_folder_out)

                if not os.path.exists(sample_folder_out):
                    os.makedirs(sample_folder_out)

                global share_name
                share_name = SMB_SHARE
                global sample_folder_smb
                sample_folder_smb = path + sample_folder_date
                user_name = SMB_USER
                password = SMB_PASS
                local_machine_name = 'RPiKBLT'
                server_machine_name = SMB_SERVER
                server_IP = SMB_IP
                global conn
                conn = SMBConnection(user_name, password, local_machine_name, server_machine_name, use_ntlm_v2 = True)
                assert conn.connect(server_IP, 139)
                conn.createDirectory(share_name, sample_folder_smb, timeout = 30)

                #data = tiff.imread(sample_folder)
                #data = read_rgb_convert(sample_folder, '*.tif', save_out=False)

                copytree(sample_folder, sample_folder_out, symlinks=False, ignore=None)

                #conn.storeFile(share_name, sample_folder_smb, data[0], timeout = 30)
                print("files successfully copied to SMB Server!")

        except KeyboardInterrupt:
                print("SMB copy interrupted via Ctrl+C command!")
                close()
        #except:
        #        print("SMB error!")

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
        relay_switch_trans(send = False, pinact = 4, pininact2 = 12, pininact3 = 27, pininact4 = 25)
        #clean up
        GPIO.cleanup()
        #exit cleanly, i.e. if the LED is on it shuts down when exiting
        win.destroy()
        #close the display
        myDisplay.quit()
        #close active threads
        cleanup_stop_thread()
        #Close the Pi Camera window, MAYBE WORKING!?
        cv2.destroyAllWindows()
        frame.close()
        rawCapture.close()
        picamera.close()
        #close SMB connection, might need to declare 'smb' as a global parameter,
        #in ordet for this to work here
        #if smb is True:
        #close SMB connection
        conn.close()
        print("Program closed correctly!")
    except KeyboardInterrupt:
        print("Program closed via Ctrl+C command!")
    except:
        print("Nothing to clean up!")
        
    print("Script closed!")
    #exit()
    sys.exit()

### WIDGETS ###

#main program below!

try:
        #Labels
        lbl = Label(win, text="Cameras:", font = myFont)
        lbl.grid(row=1,column=1)
        
        #Cam button
        CamButtonOn = Button(win, text = 'Acq.', font = myFont, command = lambda: CamAreaOnThread(), bg = 'green2', height = 1, width = 6)
        CamButtonOn.grid(row=1,column=2)

        PiCamButtonOn = Button(win, text = 'Surv.', font = myFont, command = lambda: PiCamOnThread(), bg = 'yellow2', height = 1, width = 6)
        PiCamButtonOn.grid(row=1,column=3)

        #AcqHistogram = Button(win, text = 'Histo.', font = myFont, command = lambda: Histogram(), bg = 'yellow2', height = 1, width = 6)
        #AcqHistogram.grid(row=1,column=4)

        #PiCamButtonOff = Button(win, text = 'Rel. Acq', font = myFont, command = lambda: ReleaseCam(), bg = 'red2', height = 1, width = 6)
        #PiCamButtonOff.grid(row=1,column=4)

        #Labels
        lbl = Label(win, text="Light Source:", font = myFont)
        lbl.grid(row=2,column=1)

        #Power up lamp relay button
        SwitchOnLightRelayButton = Button(win, text = 'ON', font = myFont, command = lambda: relay_switch(send = True), bg = 'green2', height = 1, width = 6)
        SwitchOnLightRelayButton.grid(row=2,column=2)

        #Shutdown lamp relay button
        SwitchOffLightRelayButton = Button(win, text = 'OFF', font = myFont, command = lambda: relay_switch(send = False), bg = 'red2', height = 1, width = 6)
        SwitchOffLightRelayButton.grid(row=2,column=3)

        #Resetting the lamp relay button
        SwitchResetLightRelayButton = Button(win, text = 'RESET', font = myFont, command = lambda: relay_switch_manual(), bg = 'yellow2', height = 1, width = 6)
        SwitchResetLightRelayButton.grid(row=2,column=4)

        #Labels
        lbl = Label(win, text="Rotation Stage:", font = myFont)
        lbl.grid(row=3,column=1)
        
        #Power up rotation stage button
        SwitchOnButton = Button(win, text = 'ON', font = myFont, command = lambda: iot_switch(send = True), bg = 'green2', height = 1, width = 6)
        SwitchOnButton.grid(row=3,column=2)

        #Shutdown rotation stage button
        SwitchOffButton = Button(win, text = 'OFF', font = myFont, command = lambda: iot_switch(send = False), bg = 'red2', height = 1, width = 6)
        SwitchOffButton.grid(row=3,column=3)

        #Labels
        lbl = Label(win, text="Rotate Sample:", font = myFont)
        lbl.grid(row=4,column=1)
        
        #Rotate 90 deg Plus button
        RotatePlusButton = Button(win, text = '+90', font = myFont, command = lambda: Rotate90deg(step_count=200, direction=1), bg = 'bisque2', height = 1, width = 6)
        RotatePlusButton.grid(row=4,column=2)

        #Rotate 90 deg Plus button
        RotatePlusButton = Button(win, text = '-90', font = myFont, command = lambda: Rotate90deg(step_count=200, direction=0), bg = 'bisque2', height = 1, width = 6)
        RotatePlusButton.grid(row=4,column=3)

        #Rotate 45 deg Plus button
        #RotatePlusButton = Button(win, text = 'Rot. +45', font = myFont, command = lambda: Rotate90deg(step_count=25, direction=1), bg = 'bisque2', height = 1, width = 6)
        #position of the Button on the grid
        #RotatePlusButton.grid(row=4,column=3)

        #Rotate 45 deg Plus button
        #RotatePlusButton = Button(win, text = 'Rot. -45', font = myFont, command = lambda: Rotate90deg(step_count=25, direction=0), bg = 'bisque2', height = 1, width = 6)
        #position of the Button on the grid
        #RotatePlusButton.grid(row=4,column=4)

        #Rotate 5 deg Plus button
        #RotatePlusButton = Button(win, text = 'Rot. +5', font = myFont, command = lambda: Rotate90deg(step_count=9, direction=1), bg = 'bisque2', height = 1, width = 6)
        #position of the Button on the grid
        #RotatePlusButton.grid(row=4,column=5)

        #Rotate 5 deg Plus button
        #RotatePlusButton = Button(win, text = 'Rot. -5', font = myFont, command = lambda: Rotate90deg(step_count=9, direction=0), bg = 'bisque2', height = 1, width = 6)
        #position of the Button on the grid
        #RotatePlusButton.grid(row=4,column=6)

        #Labels
        lbl = Label(win, text="Translation Stages:", font = myFont)
        lbl.grid(row=5,column=1)

        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Light', font = myFont, command = lambda: relay_switch_trans(send = True, pinact = 12, pininact2 = 25, pininact3 = 27, pininact4 = 4), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=2)

        #Shutdown trans stage button
        #SwitchOffTransButton = Button(win, text = 'OFF', font = myFont, command = lambda: relay_switch_trans(send = False, pinact = 12, pininact2 = 25, pininact3 = 27, pininact4 = 4), bg = 'red2', height = 1, width = 6)
        #SwitchOffTransButton.grid(row=5,column=3)   

        #Resetting the lamp relay button
        #SwitchResetTransButton = Button(win, text = 'RESET', font = myFont, command = lambda: reset_relay_switch_trans_manual(12), bg = 'yellow2', height = 1, width = 6)
        #SwitchResetTransButton.grid(row=5,column=4)

        #Labels
        #lbl = Label(win, text="Translation Stage Sample:", font = myFont)
        #lbl.grid(row=6,column=1)
        
        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Sample', font = myFont, command = lambda: relay_switch_trans(send = True, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=3)

        #Shutdown trans stage button
        #SwitchOffTransButton = Button(win, text = 'OFF', font = myFont, command = lambda: relay_switch_trans(send = False, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 4), bg = 'red2', height = 1, width = 6)
        #SwitchOffTransButton.grid(row=6,column=3)  

        #Resetting the lamp relay button
        #SwitchResetTransButton = Button(win, text = 'RESET', font = myFont, command = lambda: reset_relay_switch_trans_manual(25), bg = 'yellow2', height = 1, width = 6)
        #SwitchResetTransButton.grid(row=5,column=4)

        #Labels
        #lbl = Label(win, text="Translation Stage Screen:", font = myFont)
        #lbl.grid(row=7,column=1)
        
        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Screen', font = myFont, command = lambda: relay_switch_trans(send = True, pinact = 27, pininact2 = 12, pininact3 = 25, pininact4 = 4), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=6,column=2)

        #Shutdown trans stage button
        #SwitchOffTransButton = Button(win, text = 'OFF', font = myFont, command = lambda: relay_switch_trans(send = False, pinact = 27, pininact2 = 12, pininact3 = 25, pininact4 = 4), bg = 'red2', height = 1, width = 6)
        #SwitchOffTransButton.grid(row=7,column=3) 

        #Labels
        #lbl = Label(win, text="Translation Stage Camera:", font = myFont)
        #lbl.grid(row=8,column=1)
        
        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Camera', font = myFont, command = lambda: relay_switch_trans(send = True, pinact = 4, pininact2 = 12, pininact3 = 27, pininact4 = 25), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=6,column=3)

        #Shutdown trans stage button
        SwitchOffTransButton = Button(win, text = 'OFF', font = myFont, command = lambda: relay_switch_trans(send = False, pinact = 4, pininact2 = 12, pininact3 = 27, pininact4 = 25), bg = 'red2', height = 1, width = 12)
        SwitchOffTransButton.grid(row=7,column=2, columnspan=2)

        #Labels
        lbl = Label(win, text="Translate active motor:", font = myFont)
        lbl.grid(row=9,column=1)
        
        #Trans. Stage Back  button
        TransBackButton = Button(win, text = 'LEFT', font = myFont, command = lambda: TranslationStageThread(direction = False), bg = 'bisque2', height = 1, width = 6)
        TransBackButton.grid(row=9,column=2)

        #Trans. Stage Front button
        TransFrontButton = Button(win, text = 'RIGHT', font = myFont, command = lambda: TranslationStageThread(direction = True), bg = 'bisque2', height = 1, width = 6)
        TransFrontButton.grid(row=9,column=3)

        #Trans. Emergency  button
        #TransStop = Button(win, text = 'Emergency STOP!', font = myFont, command = lambda: emergencyThread(), bg = 'red2', height = 1, width = 12, state = DISABLED)
        #position of the Button on the grid
        #TransStop.grid(row=5,column=3)

        #Labels
        lbl = Label(win, text="Start Tomo. Scan:", font = myFont)
        lbl.grid(row=10,column=1)
        
        #Acq. Full Scan button
        TomoFullButton = Button(win, text = '3D', font = myFont, command = lambda: StartAllScans(area_cr, scale_x_width, scale_y_width, tomo_reps = 1), bg = 'green2', height = 1, width = 6)
        TomoFullButton.grid(row=10,column=2)

        #Acq. Rep. button
        ScanRepButton = Button(win, text = '4D', font = myFont, command = lambda: StartAllScans(area_cr, scale_x_width, scale_y_width, tomo_reps = 2), bg = 'green2', height = 1, width = 6)
        ScanRepButton.grid(row=10,column=3)

        #Labels
        lbl = Label(win, text="SMB:", font = myFont)
        lbl.grid(row=11,column=1)

        #NOT WORKING!
        #Copy to SMB button
        SMBButton = Button(win, text = 'Copy', font = myFont, command = lambda: copy_local_to_smb(), bg = 'bisque2', height = 1, width = 6)
        #position of the Button on the grid
        SMBButton.grid(row=11,column=2)

        #Labels
        lbl = Label(win, text="LED:", font = myFont)
        lbl.grid(row=12,column=1)

        #Blink LED button
        LEDButton = Button(win, text = 'ON', font = myFont, command = lambda: led_onoff_green(ledpower = True), bg = 'green2', height = 1, width = 6)
        LEDButton.grid(row=12,column=2)

        #Blink LED button
        LEDButton = Button(win, text = 'OFF', font = myFont, command = lambda: led_onoff_green(ledpower = False), bg = 'red2', height = 1, width = 6)
        LEDButton.grid(row=12,column=3)

        #Labels
        lbl = Label(win, text="Program:", font = myFont)
        lbl.grid(row=13,column=1)

        #exit Button
        exitButton = Button(win, text = 'CLOSE', font = myFont, command = close, bg = 'red2', height = 1, width = 6)
        exitButton.grid(row=13, column=2)#columnspan=1)

        #Restart Button
        #exitButton = Button(win, text = 'RESTART', font = myFont, command = restartprogram, bg = 'yellow2', height = 1, width = 6)
        #exitButton.grid(row=8, column=3)#columnspan=1)
        
        #email Button
        #emailButton = Button(win, text = 'Send email help request', font = myFont, command = lambda: send_email(GMAIL_USER, 'KBLT assistance required!', 'Assitance at the KBLT scanner needed ASAP! /The KBLT Team'), bg = 'red2', height = 1, width = 24)
        #emailButton.grid(row=8,column=1,columnspan=2)

        #exit cleanly, i.e. if the LED is on it shuts down when exiting
        win.protocol("WM_DELETE_WINDOW",close)
        
        #Initiate rotation stage button
        #InitRotButton = Button(win, text = 'Init. rot. stage', font = myFont, command = lambda: Initiate_rotation_stage(scan_mode = 1, no_projections = 200), bg = 'green2', height = 1, width = 12, state = DISABLED)
        #position of the Button on the grid
        #InitRotButton.grid(row=1,column=1)

        #Cam button
        #CamButtonOn = Button(win, text = 'Camera On', font = myFont, command = lambda: CamAreaCheck(), bg = 'green2', height = 1, width = 12)
        #position of the Button on the grid
        #CamButtonOn.grid(row=5,column=1)

        #Cam button OFF
        #CamButtonOff = Button(win, text = 'Camera Off', font = myFont, command = lambda: CameraOff(), bg = 'red2', height = 1, width = 12)
        #position of the Button on the grid
        #CamButtonOff.grid(row=5,column=3)

        #Camera Crop button X
        #CropXButton = Button(win, text = 'Crop width 2000 (L/R)', font = myFont, command = lambda: CamAreaCrop(area,200,0), bg = 'bisque2', height = 1, width = 12)
        #position of the Button on the grid
        #CropXButton.grid(row=6,column=1)

        #Camera Crop button Y
        #CropYButton = Button(win, text = 'Crop height 200 (T/B)', font = myFont, command = lambda: CamAreaCrop(area,0,200), bg = 'bisque2', height = 1, width = 12)
        #position of the Button on the grid
        #CropYButton.grid(row=6,column=2)

        #Acq. Tomos button
        #TomoButton = Button(win, text = 'Acq. Tomos', font = myFont, command = lambda: StartScan(area_cr, scale_x_width, scale_y_width), bg = 'bisque2', height = 1, width = 12)
        #position of the Button on the grid
        #TomoButton.grid(row=7,column=1)

        #Trans. Stage Back  button
        #TransStopReset = Button(win, text = 'Reactivate Motors!', font = myFont, command = lambda: emergencyThread(), bg = 'yellow2', height = 1, width = 12)
        #position of the Button on the grid
        #TransStopRest.grid(row=8,column=4)

        #Acq. Refs button
        #RefButton = Button(win, text = 'Acq. Refs', font = myFont, command = lambda: StartRefScan(area_cr, scale_x_width, scale_y_width), bg = 'bisque2', height = 1, width = 12)
        #position of the Button on the grid
        #RefButton.grid(row=9,column=1)

        #loop forever, keeps the GUI running forever
        win.mainloop()
except KeyboardInterrupt:
        print("GUI interrupted via Ctrl+C command!")
        close()
#except NameError:
#        if area_cr is None:
#                print("Please set capture area (by Turning on the camera), prior to starting a scan!")
except:
        #close()
        print("GUI closed normally or via exception!")

