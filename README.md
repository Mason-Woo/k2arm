# k2arm - keras to arm parser
A simple project to show how a custom keras model can be automatically translated into c-code.
The generated c-code can, in combination with the [ARM-CMSIS-NN](http://www.keil.com/pack/doc/CMSIS_Dev/NN/html/index.html) functions, be used
to run neural-net calculations in an efficient way on an embedded micro-controller such as the CORTEX-M4.

This repository has also example firmware which runs on the [STM32F4-Discorevy Board](https://www.st.com/en/evaluation-tools/stm32f4discovery.html). Part of the firmware was generated with [cubeMX](https://www.st.com/en/development-tools/stm32cubemx.html). The example project has a MNIST classifier which can classify handwritten digits.

Following steps are tested on Ubuntu 18.04

## CMSIS-NN code generation
Following software is required:
 - python: 3.6
 - tensorflow 1.10.0

The keras model is defined in /host/MnistClassifier.py. 
Feel free to modify the default model, defined in createModel.
Note that:
 - That models with tanh and sigmoid sometimes perform bad (LUT approach of CMSIS-NN, see: [Issue](https://github.com/ARM-software/CMSIS_5/issues/470))
 - Softmax can only be the activation function of the last dense layer
 - Only fully connected (dense) layers are supported yet

Clone repository with submodules:
```
git clone --recurse-submodules https://github.com/InES-HPMM/k2arm.git
cd k2arm/host
```
Generate C-code which uses the q7 implementations:
```
python3.6 ./main.py -g 7
```
Generate C-code which uses the q15 implementations:
```
python3.6 ./main.py -g 15
```

## Firmware deployment and model evaluation
Following software and hardware is required:
 - [libusb-1.0.0-dev](https://packages.ubuntu.com/search?keywords=libusb-1.0-0-dev) (for st-link)
 - [arm-none-eabi-gcc](https://packages.ubuntu.com/de/trusty/gcc-arm-none-eabi)
 - [STM32F4-Discorevy Board](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)
 - [Serial connection device such as the TLL-232R Converter](https://ch.farnell.com/ftdi/ttl-232r-3v3/kabel-usb-ttl-pegel-seriell-umsetzung/dp/1329311?mckv=s89FAqCVd_dc|pcrid|251391972450|kword|ttl-232r-3v3|match|p|plid|&CMP=KNC-GCH-GEN-SKU-MDC-German&gclid=EAIaIQobChMIjfS4hcyo2wIVxDobCh14jwVBEAAYAiAAEgLMo_D_BwE)

### Setup
Build st-flash according to [guide](https://github.com/texane/stlink/blob/master/doc/compiling.md):

```
cd ../target/stlink
make
sudo cp etc/udev/rules.d/49-stlinkv* /etc/udev/rules.d/
sudo udevadm control --reload-rules

```

### Build and deploy
Build firmware with default neural net:
```
cd ..
make
```
In case of the error:
```
Conflicting CPU architectures 13/1
```
install: [this packages](https://github.com/bbcmicrobit/micropython/issues/514#issuecomment-404759614).

Connect the discovery board to through the usb connector, flash firmware with default net:
```
./stlink/build/Release/st-flash --format ihex write ./build/cubeMx.hex
```

### Evaluate the translated neural net
Connect the serial connection device RX/TX to the RX/TX pins of UART4 of the discovery Board:
```
PA0-WKUP Board ------> TX Serial device host
PA1      Board ------> RX Serial device host
GND      Board ------> GND host
```

adapt /dev/ttyUSB2 to your serial device then run:
```
cd ../host/
python3.6 ./main.py -r /dev/ttyUSB2
```

