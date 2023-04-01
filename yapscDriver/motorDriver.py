from machine import Pin, PWM, ADC
import utime

class motorDriver():
    def __init__(self, pin_A, pin_B, frequency):
        self.pin_A = pin_A
        self.pin_B = pin_B
        self.frequency = frequency
        self.r_pwm = PWM(Pin(pin_A, mode=Pin.OUT))
        self.r_pwm.freq(frequency)
        self.l_pwm = PWM(Pin(pin_B, mode=Pin.OUT))
        self.l_pwm.freq(frequency)
        self.r_pwm.duty_u16(0)
        self.l_pwm.duty_u16(0)
        self.direction = False
        self.value = 0
        pass
    
    def setOutput(self, direction, value):
        self.direction = direction
        self.value = value
        if direction:
            self.r_pwm.duty_u16(value)
            self.l_pwm.duty_u16(0)
        else:
            self.l_pwm.duty_u16(value)
            self.r_pwm.duty_u16(0)
        pass
    
    def getOutput(self):
        return [self.direction, self.value]

#functional test
'''
motorOutObj = motorDriver(pin_A = 16,pin_B = 17,frequency = 80_000)

def pwmOutTest():
    print("flank a test")
    for duty in range(0, 65535):
        motorOutObj.setOutput(0,duty)
        utime.sleep(0.0001)
    print("flank b test")
    for duty in range(0, 65535):
        motorOutObj.setOutput(1,duty)
        utime.sleep(0.0001)
'''