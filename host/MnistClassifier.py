# pylint: disable=C0103
""" Implement a MnistClassifier

Simple MNIST classifier uses keras/tensorflow to create, train and
evaluate the neural net

@author: Raphael Zingg zing@zhaw.ch
@copyright: 2018 ZHAW / Institute of Embedded Systems
"""
import tensorflow as tf
import numpy as np


class MnistClassifier:
    def __init__(self):
        self.model = []

        # traing data
        self.trainVec = []
        self.trainLabel = []

        # test data
        self.testVecInt = []
        self.testVec = []
        self.testLabel = []

    def createModel(self):
        """ Create a model with 3 dense layers
        This model is not optimized or anything to predict MNIST,
        it is just a example model to show how a keras model can
        be ported to the ARM-CMSIS NN library functions
        
        Note: tanh and sigmoid implementations of arm are parsed
              but accuracy is bad, due to lookup table with low resolution
              and bug in tanh act see: https://github.com/ARM-software/CMSIS_5/issues/470
              therefore use only relu to get similar responses on host as ontarget!
        Note: softmax layer is only allowed as last layer!
        """
        self.model = tf.keras.models.Sequential()
        self.model.add(tf.keras.layers.Dense(30))
        self.model.add(tf.keras.layers.Activation('relu'))
        self.model.add(tf.keras.layers.Dense(18))
        self.model.add(tf.keras.layers.Activation('relu'))
        self.model.add(tf.keras.layers.Dense(10))
        self.model.add(tf.keras.layers.Activation('softmax'))

        # set up optimizer
        adam = tf.keras.optimizers.Adam(
            lr=0.005, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

        # compile the model
        self.model.compile(optimizer=adam,
                           loss='sparse_categorical_crossentropy',
                           metrics=['accuracy'])

    def importAndPrepData(self):
        """ Import the MNIST data set and stores it in the class properties
        """
        # split the dataset into train and test data, scale into float
        mnist = tf.keras.datasets.mnist
        (x_train, self.trainLabel), (self.testVecInt,
                                     self.testLabel) = mnist.load_data()
        x_train, x_test = x_train / 255.0, self.testVecInt / 255.0

        self.trainVec = x_train.reshape(x_train.shape[0], 28*28)
        self.testVec = x_test.reshape(x_test.shape[0], 28*28)

    def train(self):
        """ Train the model on the training data
        """
        self.model.fit(self.trainVec, self.trainLabel,
                       batch_size=50, epochs=5, verbose=0)

    def predict(self, mnistImageIdx):
        """ Predict the mnist image provided to the function
        """
        currPicture = np.array(self.testVec[mnistImageIdx])
        currPicture = currPicture.reshape(1, 28*28)
        return self.model.predict(currPicture)

    def reloadModel(self):
        """ Replace the weights of the model with the quantized one
        """
        # load json and create model
        json_file = open('trainedNet/model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = tf.keras.models.model_from_json(loaded_model_json)

        # load weights into new model
        self.model.load_weights("trainedNet/model.h5")

        # compile the model
        self.model.compile(optimizer='adam',
                           loss='sparse_categorical_crossentropy',
                           metrics=['accuracy'])

    def storeModel(self):
        """ Store the model and weights
        """
        # store model to a json file
        modelJson = self.model.to_json()
        with open("trainedNet/model.json", "w") as json_file:
            json_file.write(modelJson)
        self.model.save_weights("trainedNet/model.h5")
