import socket
import select
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
    print 'login respond size', len(data)
    
    validlogin(data)

def validlogin(data):
    if ((ord(data[1]) == len(data)) and (ord(data[2]) == 1) ):
        print 'login success!'
    else:
        print data

def talk(socket, sentence):
    sendcount = socket.send(sentence)
    data = socket.recv(1024)
    print 'talk respond size', len(data)
    # peek into data buffer for left
    # TODO: refactor, extract method
    # TODO: analyze & display incoming package
    # TODO: packing outgoing package
    while (True):
        infd, outfd, errfd = select.select([socket,],[],[],1)
        print len(infd), len(outfd), len(errfd)
        if len(infd) != 0:
            data = socket.recv(1024)
            print 'talk respond size', len(data)
        else:
            break

def hello(socket):
    word = b'\x01\xfe\x00\x11\x14\x10\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    talk(socket, word)
    
serverip = "61.155.8.130"
serverport = 350

loginuser = 'dttest'
loginpass = 'test'
#loginpass = 'test2' # wrong pass!

socket = conn(serverip, serverport)
login(socket, loginuser, loginpass)

hello(socket)
