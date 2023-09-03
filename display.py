import subprocess
import i2cLCD  # LCD Driver is derived from https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import signal
from time import sleep


def checki2cDevices():
    '''Returns addressess of available devices'''
    removeList = [str(i*10).zfill(2) + ':' for i in range(8)]
    removeList.append('--')

    out = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True).stdout.decode().split('\n', 1)[1]

    for each in removeList:
        out = out.replace(each, '')
    return out.strip()


def getThrottled():
    '''returns throttle data hex'''
    return subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True).stdout.decode().strip().split('=')[1]


def isThrottled():
    '''Returns True if presently throttled'''
    result = getThrottled()
    bin_result = (bin(int(result, 16)))[-4:]
    if bin_result == '0000' or '0':
        return False
    return True


def getTemp():
    '''Returns temp reading of SoC as a string with ''C' at the end'''
    return subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True).stdout.decode().split('=')[1].strip()


def freeRAM():
    '''returns free RAM in MB'''
    return subprocess.run(['free', '--mega'], capture_output=True).stdout.decode().strip().split()[12]


def printSTat():
    if isThrottled():
        print(f'CPU is throttled ({getThrottled()})', end='. ')
    else:
        print("CPU isn't throttled", end='. ')
    print(f'Free RAM = {freeRAM()} MB', end='. ')
    print(f'CPU Temp = {getTemp()}', end='\r')


def terminationHandler(*_):
    disp.lcd_clear()
    disp.backlight(False)
    quit()


if __name__ == "__main__":
    if checki2cDevices():
        disp = i2cLCD.lcd()

        for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, terminationHandler)

        while True:
            disp.lcd_display_string(f'CPU Temp-{getTemp()}', 1)
            disp.lcd_display_string(f'Free RAM-{freeRAM()}MB', 2)
            sleep(1)
    else:
        print('No I²C Device detected! Quitting script...')
        quit()
