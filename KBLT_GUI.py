#!/usr/bin/python

from kblt import scan as kblt
####### packages needed for the GUI ####
from tkinter import *
import tkinter.font

## GUI DEFINITIONS ##
win = Tk()
win.title("KBLT")
myFont = tkinter.font.Font(family = 'Helvetica', size = 12, weight = "bold")

#Initiate web camera
#kblt.CamInit(cam_no=0, x_res=720, y_res=480)

#Set rotation parameters
kblt.Initiate_rotation_stage(scan_mode = 4, no_projections=800)
#kblt.Initiate_rotation_stage(scan_mode = 1, no_projections=200)

#GUI starts below!
try:
        
        #Labels
        lbl = Label(win, text="Cameras: (X, W, Y, H)", font = myFont)
        lbl.grid(row=1,column=1)
        
        #Cam button
        CamButtonOn = Button(win, text = 'Acq.', font = myFont, command = lambda: kblt.CamAreaOnThread(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get())), bg = 'green2', height = 1, width = 6)
        #CamButtonOn = Button(win, text = 'Acq.', font = myFont, command = lambda: kblt.CamAreaCheck(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get())), bg = 'green2', height = 1, width = 6)
        CamButtonOn.grid(row=1,column=2)

        #Labels
        large_font = ('Verdana', 15)
        e7 = Entry(win, width = 6, font=large_font)
        e7.insert(10, "0")
        e7.grid(row=1, column=3)

        #Labels
        large_font = ('Verdana', 15)
        e8 = Entry(win, width = 6, font=large_font)
        e8.insert(10, "720")
        e8.grid(row=1, column=4)
        
        #Labels
        large_font = ('Verdana', 15)
        e9 = Entry(win, width = 6, font=large_font)
        e9.insert(10, "0")
        e9.grid(row=1, column=5)

        #Labels
        large_font = ('Verdana', 15)
        e10 = Entry(win, width = 6, font=large_font)
        e10.insert(10, "480")
        e10.grid(row=1, column=6)

        #PiCamButtonOn = Button(win, text = 'Init. Cam.', font = myFont, command = lambda: kblt.CamInit(cam_no=0, x_res=720, y_res=480), bg = 'green2', height = 1, width = 6)
        #PiCamButtonOn.grid(row=1,column=7)

        PiCamButtonOn = Button(win, text = 'Surv.', font = myFont, command = lambda: kblt.PiCamOnThread(), bg = 'yellow2', height = 1, width = 6)
        PiCamButtonOn.grid(row=1,column=8)

        #Labels
        lbl = Label(win, text="Light Source:", font = myFont)
        lbl.grid(row=2,column=1)

        #Power up lamp relay button
        SwitchOnLightRelayButton = Button(win, text = 'ON', font = myFont, command = lambda: kblt.relay_switch(send = True), bg = 'green2', height = 1, width = 6)
        SwitchOnLightRelayButton.grid(row=2,column=2)

        #Shutdown lamp relay button
        SwitchOffLightRelayButton = Button(win, text = 'OFF', font = myFont, command = lambda: kblt.relay_switch(send = False), bg = 'red2', height = 1, width = 6)
        SwitchOffLightRelayButton.grid(row=2,column=3)

        #Resetting the lamp relay button
        SwitchResetLightRelayButton = Button(win, text = 'RESET', font = myFont, command = lambda: kblt.relay_switch_manual(), bg = 'yellow2', height = 1, width = 6)
        SwitchResetLightRelayButton.grid(row=2,column=4)

        #Language audio selector
        options_var = StringVar()
        options_var.set("Audio")
        contents = {'English f', 'English m', 'Swedish m', 'French m', 'Italian f', 'Italian m', 'German m', 'Slovenian f', 'Croatian f', 'Mandarin m', 'Russian m'}
        dropdown = OptionMenu(win, options_var, *contents)
        dropdown.grid(row=2,column=5)
        
        #print language
        #LangButton = Button(win, text = 'Print language', font = myFont, command = lambda: kblt.printparam(options_var.get()), bg = 'yellow2', height = 1, width = 6)
        #LangButton = Button(win, text = 'Print language', font = myFont, lang=options_var.get(), bg = 'yellow2', height = 1, width = 6)
        #LangButton = Button(win, text = 'Play language', font = myFont, command = lambda: kblt.AudioMessage(lang=options_var.get()), bg = 'yellow2', height = 1, width = 6)
        LangButton = Button(win, text = 'Set', font = myFont, command = lambda: kblt.setlang(language=options_var.get()), bg = 'yellow2', height = 1, width = 6)
        LangButton.grid(row=2,column=6)

        #Labels
        lbl = Label(win, text="Rotation Stage:", font = myFont)
        lbl.grid(row=3,column=1)
        
        #Power up rotation stage button
        SwitchOnButton = Button(win, text = 'ON', font = myFont, command = lambda: kblt.iot_switch(send = True), bg = 'green2', height = 1, width = 6)
        SwitchOnButton.grid(row=3,column=2)

        #Shutdown rotation stage button
        SwitchOffButton = Button(win, text = 'OFF', font = myFont, command = lambda: kblt.iot_switch(send = False), bg = 'red2', height = 1, width = 6)
        SwitchOffButton.grid(row=3,column=3)

        #Labels
        lbl = Label(win, text="Rotate Sample (deg.):", font = myFont)
        lbl.grid(row=4,column=1)

        #Labels
        large_font = ('Verdana', 15)
        e3 = Entry(win, width = 6, font=large_font)
        e3.insert(10, "90")
        e3.grid(row=4, column=2)
               
        #Rotate Plus button
        #for scan mode = 4
        RotatePlusButton = Button(win, text = 'CW', font = myFont, command = lambda: kblt.Rotate90deg(step_count= int(int(e3.get())*200*4/360), direction=1), bg = 'bisque2', height = 1, width = 6)
        #for scan mode = 1, Full
        #RotatePlusButton = Button(win, text = 'CW', font = myFont, command = lambda: kblt.Rotate90deg(step_count= int(int(e3.get())*200*1/360), direction=1), bg = 'bisque2', height = 1, width = 6)
        RotatePlusButton.grid(row=4,column=3)

        #Rotate Minus button
        #for scan mode = 4
        RotatePlusButton = Button(win, text = 'CCW', font = myFont, command = lambda: kblt.Rotate90deg(step_count= int(int(e3.get())*200*4/360), direction=0), bg = 'bisque2', height = 1, width = 6)
        #for scan mode = 1, Full
        #RotatePlusButton = Button(win, text = 'CCW', font = myFont, command = lambda: kblt.Rotate90deg(step_count= int(int(e3.get())*200*1/360), direction=0), bg = 'bisque2', height = 1, width = 6)
        RotatePlusButton.grid(row=4,column=4)

        #Labels
        lbl = Label(win, text="Translation Stages:", font = myFont)
        lbl.grid(row=5,column=1)

        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Light', font = myFont, command = lambda: kblt.relay_switch_trans(send = True, pinact = 12, pininact2 = 25, pininact3 = 27, pininact4 = 15), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=2)
      
        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Sample', font = myFont, command = lambda: kblt.relay_switch_trans(send = True, pinact = 25, pininact2 = 12, pininact3 = 27, pininact4 = 15), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=3)
        
        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Screen', font = myFont, command = lambda: kblt.relay_switch_trans(send = True, pinact = 27, pininact2 = 12, pininact3 = 25, pininact4 = 15), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=4)

        #Power up trans stage button
        SwitchOnTransButton = Button(win, text = 'Camera', font = myFont, command = lambda: kblt.relay_switch_trans(send = True, pinact = 15, pininact2 = 12, pininact3 = 27, pininact4 = 25), bg = 'green2', height = 1, width = 6)
        SwitchOnTransButton.grid(row=5,column=5)

        #Shutdown trans stage button
        SwitchOffTransButton = Button(win, text = 'OFF', font = myFont, command = lambda: kblt.relay_switch_trans(send = False, pinact = 15, pininact2 = 12, pininact3 = 27, pininact4 = 25), bg = 'red2', height = 1, width = 6)
        SwitchOffTransButton.grid(row=5,column=6)

        #Labels
        lbl = Label(win, text="Translate active motor (mm):", font = myFont)
        lbl.grid(row=9,column=1)

        #Labels
        large_font = ('Verdana', 15)
        e2 = Entry(win, width = 6, font=large_font)
        e2.insert(10, "10")
        e2.grid(row=9, column=2)

        #Trans. Stage Front button
        TransFrontButton = Button(win, text = 'LEFT', font = myFont, command = lambda: kblt.TranslationStageThread(direction = True, trans_step = int(int(e2.get())*1*768/92)), bg = 'bisque2', height = 1, width = 6)
        TransFrontButton.grid(row=9,column=3)

        #Trans. Stage Back  button
        TransBackButton = Button(win, text = 'RIGHT', font = myFont, command = lambda: kblt.TranslationStageThread(direction = False, trans_step = int(e2.get())*1*768/92), bg = 'bisque2', height = 1, width = 6)
        TransBackButton.grid(row=9,column=4)
        
        #Trans. Emergency  button
        #TransStop = Button(win, text = 'Emergency STOP!', font = myFont, command = lambda: emergencyThread(), bg = 'red2', height = 1, width = 12, state = DISABLED)
        #position of the Button on the grid
        #TransStop.grid(row=5,column=3)

        #Labels        
        lbl = Label(win, text="Sample Name & User Email", font = myFont).grid(row=10,column=1)
        large_font = ('Verdana', 15)
        e1 = Entry(win, width = 6, font = large_font)
        e1.insert(10, "Default")
        e1.grid(row=10, column=2)
        #PrintButton = Button(win, text = 'PRINT', font = myFont, command = lambda: kblt.printparam(e1.get()), bg = 'bisque2', height = 1, width = 6).grid(row=10, column=3)

        #Labels        
        #lbl = Label(win, text="User email:", font = myFont).grid(row=11,column=1)
        large_font = ('Verdana', 15)
        e0 = Entry(win, width = 24, font = large_font)
        e0.insert(10, "emanuel.larsson@gmail.com")
        e0.grid(row=10, column=3, columnspan=4)
        #PrintButton = Button(win, text = 'PRINT', font = myFont, command = lambda: kblt.printparam(e0.get()), bg = 'bisque2', height = 1, width = 6).grid(row=11, column=3)

        #Labels
        lbl = Label(win, text="Tomo. Scan (Reps & T.Sep. & T.Count From & No. Proj.):", font = myFont)
        lbl.grid(row=12,column=1)
        
        #Labels, #Repeated scans
        large_font = ('Verdana', 15)
        e4 = Entry(win, width = 6, font = large_font)
        e4.insert(10, "1")
        e4.grid(row=12, column=2)

        #Labels, Time separation in seconds
        large_font = ('Verdana', 15)
        e5 = Entry(win, width = 6, font = large_font)
        e5.insert(10, "0")
        e5.grid(row=12, column=3)

        #Labels, No. Acq. Projections
        large_font = ('Verdana', 15)
        tc = Entry(win, width = 6, font = large_font)
        tc.insert(10, "0")
        tc.grid(row=12, column=4)
        
        #Labels, No. Acq. Projections
        large_font = ('Verdana', 15)
        e6 = Entry(win, width = 6, font = large_font)
        e6.insert(10, "200")
        e6.grid(row=12, column=5)

        #Acq. Rep. button
        ScanRepButton = Button(win, text = 'START', font = myFont, command = lambda: kblt.StartAllScans(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get()), manual_sample_name = e1.get(), noproj_acq = int(e6.get()), tomo_reps = int(e4.get()), time_diff = int(e5.get()), tomo_count_from = int(tc.get()), email_recipent = str(e0.get()) ), bg = 'green2', height = 1, width = 6)
        ScanRepButton.grid(row=12,column=6)

        #Acq. Manual Ref. scan button
        ManRefButton = Button(win, text = 'FLATS', font = myFont, command = lambda: kblt.ManualRefScan(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get()), manual_sample_name = e1.get()), bg = 'yellow2', height = 1, width = 6)
        ManRefButton.grid(row=12,column=7)

        #Acq. Manual Dark scan button
        ManDarkButton = Button(win, text = 'DARKS', font = myFont, command = lambda: kblt.ManualDarkScan(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get()), manual_sample_name = e1.get()), bg = 'blue2', height = 1, width = 6)
        ManDarkButton.grid(row=12,column=8)

        #Labels
        lbl = Label(win, text="LED:", font = myFont)
        lbl.grid(row=13,column=1)

        #Blink LED button
        LEDButton = Button(win, text = 'ON', font = myFont, command = lambda: kblt.led_onoff_green(ledpower = True), bg = 'green2', height = 1, width = 6)
        LEDButton.grid(row=13,column=2)

        #Blink LED button
        LEDButton = Button(win, text = 'OFF', font = myFont, command = lambda: kblt.led_onoff_green(ledpower = False), bg = 'red2', height = 1, width = 6)
        LEDButton.grid(row=13,column=3)

        #Labels
        lbl = Label(win, text="Program:", font = myFont)
        lbl.grid(row=14,column=1)

        #exit Button
        exitButton = Button(win, text = 'CLOSE', font = myFont, command = kblt.close, bg = 'red2', height = 1, width = 6)
        exitButton.grid(row=14, column=2)#columnspan=1)

        #exit cleanly, i.e. if the LED is on it shuts down when exiting
        win.protocol("WM_DELETE_WINDOW", kblt.close)
   
        #loop forever, keeps the GUI running forever
        win.mainloop()
        
except KeyboardInterrupt:
        print("GUI interrupted via Ctrl+C command!")
        kblt.close()
#except NameError:
#        if area_cr is None:
#                print("Please set capture area (by Turning on the camera), prior to starting a scan!")
#except:
        #close()
#        print("GUI closed normally or via exception!")
