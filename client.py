import socket
import struct
import string

def conn(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    errno = s.connect_ex((ip, port))
    if errno != 0:
        print "errno is ", errno
    return s
    
def login(socket, username, password):

    loginhead = 1
    loginlength = 162
    loginmac = '14DAE9BE3EF2'
    loginip = '192.168.1.107  '
    loginversion = '3911010'
    loginsubversion = '000000'
    loginstruct = struct.pack("BB16s32s12s15s8s77s", loginhead,
                              loginlength, username, password,
                              loginmac, loginip, loginversion,
                              loginsubversion)
    
    sendcount = socket.send(loginstruct)
    data = socket.recv(1024)
    
    validlogin(data)

def validlogin(data):
    if ((ord(data[1]) == len(data)) and (ord(data[2]) == 1) ):
        print 'login success!'
    else:
        print data

def talk(socket, sentence):
    socket.send(sentence)
    data = socket.recv(1024)

def hello(socket):
    word = b'\0x01\0xfe\0x00\0x11\0x14\0x10\0x00\0x02\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00\0x00'
    talk(socket, word)
    
serverip = "61.155.8.130"
serverport = 350

loginuser = 'dttest'
loginpass = 'test'
#loginpass = 'test2' # wrong pass!

socket = conn(serverip, serverport)
login(socket, loginuser, loginpass)

setence = b'\x01\x02'
hello(socket, setence)
