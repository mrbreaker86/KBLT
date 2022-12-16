GUI - Graphical User Interface
==============================

	.. image:: photos/gui.png
	  :width: 800
	  :alt: KBLT GUI

example code for setting up the button Acq. and calling the function CamAreaOnThread: ::

	$ CamButtonOn = Button(win, text = 'Acq.', font = myFont, command = lambda: kblt.CamAreaOnThread(x0=int(e7.get()), xw=int(e8.get()), y0=int(e9.get()), yh=int(e10.get())), bg = 'green2', height = 1, width = 6)