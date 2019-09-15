import socket
from _thread import *
import threading
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
import base64
import pickle
import hashlib

MODE=2
def encrypt_decrypt(data,flag=True): #True flag means encryption
    if flag:
        return bytes(data, encoding="ascii")
    else:
        return (data.decode(encoding = "ascii"))

class forwardThread(threading.Thread):
    def __init__(self,receive_socket):
        threading.Thread.__init__(self)
        self.receiveSocket = receive_socket

    def run(self):
        while True:
            # if (MODE != 1):
                # pub_key = encrypt_decrypt(pickle.loads(self.receiveSocket.recv(1024)),False) #public key received
            fwdm = encrypt_decrypt(self.receiveSocket.recv(1024),False)
            if fwdm == "EXIT":
                break
            chk = [ line.split() for line in fwdm.split('\n')]
            # print ("Receiver Client: ")
            # print(chk[3][0])
            # print("------------------------")
            if MODE != 1:
                actual_message = encrypt_decrypt(decrypt_message(priv_key, chk[3][0]),False)
            else:
                actual_message = "\n".join([ " ".join(line) for line in chk[3:]])
            if len(chk)<=3:
                #Bad Header
                self.receiveSocket.send(encrypt_decrypt("ERROR 103 Header incomplete\n\n"))
            else:

                print("----MESSAGE START----")
                print ("From: " + chk[0][1]+"\n")
                print(actual_message)
                print ("----MESSAGE END----")
                self.receiveSocket.send(encrypt_decrypt("RECEIVED "+ chk[0][1]+"\n\n"))


class sendThread(threading.Thread):
    def __init__(self,send_socket):
        threading.Thread.__init__(self)
        self.sendSocket = send_socket


    def send_message(self,inp):
         tmp = inp.split()
         recipent = tmp[0]
         message = ' '.join(tmp[1:])
         if (MODE !=1):
             prelim_message = "SEND "+recipent+"\n"
             # print(prelim_message + " CREATED")
             self.sendSocket.send(encrypt_decrypt(prelim_message))
             # print(prelim_message + " SENT")
             # to_pub_key = encrypt_decrypt((self.sendSocket.recv(1024)),False) #encrypt with recipent's public key
             to_pub_key = (self.sendSocket.recv(1024))
             # print("Public key received,")
             encrypted_message = encrypt_message(to_pub_key,message)

         c_l = len(message)
         if MODE == 1:
             actual_message = "SEND "+recipent+"\nContent-length: "+str(c_l)+"\n\n"+message
         else:
             actual_message = "SEND "+recipent+"\nContent-length: "+str(c_l)+"\n\n"+encrypted_message
             # print("Message sent to the server: "+ actual_message)
         self.sendSocket.send(encrypt_decrypt(actual_message))

    def run(self):
        while True:
            print("Data should be of form @[recipent] [message]")
            inp = input("Enter data to be sent to the server. Type q to exit\n")
            if (inp.lower() == 'q'):
                self.sendSocket.send(encrypt_decrypt("UNREGISTER"))
                break
            else:
                test = inp.split()
                if (test[0][0] == "@") and len(test)>1:
                    self.send_message(inp)
                    data = encrypt_decrypt(self.sendSocket.recv(1024),False) #waiting for ack
                    tmp_data =  [line.split() for line in data.split('\n')]
                    if (tmp_data[0][0] == "SENT"):
                        print("Message sent successfully.")
                    else:
                        print("Some error from the server.")
                else:
                    print("Write the message again.")
                    continue

#Generating Keys for encryption
def keyGeneration():
    key = RSA.generate(2048)
    private_key = key.exportKey('PEM', pkcs = 8)
    public_key = key.publickey().exportKey('PEM', pkcs = 8)

    return public_key, private_key

def encrypt_message(key, message):
    rsa_key = RSA.importKey(key)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    message = str.encode(message)
    message = rsa_key.encrypt(message)
    encodedBytes = base64.b64encode(message)
    encodedStr = str(encodedBytes, "ascii")
    return encodedStr

def decrypt_message(key, message):
    rsa_key = RSA.importKey(key)
    rsa_key = PKCS1_OAEP.new(rsa_key)
    message = base64.b64decode(message)
    message = rsa_key.decrypt(message)
    return message

def SHAencryption(message, key):
  res = hashlib.sha256(message.encode())
  res = encrypt_message(key, str(res))
  return res


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
        # print (str(pub_key))
        if (MODE != 1):
            # s1.send(encrypt_decrypt(pickle.dumps(pub_key))) #Send the public key to the server to save.
            # print (pub_key)
            s1.send(pub_key)
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
    pub_key, priv_key = keyGeneration()
    if register_user(u_name, s1, s2):
        username_retry = False
    else:
        continue

thread1 = sendThread(s1)
thread2 = forwardThread(s2)
thread1.start()
thread2.start()

thread1.join()
thread2.join()

s1.close()
s2.close()
print ("Thanks for connecting!")
# thread2.join()
