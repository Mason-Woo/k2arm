""" Script used to:
- create a simple MNIST classifier with keras

- create a .h and .c file with represents the created keras model and can be
  used to run the keras model with the ARM CMSIS NN functions

- call a build and flash script

- compare the predictions of MNSIT pictures of the original net and the net on the
  embedded target, using UART communication

@author: Raphael Zingg zing@zhaw.ch
@copyright: 2018 ZHAW / Institute of Embedded Systems
"""
import subprocess
import numpy as np
import sys, getopt
import matplotlib.pyplot as plt
from MnistClassifier import MnistClassifier
from Keras2arm import Keras2arm
from M4Driver import M4Driver


# ---------------------------------------------------------------------------------------------------
#                                          default settings 
# ---------------------------------------------------------------------------------------------------
generateCode = False
compareThroughSerial = False
serDev = '/dev/ttyUSB2'
fixPointBits = 15  # use q7 or q15 bits functions

# compare using UART4 of the STM32F429
nrTestSamples = 10  # number of test samples to compare (max 10000)

# ---------------------------------------------------------------------------------------------------
#                                           parse input 
# ---------------------------------------------------------------------------------------------------
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# check if user wants to generate code or copare through serial
try:
    opts, args = getopt.getopt(sys.argv[1:],'hg:c:r:s:', ['generate=','run=','ser='])
except getopt.GetoptError:
    print('usage: $ main.py -g <True> -c <False> -r <True> -s </dev/ttyUSB2>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('usage: $ main.py -g <True> -c <False> -r <True> -s </dev/ttyUSB2>')
        sys.exit()
    elif opt in ('-g', '--generate'):
        generateCode = True
        fixPointBits = int(arg)
        if fixPointBits != 7 and fixPointBits != 15:
            print('only q7 or q15 is supportet!')
            sys.exit(2)
    elif opt in ('-r', '--run'):
        compareThroughSerial = True
        serDev = arg     


# set maximal integer output range for arm fully connected layers (can be tuned if required)
if fixPointBits == 7:
    stopBit = 4
else:
    stopBit = 8
# ---------------------------------------------------------------------------------------------------
#                                          init classes
# ---------------------------------------------------------------------------------------------------
mc = MnistClassifier()
k2arm = Keras2arm(outputFilePath='../target/')
mc.importAndPrepData()
mc.reloadModel()

# ---------------------------------------------------------------------------------------------------
#                         train a keras model, get specs of the keras model
# ---------------------------------------------------------------------------------------------------
if generateCode:
    mc.createModel()
    mc.train()
    mc.storeModel()


    classifier = mc.model
    evalData = [mc.testVec, mc.testLabel]

    # get number of dense layers of the classifier
    numberOfDenseLayers = len(k2arm.getDenseLayersInformation(mc.model))

    # set variables of the parser
    k2arm.fixPointBits = fixPointBits
    k2arm.numberOfDenselayers = numberOfDenseLayers

# ---------------------------------------------------------------------------------------------------
#               quantize the weights into Q Formats, calculate output format of layers
# ---------------------------------------------------------------------------------------------------
    k2arm.quantizeWeights(model=classifier)
    k2arm.findOutputFormat(startBit=0, stopBit=stopBit,
                        model=classifier, evalData=evalData)

# ---------------------------------------------------------------------------------------------------
#                                            write C files
# ---------------------------------------------------------------------------------------------------
    k2arm.storeWeights()
    k2arm.storeDimension()
    k2arm.storeOutShiftParams()
    k2arm.storeNetFunction(model=classifier)
    k2arm.storeBitSize()
    print('Done, all files generated')

acc = mc.model.evaluate(mc.testVec, mc.testLabel, verbose=0)[1]*100
print('MNIST classifier accuracy on host: ' + str(acc) + '%')

# ---------------------------------------------------------------------------------------------------
#                               get the prediction of nrTestSamples images
# ---------------------------------------------------------------------------------------------------
if compareThroughSerial == True:
    predictionHost = np.zeros(nrTestSamples)
    predictionM4 = np.zeros(nrTestSamples)
    errorCountHost = 0
    errorCountM4 = 0
    m4d = M4Driver()
    # open the serial connection
    try:
        if m4d.openSerial(str(serDev)) is False:
            sys.exit(2)
    except AttributeError:
        print('Cant open serial device, check if serDev is correct!')
        sys.exit(2)
    print('Comparing ' + str(nrTestSamples) + ' MNIST predictions, this takes a while')
    m4d.ser.flushInput()
    m4d.ser.flushOutput()
    for i in range(0, nrTestSamples):

        # get prediction from classifier on host
        predictionHost[i] = np.argmax(mc.predict(i))

        # get prediction from classifier on m4
        predictionM4[i] = int(m4d.predict(mc.testVecInt[i].reshape(1, 28*28)))

        # check if prediction was correct of host
        if predictionHost[i] != mc.testLabel[i]:
            errorCountHost = errorCountHost + 1

        # check if the prediction was correct of M4
        if predictionM4[i] != mc.testLabel[i]:
            errorCountM4 = errorCountM4 + 1

        plt.imshow(mc.testVecInt[i], cmap=plt.get_cmap('gray'))
        plt.title('Label:' + str(mc.testLabel[i]) + ' Pred Host:' +
                    str(predictionHost[i]) + ' Pred Target:' + str(predictionM4[i]))
        plt.show()

        # calc acc
        accM4 = str(100 - (errorCountM4 / (i + 1)) * 100)
        accHost = str(100 - (errorCountHost / (i + 1)) * 100)

    # print evaluation of the neural net
    print('Done ' + str(i) + ' Images tested \nAccuracy on host:'
          + str(accHost) + '%\n'
          + 'Accuracy on target:' + str(accM4) + '%\n')


print('Done')
