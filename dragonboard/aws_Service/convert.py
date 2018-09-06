#! /usr/bin/env python

import subprocess
#from gtts import gTTS

#input_text = 'ask coffee machine make short coffee'
#print("[convert]: Converting text to "+input_text)
#tts = gTTS(input_text, lang='en')
#tts.save('file.mp3')
#print("[convert]: Generated MP3 file!")

wavfile = 'alexa_shortCoffee.wav'
mp3file = 'alexa_shortCoffee.mp3'
print("[convert]: Converting MP3 to WAV...")
subprocess.call(['ffmpeg','-y', '-i', mp3file, '-acodec', 'pcm_s16le', '-ar', '16000', wavfile])
subprocess.call(['aplay', wavfile])
print("[convert]: Done!")