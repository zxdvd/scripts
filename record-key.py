
import os
import logging
from select import select
import subprocess
import threading
from time import sleep

# requirement click, evdev
import click
from evdev import InputDevice, UInput, list_devices, ecodes as e

KEY_MAP = {}
KEY_MAP['dot'] = '.'

logging.basicConfig(level=logging.DEBUG)

def getdevice():
    '''get the first keyborad device and return it'''

    devs = [InputDevice(fn) for fn in list_devices()]
    for dev in devs:
        #device's capabilities is a dict, and the key 1's items are keys
        #while key 17's items are leds, key 4's items are mice
        #some mouse also have keys so len(caps[1]) to assure it is keyboard
        caps = dev.capabilities()
        if 1 in caps:
            if len(caps[1]) > 26:
                return dev

def keylog(dev, fd):
    '''log all the keystrokes of the [dev] to a file descriptor'''

    while True:
        if app_exited:
            logging.debug('thread keylog exited')
            break
        #wait for device to ready, otherwise may get BlockingIOError
        #use the 2 secs timeout to avoid it blocking at here forever
        r, w, x = select([dev], [], [], 1)
        if not r:
            continue
        for event in dev.read():
            if event.type == e.EV_KEY:
                line = ','.join([str(event.sec), e.KEY[event.code],
                    str(event.value)])
                fd.write(line + '\n')
                logging.debug(line)

def parselog(fd):
    '''read the key log file and output the keys/strings'''

    logging.debug('in the parselog function')
    tmp = []
    output = []
    for line in fd:
        t, k, act = line.split(',')     #time, key, action
        k = k[4:].lower().replace('left', '').replace('right', '')
        k = KEY_MAP[k] if k in KEY_MAP else k
        if act[0] == '1':
            tmp.append(k)
        if act[0] == '0' and len(tmp) and k == tmp[0]:
            if len(tmp) == 1:           #it's a single key
                last = output[-1][0]
                if '-' in last or len(k) > 1:
                    output.append((k, t))
                else:
                    output[-1] = (last + k, t)
            if len(tmp) > 1:            #it's a combined key
                output.append(('-'.join(tmp), t))
            tmp = []

    logging.debug(output)

@click.command()
@click.option('-c', '--cmd', prompt='Please input the command and args',
        help='the cmd of application you want to open')
def launch(cmd):
    dev = getdevice()
    if not dev:
        logging.error('can not get a keyboard device, please run with root')
    else:
        logging.info('get a keyboard: {0} {1}'.format(dev.fn, dev.name))
    cmd = cmd.split(' ')
    app = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
    global app_exited
    app_exited = 0
    with open('/tmp/key.log', 'w') as f:
        task_keylog = threading.Thread(name='logger', target=keylog,
                args=(dev, f))
        task_keylog.start()
        while app.poll() == None:
            sleep(2)
            logging.debug('in the main loop')
        app_exited = 1
        task_keylog.join(2)
        sleep(2)

    with open('/tmp/key.log', 'r') as f:
        logging.debug('open the key.log file')
        parselog(f)

if __name__ == '__main__':
    launch()
