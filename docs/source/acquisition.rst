Acquisition
===========

KBLT Python code for acqusition can be found on GitHub: 
:cite:`larsson_kblt`

=============
StartAllScans
=============

	.. method:: scan.StartAllScans(x0, xw, y0, yh, manual_sample_name, noproj_acq, tomo_reps, time_diff, tomo_count_from, email_recipent)

	.. automodule:: scan.StartAllScans
		:members:
		:show-inheritance:

=========
StartScan
=========

	.. method:: scan.StartScan(x0, xw, y0, yh, proj_skip)

	.. automodule:: scan.StartScan
		:members:
		:show-inheritance:

==========================
Initiate Translation Stage
==========================

	.. method:: scan.Initiate_translation_stage(direction, trans_step, GPIOno_trans_on, GPIOno_trans_off)

	.. automodule:: scan.Initiate_translation_stage
		:members:
		:show-inheritance:

=======================
Initiate Rotation Stage
=======================

	.. method:: scan.Initiate_rotation_stage(scan_mode, no_projections)

	.. automodule:: scan.Initiate_rotation_stage
		:members:
		:show-inheritance:

	The code has been reproduced from ROTOTRON 2004. Raspberry pi stepper motor tutorial. Guide available on: `ROTOTRON_guide`_.
		.. _ROTOTRON_guide: https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/

============
LED blinking
============

	.. method:: scan.led_blinking_green(led_port)

	.. automodule:: scan.led_blinking_green
		:members:
		:show-inheritance:

===============
LED solid light
===============

	.. method:: scan.led_onoff_green(ledpower, led_port)

	.. automodule:: scan.led_onoff_green
		:members:
		:show-inheritance:

============
AudioMessage
============

	.. method:: scan.AudioMessage(lang)

	.. automodule:: scan.AudioMessage
		:members:
		:show-inheritance: