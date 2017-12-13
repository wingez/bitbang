import RPi.GPIO as GPIO
import time
import json
from io import StringIO

GPIO.setmode(GPIO.BCM)

sleepdelayus = 100
pindelay = lambda:time.sleep(sleepdelayus / 1000000.0)

Input = 0
Output = 1

MSBFirst=2
LSBFirst=3

def disablewarnings():
    GPIO.set_warnings(False)



class GPIOError(Exception):
    def __init__(self,message):
        self.message=message
    





class Pin(object):
    def __init__(self,pinindex,direction=Output,inverted=False):
        self.index = pinindex
        self.direction = mode
        self.inverted = inverted
        
        if direction == Output:
            GPIO.setup(self.index,GPIO.OUT)
            self.low()
        elif direction == Input:
            GPIO.setup(self.index,GPIO.IN)
        else:
            raise ValueError('mode must be either Input or Output') 

    def high(self):
        if self.direction is not Output:
            raise GPIOError('Pin is not an output')
        GPIO.output(self.index,not self.inverted)
    def low(self):
        if self.direction is not Output:
            raise GPIOError('Pin is not an output')
        GPIO.output(self.index,self.inverted)

    def pulse(self):
        self.low()
        self.high()
        self.low()

    def read(self):
        if self.direction is not Input:
            raise GPIOError('Pin is not an input')
        val = GPIO.input(self.index)
        if self.inverted:
            val = not val
        return val

def getiterator(bits,mode):
    
    if mode is MSBFirst:
        return range(bits - 1,-1,-1)
    elif mode is LSBFirst:
        return range(bits)
    else:
        raise ValueError('mode')

def shiftout(data,bits,mode,clockpin=None,datapin=None,latchpin=None,pins={}):

    if not clockpin:
        clockpin=pins['clock']
    if not datapin:
        datapin=pins['data']
    if not latchpin:
        latchpin=pins['latch']


    for pin in (clockpin,datapin,latchpin):
        pin.low()
    
    for i in getiterator(bits,mode):
        if ((1 << i) & data) != 0:
            datapin.high()
        else:
            datapin.low()
        clockpin.pulse()

    latchpin.pulse()


def shiftin(bits,mode,clockpin=None,datapin=None,latchpin=None,pins={}):
    
    if not clockpin:
        clockpin=pins['clock']
    if not datapin:
        datapin=pins['data']
    if not latchpin:
        latchpin=pins['latch']

    for pin in (latchpin,clockpin):
        pin.low()

    latchpin.pulse()
    result=0

    for i in getiterator(bits,mode):
        if datapin.read():
            result|=(1<<i)

        clockpin.pulse()

    return result



def readpinjson(json):

    if 'pin' not in json:
        raise ValueError("'pin' missing from pin object")
    pin = json['pin']

    direction=Output
    if 'direction' in json:
        direction = json['direction']
        if direction=='output':
            direction=Output
        elif direction=='input':
            direction=Input
        else:
            raise ValueError('direction: {} is not defined'.format(direction))

    inverted=False
    if 'inverted' in json:
        inverted = json['inverted']
    
    return Pin(pin,direction,inverted)


def readpins(jsonfile,group=''):

    result = {}

    with open(jsonfile) as f:
        j = json.loads(f.read())

        if not group:
            for k,v in j.items():
                result[k]=readpinjson(v)
        else:
            for k,v in j[group].items():
                result[k]=readpinjson(v)
    return result
    












