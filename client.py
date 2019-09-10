import socket
# import re

def register_user(u_name):
#    if (check_username(u_name)):
    payload = "REGISTER TOSEND ", u_name,"\n\n"
    payload2 = "REGISTER TORECV ",u_name,"\n\n"


s1 = socket.socket()
s2 = socket.socket()
r_port = 6969  #receiving port of the server
s_port = 6970 #sending port of the server
s1.connect(('127.0.0.1',r_port)) #It'll send data for the client
s2.connect(('127.0.0.1',s_port)) #It'll receive data for the client
print ("You are successfully connected to the server\n")
get_out = False
u_name = input("Please Enter your username: ")
get_out=True

while get_out:
    inp = input("Enter data to be sent to the server. Type q to exit\n")
    if (inp.lower() == 'q'):
        get_out = False
    else:
        s1.send(bytes(inp, encoding="ascii"))
        data = s2.recv(1024)
        if not data:
            continue
        else:
            print(data)
    #print(s2.recv(1024))
    #print (s1.send(b"Using the send port to send data from the client.\n"))
s1.close()
s2.close()
