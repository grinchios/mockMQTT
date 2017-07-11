import socket, pdb

MAX_CLIENTS = 30
PORT = 22222
QUIT_STRING = '<$quit$>'


def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

class Hall:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}

    def welcome_new(self, new_player):
        new_player.socket.sendall(b'Subscribe command\nexample: UserID=1 Topic=temperature qos=1\n')

    def handle_msg(self, player, msg):
        if 'puback' not in msg:
            print(player.name + " says: " + msg)
            player.suback = 0

            commandlist = msg.split()

            for command in commandlist:
                if command.find('=') == -1:
                    payload = command
                    print(payload)
                    break

            if "userid=" in msg:  #obtained when subscribing
                try:
                    if 'temp' in msg.split('userid=')[1].split()[0] or 'hum' in msg.split('userid=')[1].split()[0] or 'lum' in msg.split('userid=')[1].split()[0]:
                        name = msg.split('userid=')[1].split()[0]
                        player.name = name
                    else:
                        name = msg.split('userid=')[1].split()[0]
                        player.name = 'userID00' + name
                        
                    print("Connection from:", player.name)

                    #msg = msg.split(maxsplit=1)[1]

                    player.suback += 1
                except:
                    print('id error')

            if "topic=" in msg:  #obtained when subscribing
                try:
                    if 'userid=' in msg:
                        room_name = msg.split('topic=')[1].split()[0]
                        if not room_name in self.rooms: # new room:
                            new_room = Room(room_name)
                            self.rooms[room_name] = new_room

                        #if player.name in self.rooms[room_name].players:
                            #self.rooms[room_name].players.remove(player)

                        self.rooms[room_name].players.append(player)
                        self.room_player_map[player.name] = room_name

                        print(player.name + ' joined ' + room_name)

                        #msg = msg.split(maxsplit=1)[1]

                        player.suback += 1

                except:
                    print('topic error')

            if "qos=" in msg:  #obtained when subscribing
                try:
                    if player.suback < 3:
                        player.qos_lvl = int(msg.split('qos=')[1].replace('\n',''))
                        print('QoS set to '+ str(player.qos_lvl)  + ' for ' + str(player.name))
                        player.suback += 1
                except:
                    print('qos error')

            if player.suback == 3 and player.subackSent == False:  #suback sent here
                player.socket.sendall(b'Connected successfully!\n')
                player.subackSent = True  #only sends if subscription was correct

            else:
                # check if in a room or not first
                if player.name in self.room_player_map:
                    if player.subackSent == True:
                        self.rooms[self.room_player_map[player.name]].broadcast(player, payload.encode(), player.qos_lvl)
                    else:
                        self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode(), player.qos_lvl)
                
                    player.socket.sendall(msg.encode())

    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Player: " + player.name + " has left\n")


class Room:
    def __init__(self, name):
        self.players = [] # a list of sockets
        self.playerlist = []
        self.name = name
        self.pubackRecieved = False

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n'
        for player in self.players:
            player.socket.sendall(msg.encode())

    def broadcast(self, from_player, msg, qos):
        self.pubackRecieved = False
        msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            if qos == 0:  #qos of 0 sends once
                player.socket.sendall(msg)
            else:  #qos of 1
                while self.pubackRecieved == False:
                    player.socket.sendall(msg)   #sends here
                    try:
                        msg = player.socket.recv(4096)  #waits for puback
                    except:
                        break
                    if 'puback' in msg.decode().lower():
                        self.pubackRecieved = True  #when puback is recieved it stops sending

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode() + b"has left the room\n"
        self.broadcast(player, leave_msg, 0)

class Player:
    def __init__(self, socket, name = "new",  qos = 0,  suback = 0):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.qos_lvl = qos
        self.suback = suback
        self.subackSent = False

    def fileno(self):
        return self.socket.fileno()
