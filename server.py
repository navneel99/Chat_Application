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
users = []
class ClientPerThread(threading.Thread):
    def __init__(self,r_sock,s_sock):
        threading.Thread.__init__(self)
        self.receiveSocket = r_sock
        self.sendSocket = s_sock

    def client_operations(self):
        while True:
            data = encrypt_decrypt(self.receiveSocket.recv(1024),False)
            split_data = [ line.split() for line in (data.split("\n"))]
            # print (split_data)
            if split_data[0][0] == "REGISTER":
                username = split_data[0][2]
                if reg_match("[a-zA-Z0-9]+", username):
                    # print("regex correct")
                    users.append((username))
                    print ("REGISTERED "+ split_data[0][1]+" "+username+"\n \n\n")
                    self.sendSocket.send(encrypt_decrypt("REGISTERED "+ split_data[0][1]+" "+username+"\n \n\n"))
                else:
                    self.sendSocket.send(encrypt_decrypt("ERROR 100 Malformed username\n \n\n"))
            else:
                print("Normal data from "+username+": "+ str(data))
                self.sendSocket.send(encrypt_decrypt("Dummy to allow next loop.\n"))
                # pass


    def run(self):
       while True:
            # send_data = b"True"
            # if send_data:
                # self.sendSocket.send(send_data) #Need to preprocess this data before sending.
            print ("Server waiting for data from client: ")
            # inp_data = self.receiveSocket.recv(1024)
            self.client_operations()
            # if not inp_data:
                # print("Breaking: ")
                # client_lock.release()
                # break
            # else:
                # print ("Data from client: ", inp_data)
       print ("Exited form the thread.\n")
       # return inp_data



def main_server_body():
    ip = "127.0.0.1"
    r_port = 6969
    s_port = 6970

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
