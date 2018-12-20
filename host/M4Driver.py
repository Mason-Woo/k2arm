""" Driver class to interact with the CT-Board

Uses serial UART connection to exchange data and commands
Hardware: https://ennis.zhaw.ch/wiki/doku.php based on STM32F29-Disco

Before using the functions of this driver class make sure that the hardware
is connected and runs with the correct firmware.
Firmware and keil project is stored in ../target/

@author: Raphael Zingg zing@zhaw.ch
@copyright: 2018 ZHAW / Institute of Embedded Systems
"""

import struct
import serial as ser


class M4Driver:

    def __init__(self):
        self.ser = []

    def openSerial(self, serialPort):
        """Open a serial connection and perform a handshake

        serialPort : (str) of the serial device eg: COM3 or /dev/ttyUSB0
        returns: True for success, False otherwise.
        """
        # open serial port and set properties
        try:
            self.ser = ser.Serial(serialPort, baudrate=115200, timeout=10)
        except ser.SerialException:
            print("SerialException, cant open port!")
            self.ser.close()
            self.ser.open()

        # handshake: write 's' receive 'X'
        try:
            self.ser.write(b's')
            ret = self.ser.read(2)
            if ret.decode("utf-8")[0] == 'X':
                print('Connection open!')
                return True
        except IndexError:
            print('Handshake failed, check if firmware is running!')
            self.ser.close()
            return False

    def predict(self, mnistIntImage):
        """ Returns prediction of the mnist image mnistIntImage

        mnistIntImage:  (np.array[1][28*28]) with a MNIST image
        returns: prediction read from the serial device
        """
        prediction = []

        # write command c and send the data
        self.ser.write(b'c')
        for i in range(0, 28*28):
            self.ser.write(struct.pack('!B', mnistIntImage[0][i]))

        # read the prediction back
        prediction = self.ser.read(1)
        if prediction != []:
            prediction = prediction.decode("utf-8")[0]
        else:
            print('Error no prediction from M4')

        return prediction
