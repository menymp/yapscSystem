#encoder driver under test menymp jan 2023
# SPDX-FileCopyrightText: 2022 Jamon Terrell <github@jamonterrell.com>
# SPDX-License-Identifier: MIT

import utime
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin

class quadraturePioEncoder():
    def __init__(self, pin_A, pin_B, idMachine = 1):
        self.pin_A = pin_A
        self.pin_B = pin_B
        self.sm1 = StateMachine(idMachine, self.encoder, freq=125_000_000, in_base=Pin(pin_A), jmp_pin=Pin(pin_B))
        self.sm1.active(1)
        self.setEncoderPos(0x7fffffff) #init x to pivot in half 32 unsigned bits to avoid word overflow
        pass
    
    def setEncoderPos(self, value):
        self.sm1.put(value)           
        self.sm1.exec("pull()")       #push init value to OSR register
        self.sm1.exec("mov(x,osr)")   #mov osr value to scratch x register
        pass
    
    def getEncoderPos(self):
        self.sm1.exec("in_(x, 32)")
        return self.sm1.get()
    
    @asm_pio(autopush=True, push_thresh=32)
    def encoder():
        #set(x,21474836)              #init x to pivot in half 32 unsigned bits to avoid word overflow
        wrap_target()
        label("start")
        wait(0, pin, 0)         # Wait for CLK to go low
        jmp(pin, "WAIT_HIGH")   # if Data is low
        mov(x, invert(x))           # Increment X
        jmp(x_dec, "nop1")
        label("nop1")
        mov(x, invert(x))
        label("WAIT_HIGH")      # else
        jmp(x_dec, "nop2")          # Decrement X
        label("nop2")
        
        wait(1, pin, 0)         # Wait for CLK to go high
        jmp(pin, "WAIT_LOW")    # if Data is low
        jmp(x_dec, "nop3")          # Decrement X
        label("nop3")
        
        label("WAIT_LOW")       # else
        mov(x, invert(x))           # Increment X
        jmp(x_dec, "nop4")
        label("nop4")
        mov(x, invert(x))
        wrap()

#encoder functional test

encoder = quadraturePioEncoder(2,3)

while(True):
    utime.sleep(1)
    x = encoder.getEncoderPos()
    print(x)
