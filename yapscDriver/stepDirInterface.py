from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

class stepDirInterface():
    def __init__(self, stepPin, dirPin,  machineId = 0):
        self.stepPin = stepPin
        self.dirPin = dirPin
        self.sm1 = StateMachine(machineId, self.stepDirQueue, freq=125_000_000, in_base=Pin(stepPin), jmp_pin=Pin(dirPin))
        self.sm1.active(1)
        self.setEncoderPos(0x7fffffff) #init x to pivot in half 32 unsigned bits to avoid word overflow
        pass
    
    def setEncoderPos(self, value):
        self.sm1.put(value)           
        self.sm1.exec("pull()")       #push init value to OSR register
        self.sm1.exec("mov(x,osr)")   #mov osr value to scratch x register
        pass
    
    def inBufferCount(self):
        return sm1.rx_fifo()
    
    def getEncoderPos(self):
        self.sm1.exec("in_(x, 32)")
        return self.sm1.get()
    
    @asm_pio(autopush=True, push_thresh=32)
    def stepDirQueue():
        #set(x,0x7fffffff)              #init x to pivot in half 32 unsigned bits to avoid word overflow
        label("wait_risingEdge")
        wait(0, pin, 0)                # Wait for CLK to go low
        wait(1, pin, 0)                # Wait for CLK to go high
        jmp(pin, "inverse_direction")  # jmp when pin 1
        mov(x, invert(x))              #for increment there is no direct instruction, so we do a simple trick, invert x first
        jmp(x_dec, "next")             #then decrement x by 1
        label("next")                  #wait to machine to perform the step
        mov(x, invert(x))              #invert again the value
        jmp("wait_risingEdge")         #jmp to wait for the next rising edge
        label("inverse_direction")
        jmp(x_dec, "next2")            #then decrement x by 1
        label("next2")
        jmp("wait_risingEdge")

#functional tests for step dir module, test pins under 27 and 26 gpio pins
'''
'''
'''
step = machine.Pin(27, machine.Pin.OUT)
dir = machine.Pin(26, machine.Pin.OUT) 
stepDirObj = stepDirInterface(16,17)
y = 0;

def funcTestStepDir():
    y = stepDirObj.getEncoderPos()
    print('initial = ' + str(y))
    step.off()
    dir.on()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    y = stepDirObj.getEncoderPos()
    print('next = ' + str(y))
    step.off()
    dir.off()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    utime.sleep(0.1)
    step.on()
    utime.sleep(0.1)
    step.off()
    y = stepDirObj.getEncoderPos()
    print('end = ' + str(y))
    utime.sleep(3)
'''