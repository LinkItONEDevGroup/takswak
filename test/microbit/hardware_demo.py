# ATAK hardware demo
from microbit import *

def mymap(x, in_min, in_max, out_min, out_max):
    r = int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
    if r<out_min:
        return out_min
    if r>=out_max:
        return out_max-1
    return r

def isnumeric(x):
    try:
        f = float(x)
        return True
    except:
        return False

uart.init(baudrate=115200) #

while True:
    ok=0
    cmd = input('>')
    cols = cmd.split()
    if len(cols)>=1:
        if cols[0]=="fire":
            if len(cols)>=3:
                x = cols[1]
                y = cols[2]
                if isnumeric(x) and isnumeric(y):
                    fx = float(x)
                    fy = float(y)
                    ok=1
        if cols[0]=='clear':
            display.clear()
            print("OK:"+cmd)
            continue
    if ok:
        ox = mymap(fx,120.027,122.003,0,5)
        oy = 4- mymap(fy,21.916,25.292,0,5) # reverse
        #print(ox,oy)
        display.clear()
        display.set_pixel(ox,oy,9)
        print("OK:"+cmd)
    else:
        print("KO:"+cmd)
                
