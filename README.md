# k2arm
A simple project to show how a custom keras model can be automatically translated into c-code.
The generated c-code can, in combination with the [ARM-CMSIS-NN](http://www.keil.com/pack/doc/CMSIS_Dev/NN/html/index.html) functions, be used
to run neural-net calculations in an efficient way on an embedded micro-controller such as the CORTEX-M4.

This repository has also example firmware which runs on the [STM32F4-Discorevy Board](https://www.st.com/en/evaluation-tools/stm32f4discovery.html). Part of the firmware was generated with [cubeMX](https://www.st.com/en/development-tools/stm32cubemx.html). The example project has a MNIST classifier which can classify handwritten digits.

## Requirements
 - arm-none-eabi-gcc [(Install problems on ubuntu 18.04 )](https://github.com/bbcmicrobit/micropython/issues/514#issuecomment-404759614)
 - python: 3.6
 - tensorflow 1.10.0
 - ubuntu 18.04
 - [STM32F4-Discorevy Board](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)
 - [TLL-232R Converter](https://ch.farnell.com/ftdi/ttl-232r-3v3/kabel-usb-ttl-pegel-seriell-umsetzung/dp/1329311?mckv=s89FAqCVd_dc|pcrid|251391972450|kword|ttl-232r-3v3|match|p|plid|&CMP=KNC-GCH-GEN-SKU-MDC-German&gclid=EAIaIQobChMIjfS4hcyo2wIVxDobCh14jwVBEAAYAiAAEgLMo_D_BwE)

## Setup
Clone with submodules:
```
git clone --recurse-submodules https://github.com/InES-HPMM/k2arm.git
```

Build st-flash:

```
cd k2arm/target/stlink.git
make
```

## Build firmware with default net
Build firmware with default neural net:
```
cd ../target
make
```
Connect the discovery board, flash firmware with default net:
```
./stlink.git/build/Release/st-flash --format ihex write ./build/cubeMx.hex
```

## Run default parsed net, compare with keras 
Connect the serial device to the RX/TX pins of UART4 of the discovery Board:
```
PA0-WKUP ------> UART4_TX
PA1 ------> UART4_RX
```

adapt /dev/ttyUSB2 to your serial device then run:
```
cd ../host/
python ./main.py -r /dev/ttyUSB2
```

## Generate custom code from new model
The keras model is defined in /host/MnistClassifier.py. 
Feel free to modify the default model, defined in createModel.
Note that:
 - That models with tanh and sigmoid sometimes perform bad (LUT approach of ARM)
 - Softmax can only be the activation function of the last dense layer
 - Only fully connected (dense) layers are supported yet

Generate a model which uses the q7 implementations:
```
python ./main.py -g 7
```
Generate a model which uses the q15 implementations:
```
python ./main.py -g 15
```
