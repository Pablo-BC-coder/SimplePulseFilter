'''This program filters an audio recording based on a pulse recorded in the same environment as that audio recording.
    Copyright (C) 2024  Pablo B. Claudino

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import wave
import numpy as np
import matplotlib.pyplot as plt

print("Simple Pulse Filter\nCopyright (C) 2024  Pablo B. Claudino\n")

pulseFilename = input("Pulse file path: ")
audioFilename = input("Audio file path: ")

#pulse = wave.Wave_read("Pulse-l.wav")
pulse = wave.Wave_read(pulseFilename)
# pulse = wave.Wave_read("440hz.wav")
#audio = wave.Wave_read("H-Info 4.wav")
audio = wave.Wave_read(audioFilename)

print("Sample width:", pulse.getsampwidth())
print("Channels:", pulse.getnchannels())
print("Framerate:", pulse.getframerate())
# print(pulse.getfp().read())

chns = pulse.getnchannels()

pulseArray = pulse.getfp().read()
audioArray = audio.getfp().read()

def byteArrayToIntArray(array, width):
    intArray = []
    for i in range(0, len(array), width):
        # if array[i + 1] & 0x8000: print((~ (((array[i + 1] << 8) | array[i]) - 1)) & 0xffff)
        if array[i + 1] & 0x80: intArray.append(- ((~ (((array[i + 1] << 8) | array[i]) - 1)) & 0xffff))
        else: intArray.append((array[i + 1] << 8) | array[i])
    return intArray

def intArrayToBytes(array, width):
    bt = bytearray()
    for i in array:
        for j in range(width):
            bt.append((i >> 8*j) & 0xff)
    return bt

def extractChannel(array, width, channel):
    return array[channel::width]

pulseList = byteArrayToIntArray(pulseArray, pulse.getsampwidth())
audioList = byteArrayToIntArray(audioArray, pulse.getsampwidth())

print(pulseList[0])

pulse.close()
audio.close()

onePulse = np.array(extractChannel(pulseList, 2, 0)) / 2**15
oneAudio = np.array(extractChannel(audioList, 2, 0)) / 2**15

plt.plot(oneAudio)
plt.show()

# onePulse = np.zeros(44100); onePulse[0] = 1; onePulse[22050] = -0.5

padPulse = np.pad(onePulse, len(oneAudio) * 2 - len(onePulse))[len(oneAudio) * 2 - len(onePulse):]

outAudio = np.fft.irfft((1 / np.fft.rfft(padPulse)) * np.fft.rfft(np.pad(oneAudio, len(oneAudio))[len(oneAudio):])).real
# outAudio = np.fft.irfft((1) * np.fft.rfft(np.pad(oneAudio, len(oneAudio))[len(oneAudio):]))

outAudio = np.array(outAudio * 2**15, np.int16)[:len(outAudio) >> 1]

plt.plot(outAudio)
plt.show()


# onePulse *= 2

def testWriting():
    pulse = wave.Wave_write(pulseFilename)
    pulse.setnchannels(chns)
    pulse.setsampwidth(2)
    pulse.setframerate(44100)
    pulse.writeframes(intArrayToBytes(pulseList, 2))
    pulse.close()

def saveAudio(file, array, channels = 1, framerate = 44100, width = 2):
    pulse = wave.Wave_write(file)
    pulse.setnchannels(channels)
    pulse.setsampwidth(width)
    pulse.setframerate(framerate)
    pulse.writeframes(intArrayToBytes(array, 2))
    pulse.close()


#saveAudio("onePulse.wav", onePulse)

#saveAudio("H-Info_Correct.wav", outAudio)
saveAudio(input("Output filename (without 'WAV' extension): ") + ".wav", outAudio)

print("Saved!")

import simpleaudio

# simpleaudio.play_buffer(pulseList, 1, 2, 44100)

# simpleaudio.play_buffer(pulseArray, 1, 2, 44100)
simpleaudio.play_buffer(intArrayToBytes(pulseList, 2), chns, 2, 44100)