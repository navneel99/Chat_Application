from _thread import *
import threading
import socket
import re

def reg_match(regex, string):
    return (len(re.findall(regex,string))==0?False:True)


client_lock = threading.Lock()
# The function sends data to the client and then receives data from the client to return to its main function
def thread_client(r_sock,s_sock, send_data):
   while True:
        if send_data:
            s_sock.send(send_data) #Need to preprocess this data before sending.    
        print ("Server waiting for data from client: ")
        inp_data = r_sock.recv(1024)
        if not inp_data:
            print("Breaking: ")
            client_lock.release()
            break
        else:
            print ("Data from client: ", inp_data)
   print ("Exited form the thread.\n")
   return inp_data


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
    
    send_socket.listen()
    receive_socket.listen()
    while True:
        conn,address = receive_socket.accept()
        conn2, address2 = send_socket.accept()
        client_lock.acquire()
        print ("Accepted  receive connection from: "+ str(address))
        print ("Acceoted send connection from: " + str(address2))
        conn2.send(b"You have connected to the server")
        data = b"DUMMY"
        start_new_thread(thread_client, (conn,conn2,data))
    
main_server_body()
