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
    validlogin(peekdata(socket))

def validlogin(data):
    if data == None:
        return
    if ((ord(data[1]) == len(data)) and (ord(data[2]) == 1) ):
        print 'login success!'
    else:
        print data

def peekdata(socket):
        infd, outfd, errfd = select.select([socket,],[],[],1)
        if len(infd) != 0:
            data = socket.recv(1024)
            print 'talk respond size', len(data)
            return data
        else:
            return None

def hello(socket):
    word = b'\x01\xfe\x00\x11\x14\x10\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sendcount = socket.send(word)
    # peek into data buffer for left
    # TODO: analyze & display incoming package
    # TODO: packing outgoing package
    validhello(peekdata(socket))
    validmatip(peekdata(socket))

def validhello(data):
    respond = struct.unpack_from(">BBHB", data)
    print respond
    return

def validmatip(data):
    respond = struct.unpack_from(">BBHL", data)
    print respond
    return

serverip = "61.155.8.130"
serverport = 350

loginuser = 'dttest'
loginpass = 'test'
#loginpass = 'test2' # wrong pass!

socket = conn(serverip, serverport)
login(socket, loginuser, loginpass)
hello(socket)
