import socket
import threading
import pdb 
host='localhost'
port=1234

client=socket.socket()
client.connect((host, port))
instructions = 'Instructions:\n'\
            + '[/list] to list all rooms\n'\
            + '[/join room_name] to join/create/switch to a room\n' \
            + '[/quit] to quit\n' \
            + 'Otherwise start typing and enjoy!' \
            + '\n'
print(instructions)
name=input("Enter your name: ")
if name=='admin':
    password=input("Enter admin password: ")

# receive message from server

stop_thread=False

def receive():
    while True:
        global stop_thread
        if stop_thread==True:
            break
        try:
            message=client.recv(1024).decode('ascii')
            if message=='NAME':
                client.send(name.encode('ascii'))
                next_message=client.recv(1024).decode('ascii')
                if next_message=='PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii')=='REFUSE':
                        print('Wrong password, connection refused!')
                        stop_thread=True
                elif next_message=='BAN':
                    print("Connection refused because of ban!")
                    client.close()
                    stop_thread=True
            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break


def write():
    while True:
        global stop_thread
        if stop_thread:
            break
        message=f'{name}: {input("")}'
        # adding kicking feature
        if message[len(name)+2:].startswith('/'):
            if message[len(name)+2:].startswith('/quit'):
                client.send(f'QUIT'.encode('ascii'))
                stop_thread=True
            elif message[len(name)+2:].startswith('/join'):
                client.send(f"JOIN {message[len(name)+2+6:]}".encode('ascii'))

            elif message[len(name)+2:].startswith('/list'):
                client.send(f'LIST'.encode('ascii'))
                
            elif name=='admin':
                if message[len(name)+2:].startswith('/kick'):
                    client.send(f"KICK {message[len(name)+2+6:]}".encode('ascii'))
                elif message[len(name)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(name)+2+5:]}'.encode('ascii'))

            else:
                print('The command can only be executed by Admin!')
                
        else:
            client.send(message.encode('ascii'))


receive_thread=threading.Thread(target=receive)
receive_thread.start()

write_thread=threading.Thread(target=write)
write_thread.start()

