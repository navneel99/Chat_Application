from _thread import *
import threading
import socket
import re
from socketserver import ThreadingMixIn

def reg_match(regex, string):
    return (False if len(re.findall(regex,string)) ==0 else True)
# client_lock = threading.Lock()
# The function sends data to the client and then receives data from the client to return to its main function

class ClientPerThread(threading.Thread):
    def __init__(self,r_sock,s_sock):
        threading.Thread.__init__(self)
        self.receiveSocket = r_sock
        self.sendSocket = s_sock

    def run(self):
       while True:
            send_data = b"True"
            if send_data:
                self.sendSocket.send(send_data) #Need to preprocess this data before sending.
            print ("Server waiting for data from client: ")
            inp_data = self.receiveSocket.recv(1024)
            if not inp_data:
                print("Breaking: ")
                # client_lock.release()
                break
            else:
                print ("Data from client: ", inp_data)
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
        s_conn.send(b"You have connected to the server")
        data = b"DUMMY"
        # start_new_thread(thread_client, (conn,conn2,data))

main_server_body()
