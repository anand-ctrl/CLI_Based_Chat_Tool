from base64 import decode
from multiprocessing.connection import Client
import socket
import threading
import pdb

host='localhost'
port =1234

server=socket.socket()
server.bind((host, port))

server.listen()

clients=[]
names=[]
rooms={} # {room_name:room_no}
client_rooms={} # {room_no. :[all_clients_in_that_room]}
room_wrt_client={} # {client: room_no}
 
# initialization
rooms['general']=0
client_rooms[0]=[]
total_rooms=0


# send message to all the clients that are currently connected

def broadcast(message, client):
    room_of_client=room_wrt_client[client]
    for c in client_rooms[room_of_client]:
        if c!=client:
            c.send(message)


# receive message from the client

def handle(client):
    while True:
        try:
            msg=message=client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if names[clients.index(client)]=='admin':
                    name_to_kick=msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send("Command was refused!".encode('ascii'))

            elif msg.decode('ascii').startswith('BAN'):
                if names[clients.index(client)]=='admin':
                    name_to_ban=msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f"{name_to_ban}\n")
                    print(f"{name_to_ban} was banned!")
                else:
                    client.send("Command was refused!".encode('ascii'))

            elif msg.decode('ascii')=='QUIT':
                index=clients.index(client)
                clients.remove(client)
                name=names[index]
                broadcast(f"{name} left the chat!".encode('ascii'), client)
                print(f"{name} has left the server!")
                client.close()
                names.remove(name)
                break

            elif msg.decode('ascii')=='LIST':
                if len(rooms)==0:
                    m = 'Oops, no active rooms currently. Create your own!\n' \
                        + 'Use [/join room_name] to create a room.\n'
                    client.send(m.encode('ascii'))
                else:
                    count=0
                    m = 'Listing current rooms...\n'
                    for i in rooms:
                        m+=str(count)+': '+i+'\n'
                        count+=1
                    client.send(m.encode('ascii'))
            
            elif msg.decode('ascii').startswith('JOIN'):
                room_name=msg.decode('ascii')[5:]
                if room_name in rooms: # if room name exists
                    room_no=rooms[room_name]
                    # check whether client is already a member of this room
                    if room_wrt_client[client]==room_no:
                        client.send("You are already a part of this room!".encode('ascii'))
                    else:
                        # 1. delete the presence of client from its previous room
                        # 2. go to clients_room which has room_no:[clients] data & pop the presence of client
                        # 3. now update client room no in room_wrt_client
                        # 4. append client in the room_no in client_rooms
                        
                        prev_room_no=room_wrt_client[client]
                        client_rooms[prev_room_no].remove(client)
                        room_wrt_client[client]=room_no
                        client_rooms[room_no].append(client)
                        client.send(f"You joined the room {room_name}!".encode('ascii'))
                        ind=clients.index(client)
                        name=names[ind]
                        print(f"{name} joined the room {room_name}!")
                        broadcast(f"{name} joined the room!".encode('ascii'), client)
                else:
                    global total_rooms
                    # 1. increase total_rooms and add this room in rooms
                    # 2. add this client into the room
                    # 3. lastly add this room no into client_rooms and append this client into it.
                    total_rooms+=1
                    prev_room_no=room_wrt_client[client]
                    client_rooms[prev_room_no].remove(client)
                    rooms[room_name]=total_rooms
                    room_wrt_client[client]=total_rooms
                    arr=[]
                    arr.append(client)
                    client_rooms[total_rooms]=arr
                    client.send(f"{room_name} room is created for you!".encode('ascii'))
                    ind=clients.index(client)
                    name=names[ind]
                    print(f"{room_name} room is created by {name}!")
            else:
                broadcast(message, client)

        except:
            if client in clients:
                index=clients.index(client)
                clients.remove(client)
                name=names[index]
                broadcast(f"{name} left the chat!".encode('ascii'), client)
                print(f"{name} has left the server!")
                client.close()
                names.remove(name)
                break



# writing the main func combining all functonalities

def receive():
    while True:
        client, address=server.accept()
        print(f"Connected with {str(address)}")

        client.send('NAME'.encode('ascii'))
        name=client.recv(1024).decode('ascii')
        with open('bans.txt', 'r') as f:
            bans=f.readline()
        

        if name in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue
            
        if not name:
            index=clients.index(client)
            clients.remove(client)
            name=names[index]
            broadcast(f"{name} left the chat!".encode('ascii'), client)
            print(f"{name} has left the server!")
            client.close()
            names.remove(name)
        
        if name=='admin':
            client.send('PASS'.encode('ascii'))
            password=client.recv(1024).decode('ascii')

            # if the password is wrong just disconnect else continue
            if password!='12345':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        client_rooms[0].append(client)
        room_wrt_client[client]=0
        names.append(name)
        clients.append(client)
        print(f"Name of client is {name}!")
        broadcast(f"{name} joined the chat".encode('ascii'), client)
        client.send('Connected to the server!'.encode('ascii'))

        thread=threading.Thread(target=handle, args=(client, ))
        thread.start()


def kick_user(name):
    if name in names:
        # remove 
        name_index=names.index(name)
        client_to_kick=clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by admin!'.encode('ascii'))
        client_to_kick.close()
        names.remove(name)
        broadcast(f"{name} was kicked by admin!".encode('ascii'), client_to_kick)

print(f"Server is listening at {host}:{port}...")
receive()



