#http://pydub.com/
from pydub import AudioSegment

path = '/home/pi/KBLT_scanner/audio/'
name = 'SWE_male'

audio = AudioSegment.from_file(path + name + '.m4a')
audio.export(path + name + '.mp3', format='mp3')
