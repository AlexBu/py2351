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
    loginrespondstr = b'\x00\x14\x01\x00\x03\x00\x00\x00\x39\xd1\x0c\x00\x00\x8c\x8c\x29\x00\x00\xa9\xa9'
    loginstruct = struct.pack("BB16s32s12s15s8s77s", loginhead,
                              loginlength, username, password,
                              loginmac, loginip, loginversion,
                              loginsubversion)
    #for traits in loginstruct:
    #    print '%x' %ord(traits)
    
    sendcount = socket.send(loginstruct)
    #print "send bytes ", sendcount
    data = socket.recv(1024)
    #print ('received: ', data)
    #print ('expected: ', loginrespondstr)
    if cmp(loginrespondstr, data) == 0:
        print 'login success!'
    else:
        print 'login failed!'

def talk(socket, setence):
    print 'talk() not implemented'
    
serverip = "61.155.8.130"
serverport = 350

loginuser = 'dttest'
loginpass = 'test'

socket = conn(serverip, serverport)
login(socket, loginuser, loginpass)

setence = b'\x01\x02'
talk(socket, setence)
