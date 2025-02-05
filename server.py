from _thread import *
import threading
import socket
import re
from socketserver import ThreadingMixIn
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
import base64
import pickle
import sys

MODE = int(sys.argv[1])

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

def decrypt_message(key, message):
    rsa_key = RSA.importKey(key)
    rsa_key = PKCS1_OAEP.new(rsa_key)
    message = base64.b64decode(message)
    message = rsa_key.decrypt(message)
    return message

# The function sends data to the client and then receives data from the client to return to its main function
users = [] #List of usernames registered
user_dic = {} #Key are usernames and bvalues are tuple of send and receive socket and public_key
class ClientPerThread(threading.Thread):
    def __init__(self,r_sock,s_sock):
        threading.Thread.__init__(self)
        self.receiveSocket = r_sock
        self.sendSocket = s_sock
        self.currClient = None

    def forward_message(self,recipent,c_length,message,signature=None):
        r_sock,s_sock,pub_key = user_dic[recipent]
        if MODE != 3:
            actual_message = "FORWARD "+ self.currClient + "\nContent-length: "+str(c_length)+"\n\n"+message
        else:
            actual_message = "FORWARD "+ self.currClient + "\nContent-length: "+str(c_length)+"\nSignature: "+signature+"\n\n"+message

        s_sock.send(encrypt_decrypt(actual_message))
        ack = encrypt_decrypt(s_sock.recv(1024),False)
        # print ("Ack after receving the message is: "+ ack)
        return ack

    def client_operations(self):
        while True:
            data = encrypt_decrypt(self.receiveSocket.recv(1024),False)
            # print (data)
            split_data = [ line.split() for line in (data.split("\n"))]
            # print (len(split_data))
            try:
                if split_data[0][0] == "REGISTER":
                    username = split_data[0][2]
                    if reg_match("^[a-zA-Z0-9]+$", username):
                        self.sendSocket.send(encrypt_decrypt("REGISTERED "+ split_data[0][1]+" "+username+"\n\n"))
                        if split_data[0][1] == "TORECV":
                            users.append(username)
                            pub_key = None
                            if MODE != 1:
                                pub_key = (self.receiveSocket.recv(1024))
                            user_dic[username] = (self.receiveSocket,self.sendSocket,pub_key)
                            self.currClient = username
                    else:
                        self.sendSocket.send(encrypt_decrypt("ERROR 100 Malformed username\n\n"))
                elif (split_data[0][0] == "SEND"):
                    recipent = split_data[0][1].lstrip("@")
                    if MODE != 1:
                        self.receiveSocket.send((user_dic[recipent][2])) #Sending the public key.
                        data = encrypt_decrypt(self.receiveSocket.recv(1024),False)
                        split_data = [ line.split() for line in (data.split('\n'))]
                        recipent = split_data[0][1].lstrip('@')
                    c_length = split_data[1][1]
                    if MODE !=3:
                        message = "\n".join([" ".join(line) for line in split_data[3:]])
                        signature = None
                    else:
                        signature = split_data[2][1]
                        message = "\n".join([" ".join(line) for line in split_data[4:]])

                    if recipent not in users:
                        #If send user doesn't exist
                        self.receiveSocket.send(encrypt_decrypt("ERROR 102 Unable to send\n\n"))
                    elif(len(split_data)<4): #This condiiton is for header incomplete
                        self.receiveSocket.send(encrypt_decrypt("ERROR 103 Header incomplete\n\n"))
                        self.receiveSocket.close()
                        self.sendSocket.close()
                    else:
                        #Send the message
                        ack = self.forward_message(recipent,c_length,message,signature)
                        tmp_ack =  [line.split() for line in ack.split("\n")]
                        if tmp_ack[0][0] == "RECEIVED":
                            self.receiveSocket.send(encrypt_decrypt("SENT "+recipent+"\n\n"))
                        else:
                            # if (tmp_ack[0][1] == "103"):
                            self.receiveSocket.send(encrypt_decrypt("ERROR 102 Unable to send\n\n"))

                else:
                    if data == "UNREGISTER":
                        users.remove(self.currClient)
                        user_dic.pop(self.currClient,None)

                        self.sendSocket.send(encrypt_decrypt("EXIT"))
                    # print("Normal data from "+username+": "+ str(data))
                    self.sendSocket.send(encrypt_decrypt("Dummy to allow next loop.\n"))
                    # pass
            except IndexError:
                break


    def run(self):
       # while True:
        print ("Server waiting for data from client: ")
        self.client_operations()
        print ("Client's connection closed.")
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
        send_socket.listen(5)
        receive_socket.listen(5)
        r_conn, r_address = receive_socket.accept()
        s_conn, s_address = send_socket.accept()
        # client_lock.acquire()
        newthread = ClientPerThread(r_conn, s_conn)
        newthread.start()
        threads.append(newthread)
        print ("Accepted  receive connection from: "+ str(r_address))
        print ("Accepted send connection from: " + str(s_address))
        # newthread.join()

        # data = b"DUMMY"
        # start_new_thread(thread_client, (conn,conn2,data))

main_server_body()
