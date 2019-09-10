import socket
# import re

def encrypt_decrypt(data,flag=True): #True flag means encryption
    if flag:
        return bytes(data,encoding="ascii")
    else:
        return (data.decode(encoding = "ascii"))

def register_user(u_name, send_socket, receive_socket):
    payload = "REGISTER TOSEND "+u_name+"\n\n"
    payload2 = "REGISTER TORECV "+u_name+"\n\n"
    for curr_payload in [payload,payload2]:
        send_socket.send(encrypt_decrypt(curr_payload))
        ack = receive_socket.recv(1024)
        # print (ack)
        # print(encrypt_decrypt(ack,False))
        ack_string = [line.split() for line in (encrypt_decrypt(ack,False)).split('\n')]
        # print (ack_string)
        if ack_string[0][0] == "REGISTERED":
            continue
        else:
            # break
            print ("Malformed Username")
            return False
    else:
        print ("User Registered.")
        return True

s1 = socket.socket()
s2 = socket.socket()
r_port = 6969  #receiving port of the server
s_port = 6970 #sending port of the server
s1.connect(('127.0.0.1',r_port)) #It'll send data for the client
s2.connect(('127.0.0.1',s_port)) #It'll receive data for the client
print ("You are successfully connected to the server\n")

username_retry = True
get_out=True

while username_retry:
    u_name = input("Please Enter your username: ")
    if register_user(u_name, s1, s2):
        username_retry = False
    else:
        continue

while get_out:
    inp = input("Enter data to be sent to the server. Type q to exit\n")
    if (inp.lower() == 'q'):
        get_out = False
    else:
        s1.send(encrypt_decrypt(inp))
        data = encrypt_decrypt(s2.recv(1024),False)
        if not data:
            continue
        else:
            print(data)
    #print(s2.recv(1024))
    #print (s1.send(b"Using the send port to send data from the client.\n"))
s1.close()
s2.close()
