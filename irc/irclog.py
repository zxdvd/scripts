
import logging
import socket
import ssl
import threading
from datetime import datetime
from time import sleep

import click

logging.basicConfig(level=logging.INFO)

def sendstr(s, string):
    logging.debug('Sent '+string)
    s.send(bytes(string, 'utf-8'))

def recv_msg(s, fd):
    while True:
        data = s.recv(4096)
        logging.debug(b'Rv '+data)
        if data.find(b'PING') == 0:
            logging.info('Get PING from server!!')
            pong = data.decode().split()[1]
            sendstr(s, 'PONG '+pong+'\r\n')
            continue
        if data:
            t = datetime.now().strftime('%Y%m%d-%H-%M-%S')
            fd.write(t + ': ' + data.decode())
            fd.flush()

@click.command()
@click.option('--server', default='irc.suse.de', help='IRC server')
@click.option('--port', default=6697, help='IRC port')
@click.option('--nick', default='zxdBot', help='Nickname')
@click.option('--channel', default='zxdtest', help='The channel to log')
def main(server, port, nick, channel):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = ssl.wrap_socket(s)
    s.connect((server, port))
    f = open('channel-'+channel+'.log', 'a', encoding='utf-8')

    t_recv = threading.Thread(target=recv_msg, args=(s,f))
    t_recv.start()

    sendstr(s, 'NICK '+nick+'\r\n')
    sendstr(s, 'USER '+nick+' 0 * :'+nick+'\r\n')
    sleep(4)
    sendstr(s, 'JOIN #'+channel+'\r\n')

if __name__ == '__main__':
    main()
