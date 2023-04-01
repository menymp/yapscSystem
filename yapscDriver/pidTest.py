import gc
import utime
from PID import PID
pid = PID(0.0, 0.0, 0.0, setpoint=1, scale='us')

# Assume we have a system we want to control in controlled_system
#v = controlled_system.update(0)

while True:
    gc.collect()
    print(gc.mem_free())
    utime.sleep(1)
    # Compute new output from the PID according to the systems current value
    control = pid(1)
    pid.Kp = 1
    # Feed the PID output to the system and get its current value
    #v = controlled_system.update(control)