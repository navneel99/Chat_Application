import socket
from _thread import *
import threading

def encrypt_decrypt(data,flag=True): #True flag means encryption
    if flag:
        return bytes(data,encoding="ascii")
    else:
        return (data.decode(encoding = "ascii"))

class forwardThread(threading.Thread):
    def __init__(self,receive_socket):
        threading.Thread.__init__(self)
        self.receiveSocket = receive_socket

    def run(self):
        while True:
            fwdm = encrypt_decrypt(self.receiveSocket.recv(1024),False)
            chk = [ line.split() for line in fwdm.split('\n')]
            if len(chk)<=3:
                #Bad Header
                self.receiveSocket.send(encrypt_decrypt("ERROR 103 Header incomplete\n\n"))
            else:
                actual_message = "\n".join([ " ".join(line) for line in chk[3:]])
                print ("Message Received from: " + chk[0][1]+"\n")
                print(actual_message)
                self.receiveSocket.send(encrypt_decrypt("RECEIVED "+ chk[0][1]+"\n\n"))


class sendThread(threading.Thread):
    def __init__(self,send_socket):
        threading.Thread.__init__(self)
        self.sendSocket = send_socket


    def send_message(self,input):
         tmp = input.split()
         recipent = tmp[0]
         message = ' '.join(tmp[1:])
         c_l = len(message)
         actual_message = "SEND "+recipent+"\nContent-length: "+str(c_l)+"\n\n"+message
         self.sendSocket.send(encrypt_decrypt(actual_message))

    def run(self):
        while True:
            print("Data should be of form @[recipent] [message]")
            inp = input("Enter data to be sent to the server. Type q to exit\n")
            if (inp.lower() == 'q'):
                break
            else:
                test = inp.split()
                if (test[0][0] == "@") and len(test)>1:
                    self.send_message(inp)
                    data = encrypt_decrypt(s2.recv(1024),False) #waiting for ack
                    tmp_data =  [line.split() for line in data.split('\n')]
                    if (tmp_data[0][0] == "SENT"):
                        print("Message sent successfully.")
                    else:
                        print(data)
                        print("Some error from the server.")
                else:
                    print("Write the message again.")
                    continue
                # if not data:
                #     continue
                # else:
                #     print(data)






def register_user(u_name, send_socket, receive_socket):
    payload = "REGISTER TOSEND "+u_name+"\n\n"
    payload2 = "REGISTER TORECV "+u_name+"\n\n"
    for curr_payload in [payload,payload2]:
        send_socket.send(encrypt_decrypt(curr_payload))
        ack = receive_socket.recv(1024)
        ack_string = [line.split() for line in (encrypt_decrypt(ack,False)).split('\n')]
        if ack_string[0][0] == "REGISTERED":
            continue
        else:
            print ("Malformed Username")
            return False
    else:
        print ("User Registered.")
        return True

s1 = socket.socket()
s2 = socket.socket()
s_port = 6969  #Send messages on this port
r_port = 6970 #receive messages on this port
s1.connect(('127.0.0.1',s_port)) #It'll send message for the client
s2.connect(('127.0.0.1',r_port)) #It'll receive message for the client
print ("You are successfully connected to the server\n")

username_retry = True
# get_out=True

while username_retry:
    u_name = input("Please Enter your username: ")
    if register_user(u_name, s1, s2):
        username_retry = False
    else:
        continue

thread1 = sendThread(s1)
thread2 = forwardThread(s2)
# while True:
thread1.start()
thread2.start()

# while get_out:
#     inp = input("Enter data to be sent to the server. Type q to exit\n")
#     if (inp.lower() == 'q'):
#         get_out = False
#     else:
#         s1.send(encrypt_decrypt(inp))
#         data = encrypt_decrypt(s2.recv(1024),False)
#         if not data:
#             continue
#         else:
#             print(data)
    #print(s2.recv(1024))
    #print (s1.send(b"Using the send port to send data from the client.\n"))
thread1.join()
# thread2.join()

s1.close()
s2.close()
print ("socket closed")
# thread2.join()
