
# yapsc System controller 
## About
This project started as a development for an older tool that allows control for old analog servomotor drivers with +-10v control interface with the existing step/dir protocol

The base targeted microcontroller selected for the task is the [RP2040](https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html) by raspberry pi, the selection was made due to facilities availables by the plataform such as dual core that allow having a deterministic timing control loop and a less deterministic interface for handling serial instructions, the plataform also contains several IO peripetals such as pwm for the analog output emulation and the PIO modules, the later being a usefull resource for handling simple operation that requieres high sampling rate, this requeriment is imposed by feedback incremental encoder present on drivers and the step\dir standard interface for comunication with cnc control boards.
An older approach attempt was made with an stm32 microcontroller [here](https://github.com/menymp/STM32_AnalogBrushlessServomotorController_10v_StepDir) with a single thread M4 core, but the project was stopped due to hardware limitations and requeriments. An FPGA approach was also considered but the conclussion was that the implementation imposes a complex approach that does not justify the problem.

a ui is also provided
## Disclaimer
This project and sources are under development and in  no way are intended to be part of a functional system, use at your own risk.
A licence is provided under LICENSE.md 

## How to run
The code under yapscDriver directory contains the main logic for the raspberry pi pico microcontroller and is expected to be loaded to a [RP2040 microcontroller](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#:~:text=MicroPython%20is%20a%20full%20implementation%20of%20the%20Python,MicroPython%20includes%20modules%20for%20accessing%20low-level%20chip-specific%20hardware.) prior to use of tunning UI. 

To run the UI execute the file in the yapsTkGUI directory.

> python main.py

## Base projects and credits
the following is the list of external projects whose developments support this project
- [mycropython EEPROM](https://github.com/peterhinch/micropython_eeprom) - Driver for I2C EEPROM by peterhinch.
- [micropython simple PID](https://github.com/gastmaier/micropython-simple-pid) - PID simple controller migrated to micropython by gastmaier.
- [qe pi pico](https://github.com/jamon/pi-pico-pio-quadrature-encoder) - encoder asembler example for PIO modules by jamon.
- [serial util](https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python) - a simple yet usefull script to find available serial ports in OS devices for Windows and Linux by tfeldmann.


## ToDo list
currently this tool is still unstable and under major test, the following are the improvement points to be addressed in the current project.
- Documentation of the testing and overview for critical modules, this includes comments, electrical diagrams, High level block diagram etc.
- Testing with real environment.

## Future ideas and features
- auto tunning tools
- decouple of controller logic to accept different control algoritms such as sliding modes or robust controll.
- PCB for the tool.