#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import math
import winsound

EXERCISETIME = 60


class MainWidget(QWidget):
    freqChangeSignal = pyqtSignal(object)
    togglerSignal = pyqtSignal()
    """docstring for MainWidget"""
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        


        self.mainLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.barsLayout = QHBoxLayout()
        self.inputLayout = QHBoxLayout()
##        self.frequencyLayout = QHBoxLayout()

        self.input1Layout = QVBoxLayout()
        self.input2Layout = QVBoxLayout()
        self.input3Layout = QVBoxLayout()

        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.start)
        self.buttonLayout.addWidget(self.startButton)

        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.stop)
        self.buttonLayout.addWidget(self.stopButton)

        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)
        self.buttonLayout.addWidget(self.resetButton)

        
        self.minFreqInput = QLineEdit()
        self.minFreqInput.setValidator(QIntValidator(1, 65535, self))
        self.minFreqText = QLabel("Minimum Frequency")

        self.input1Layout.addWidget(self.minFreqText)
        self.input1Layout.addWidget(self.minFreqInput)

        self.maxFreqInput = QLineEdit()
        self.maxFreqInput.setValidator(QIntValidator(1, 65535, self))
        self.maxFreqText = QLabel("Maximum Frequency")

        self.input2Layout.addWidget(self.maxFreqText)
        self.input2Layout.addWidget(self.maxFreqInput)

        self.intervalInput = QLineEdit()
        self.intervalInput.setValidator(QIntValidator(1, 65535, self))
        self.intervalText = QLabel("Interval")
        self.input3Layout.addWidget(self.intervalText)
        self.input3Layout.addWidget(self.intervalInput)

        self.inputLayout.addLayout(self.input1Layout)
        self.inputLayout.addLayout(self.input2Layout)
        self.inputLayout.addLayout(self.input3Layout)

##        self.frequency = QLabel("0")
##        f = QFont("Arial", 40)
##        self.frequency.setFont( f)
##        self.frequencyLayout.addWidget(self.frequency)
##        self.frequencyLayout.setAlignment(Qt.AlignHCenter)
        
        self.progressBar = QProgressBar()
        self.progressBar.setTextVisible(False)

        self.barsLayout.addWidget(self.progressBar)
    
        self.mainLayout.addLayout(self.inputLayout)
        self.mainLayout.addLayout(self.buttonLayout)
##        self.mainLayout.addLayout(self.frequencyLayout)
        self.mainLayout.addLayout(self.barsLayout)
        self.setLayout(self.mainLayout)

        self.setWindowTitle('Rope skipping Metronoom')

    def start(self):
        interval = self.intervalInput.text()
        minFreq = self.minFreqInput.text()
        maxFreq = self.maxFreqInput.text()

        if interval == "":
            interval = "5"

        if minFreq != "" and maxFreq!="":
            self.interval = int(interval)
            self.maxFreq = int(maxFreq)
            self.minFreq = int(minFreq)

            self.timerThread = TimerThread(self.interval, self.minFreq, self.maxFreq)
            self.timerThread.tick.connect(self.update)
            self.timerThread.stopSignal.connect(self.stop)
            self.timerThread.start()

            self.beeperThread = Beeper(self.minFreq, self.freqChangeSignal, self.togglerSignal, self.interval)
            self.beeperThread.start()
        else:
            QMessageBox.warning(self, "Input missing", "No frequency.", QMessageBox.Ok)

    def update(self, currentFreq, updateFreq, percentage):
##        if updateFreq:
##            self.frequency.setText(str(round(currentFreq)))
        self.progressBar.setValue(100*percentage)
        self.freqChangeSignal.emit(currentFreq)


    def stop(self):
        self.timerThread.stop()
        self.togglerSignal.emit()

    def reset(self):
        self.stop()
##        self.frequency.setText("0")
        self.progressBar.setValue(0)
        
        
        
class TimerThread(QThread):

    tick = pyqtSignal(object, object, object)
    stopSignal = pyqtSignal()
    def __init__(self, interval, minFreq, maxFreq):
        QThread.__init__(self)
        self._isStopped = False
        self.interval = interval
        self.minFreq = minFreq
        self.maxFreq = maxFreq

        self.deltaFreq = 2 * (self.interval * (self.maxFreq - self.minFreq))/ EXERCISETIME

    def run(self):
        startTime = time.time()
        currentTime = time.time()
        currentFreq = self.minFreq
        counter = 0
        while counter <= EXERCISETIME/2:
            counter += 1
            if not self._isStopped:
                currentFreq += self.deltaFreq/self.interval
                updateFreq = counter%self.interval == 0
                self.tick.emit(min(currentFreq,self.maxFreq), updateFreq, 2*counter/EXERCISETIME)
            time.sleep(1)

        while counter <= EXERCISETIME:
            counter += 1
            if not self._isStopped:
                currentFreq -= self.deltaFreq/self.interval
                updateFreq = counter%self.interval == 0
                self.tick.emit(min(currentFreq,self.maxFreq), updateFreq, 2 - 2*counter/EXERCISETIME)

            
            time.sleep(1)
        self.stopSignal.emit()
    def stop(self):
        self._isStopped = True

class Beeper(QThread):
    """docstring for Beeper"""
    def __init__(self, freq, freqChangesignal, togglerSignal, interval):
        super(Beeper, self).__init__()
        self.freq = freq
        self.signal = freqChangesignal
        self.signal.connect(self.setFreq)
        self.timerToggle = togglerSignal
        self.timerToggle.connect(self.toggle)
        self.stop = False
        self.timeToSleep = 1/(self.freq/60)
        self.timeToSleepInc = self.timeToSleep/100
        self.freqChange = False
        self.interval = interval
        
    def setFreq(self, newFreq):
        self.freq = newFreq
        self.newTimeToSleep = 1/(self.freq/60)

        

    def run(self):
        while True:
            if not self.stop:
                acc = self.timeToSleep
                timeSlept = 0
                self.playSound()
                while timeSlept < acc:
                    minimum = min(self.interval,self.timeToSleep)
                    time.sleep(minimum)
                    timeSlept += minimum

                    acc = min(self.timeToSleep-minimum,self.newTimeToSleep)
                    self.timeToSleep = self.newTimeToSleep
                # acc = self.timeToSleep
                # print(self.freq)
                # print(self.timeToSleep)
                # print()
                # for i in range(10):
                #     if self.freqChange:
                #         self.freqChange = False
                #         break
                #     else:
                #         time.sleep(self.timeToSleep/10)

    def playSound(self):
        winsound.PlaySound('Ticking-clock-sound.wav', winsound.SND_FILENAME)

    def toggle(self):
        self.stop = True


def get_elapsed(start):
    return time.time() - start

def main():

    app = QApplication(sys.argv)

    w = MainWidget()
    w.resize(450, 150)
    w.move(300, 300)
    
    w.show()
    
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
