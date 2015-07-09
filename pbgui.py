#!/usr/bin/env python
 
import numpy as np
import pyaudio
import math
import time
import random 

import sys
from PyQt4 import QtGui, QtCore

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

initial_phase = 0.0
initial_frequency = 83
initial_ampl_l = 0.05
initial_ampl_r = 0.05

class ToneGenerator(object):
 
    def __init__(self, samplerate=44100, frames_per_buffer=4096):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.phase_r = 0.0
 
    # sin([buffer_offset,...,buffer_offset+frames_per_buffer]*2*pi*f/samplerate + phase)
    def sinewave_l(self):
        xs = np.arange(self.buffer_offset_l,
                          self.buffer_offset_l + self.frames_per_buffer)
        out = self.amplitude_l * np.sin(xs * self.omega_l)
        self.buffer_offset_l += self.frames_per_buffer
        return out

    def sinewave_r(self):
        xs = np.arange(self.buffer_offset_r,
                          self.buffer_offset_r + self.frames_per_buffer)
        out = self.amplitude_r * np.sin(xs * self.omega_r + self.phase_r)
        self.buffer_offset_r += self.frames_per_buffer
        return out
 
    def callback(self, in_data, frame_count, time_info, status):
        left = self.sinewave_l().astype(np.float32)
        right = self.sinewave_r().astype(np.float32)

        #interweave left and right to create stereo
        data = np.empty((left.size + right.size,), dtype = left.dtype)
        data[0::2] = left
        data[1::2] = right

        return data.tostring(), pyaudio.paContinue
 
    """
    Play parameterized sine waves on stereo (left and right)
    """
    def play(self, frequency_l, amplitude_l, frequency_r, amplitude_r, phase):
        self.omega_l = float(frequency_l) * (math.pi * 2) / self.samplerate
        self.amplitude_l = amplitude_l
        self.buffer_offset_l = 0

        self.frequency_r = frequency_r
        self.omega_r = float(frequency_r) * (math.pi * 2) / self.samplerate
        self.amplitude_r = amplitude_r
        self.buffer_offset_r = 0

        self.phase_r = phase*2.0*np.pi/360

        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=2,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)

    def halt(self):
        self.stream.stop_stream()
        self.stream.close()

class Example(QtGui.QWidget):
    def __init__(self, controller):
        super(Example, self).__init__()

        self.controller = controller

        self.initUI()

    def initUI(self):



        f = QtGui.QLabel("Frequency",self)
        freq = QtGui.QLineEdit(str(initial_frequency),self)
        p = QtGui.QLabel("Phase",self)
        phase = QtGui.QLineEdit(str(initial_phase),self)
        al = QtGui.QLabel("Amplitude (Left)",self)
        ampl_l = QtGui.QLineEdit(str(initial_ampl_l),self)
        ar = QtGui.QLabel("Amplitude (Right)",self)
        ampl_r = QtGui.QLineEdit(str(initial_ampl_r),self)
        button = QtGui.QPushButton("Apply", self)


        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(p)
        vbox.addWidget(phase)
        vbox.addWidget(f)
        vbox.addWidget(freq)
        vbox.addWidget(al)
        vbox.addWidget(ampl_l)
        vbox.addWidget(ar)
        vbox.addWidget(ampl_r)
        vbox.addWidget(button)

        self.setLayout(vbox)

        phase.textChanged.connect(self.controller.phaseChanged)
        freq.textChanged.connect(self.controller.freqChanged)
        ampl_l.textChanged.connect(self.controller.ampl_lChanged)
        ampl_r.textChanged.connect(self.controller.ampl_rChanged)
        button.clicked.connect(self.controller.apply)

        self.setFocus()

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("PB")
        self.show()

class Controller():
    def __init__(self, generator):
        self.generator = generator
        self.phase = initial_phase
        self.frequency = initial_frequency
        self.ampl_l = initial_ampl_l
        self.ampl_r = initial_ampl_r

    def phaseChanged(self, value):
        if value:
            self.phase = float(value)

    def freqChanged(self, value):
        if value:
            self.frequency = float(value)

    def ampl_lChanged(self, value):
        if value:
            self.ampl_l = float(value)

    def ampl_rChanged(self, value):
        if value:
            self.ampl_r = float(value)

    def apply(self):
        self.generator.halt()
        time.sleep(0.1)
        self.generator.play(self.frequency, self.ampl_l, self.frequency, self.ampl_r, self.phase)


def main():
    app = QtGui.QApplication(sys.argv)

    generator = ToneGenerator()
    generator.play(initial_frequency,initial_ampl_l,initial_frequency,initial_ampl_r,initial_phase)

    c = Controller(generator)
    ex = Example(c)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()