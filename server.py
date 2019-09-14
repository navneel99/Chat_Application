from _thread import *
import threading
import socket
import re
from socketserver import ThreadingMixIn

def reg_match(regex, string):
    if re.search(regex, string):
        return True
    else:
        return False

def encrypt_decrypt(data,flag=True): #True flag means encryption
    if flag:
        return bytes(data,encoding="ascii")
    else:
        return (data.decode(encoding = "ascii"))

# client_lock = threading.Lock()
# The function sends data to the client and then receives data from the client to return to its main function
users = [] #List of usernames registered
user_dic = {} #Key are usernames and bvalues are tuple of send and receive socket.
class ClientPerThread(threading.Thread):
    def __init__(self,r_sock,s_sock):
        threading.Thread.__init__(self)
        self.receiveSocket = r_sock
        self.sendSocket = s_sock
        self.currClient = None

    def forward_message(self,recipent,c_length,message):
        r_sock,s_sock = user_dic[recipent]
        actual_message = "FORWARD "+ self.currClient + "\nContent-length: "+str(c_length)+"\n\n"+message
        s_sock.send(encrypt_decrypt(actual_message))
        ack = encrypt_decrypt(s_sock.recv(1024),False)
        print ("Ack after receving the message is: "+ ack)
        return ack

    def client_operations(self):
        while True:
            data = encrypt_decrypt(self.receiveSocket.recv(1024),False)
            split_data = [ line.split() for line in (data.split("\n"))]
            print (split_data)
            if split_data[0][0] == "REGISTER":
                username = split_data[0][2]
                if reg_match("[a-zA-Z0-9]+", username):
                    users.append(username)
                    user_dic[username] = (self.receiveSocket,self.sendSocket)
                    self.currClient = username
                    self.sendSocket.send(encrypt_decrypt("REGISTERED "+ split_data[0][1]+" "+username+"\n\n"))
                else:
                    self.sendSocket.send(encrypt_decrypt("ERROR 100 Malformed username\n\n"))
            elif (split_data[0][0] == "SEND"):
                recipent = split_data[0][1].lstrip("@")
                c_length = split_data[1][1]
                message = "\n".join([" ".join(line) for line in split_data[3:]])
                if recipent not in users:
                    #If send user doesn't exist
                    self.receiveSocket.send(encrypt_decrypt("ERROR 102 Unable to send\n\n"))
                elif(len(split_data)<4): #This condiiton is for header incomplete
                    self.receiveSocket.send(encrypt_decrypt("ERROR 103 Header incomplete\n\n"))
                else:
                    #Send the message
                    ack = self.forward_message(recipent,c_length,message)
                    tmp_ack =  [line.split() for line in ack.split("\n")]
                    if tmp_ack[0][0] == "RECEIVED":
                        self.receiveSocket.send(encrypt_decrypt("SENT "+recipent+"\n\n"))
                    else:
                        self.receiveSocket.send(encrypt_decrypt("ERROR 102 Unable to send\n\n"))

            else:
                print("Normal data from "+username+": "+ str(data))
                self.sendSocket.send(encrypt_decrypt("Dummy to allow next loop.\n"))
                # pass


    def run(self):
       while True:
            print ("Server waiting for data from client: ")
            self.client_operations()
       print ("Exited form the thread.\n")
       # return inp_data



def main_server_body():
    ip = "127.0.0.1"
    r_port = 6969 #receives messages on this port
    s_port = 6970 #forwards messages on this port

    registered_users = []

    receive_socket = socket.socket()
    print("Receive socket created.")
    send_socket = socket.socket()
    print("Send socket created.")

    receive_socket.bind(('',r_port))
    send_socket.bind(('',s_port))

    threads = []

    while True:
        send_socket.listen(2)
        receive_socket.listen(2)
        r_conn, r_address = receive_socket.accept()
        s_conn, s_address = send_socket.accept()
        # client_lock.acquire()
        newthread = ClientPerThread(r_conn, s_conn)
        newthread.start()
        threads.append(newthread)
        print ("Accepted  receive connection from: "+ str(r_address))
        print ("Acceoted send connection from: " + str(s_address))

        # data = b"DUMMY"
        # start_new_thread(thread_client, (conn,conn2,data))

main_server_body()
