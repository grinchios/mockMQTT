import select, socket, sys
from util import Room, Hall, Player
import util
import time

READ_BUFFER = 4096

if len(sys.argv) < 2:
    print("Usage: Python3 client.py [hostname]", file = sys.stderr)
    sys.exit(1)
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], util.PORT))

def prompt():
    print('>', end=' ', flush = True)

print("Connected to server\n") #CONNACK
msg_prefix = ''

socket_list = [sys.stdin, server_connection]

nodeID = ''

while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_connection: # incoming message
            time.sleep(0.1)
            msg = s.recv(READ_BUFFER)
            if not msg:
                print("Server down!")
                sys.exit(2)
            else:
                if msg == util.QUIT_STRING.encode():
                    sys.stdout.write('DICONNECTED\n')
                    sys.exit(2)
                else:
                    server_connection.sendall(b'puback')
                    sys.stdout.write('\r\r' + msg.decode())
                    print()
                    if 'example:' in msg.decode():
                        subscribeCheck = False
                    prompt()

        else:
            if subscribeCheck == False:
                while subscribeCheck == False:
                    msg = msg_prefix + sys.stdin.readline()
                    if subscribeCheck == False and 'userid='  in msg.lower() and 'topic=' in msg.lower() and 'qos=' in msg.lower():
                        subscribeCheck = True
                    else:
                        print('\nSubscribe command not in correct format\nexample: UserID=1 Topic=temperature qos=1')
                        #subscription format check ^
                        prompt()
            
            else:
                msg = msg_prefix + sys.stdin.readline()
            server_connection.sendall(msg.encode())










