import socket
import select
import struct
import string
import sys

# global area
serverip = "61.155.8.130"
serverport = 350
loginuser = 'dttest'
loginpass = 'test'

session = ''

def conn(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    errno = s.connect_ex((ip, port))
    return s, errno
    
def login(socket, username, password):
    loginhead = 1
    loginlength = 162
    # replace these values
    loginmac = '14DAE9BE3EF2'
    loginip = '192.168.1.107  '
    loginversion = '3911010'
    loginsubversion = '000000'
    loginstruct = struct.pack("2B16s32s12s15s8s77s", loginhead,
                              loginlength, username, password,
                              loginmac, loginip, loginversion,
                              loginsubversion)
    
    sendcount = socket.send(loginstruct)
    return validlogin(peekdata(socket))

def validlogin(data):
    if data == None:
        return False
    if ((ord(data[1]) == len(data)) and (ord(data[2]) == 1) ):
        return True
    return False

def peekdata(socket):
    infd, outfd, errfd = select.select([socket,],[],[],5)
    if len(infd) != 0:
        data = socket.recv(1024)
        # TODO: how to solve socket data packing problem?
        #print '[dbg] talk respond size', len(data)
        return data
    else:
        return None

def hello(socket):
    sendcount = socket.send(pack_so())
    if parse_oc(peekdata(socket)) == False:
        return False
    return unpack_data(peekdata(socket))

def pack_so():
    ver = 1
    so = 0xfe
    length = 0x11
    coding = 0x14    #ascii
    subtype = 0x10
    rfu = 0
    mpx = 0
    hdr = 0
    pres = 2 # p1024c presentation
    mix = mpx << 6 | hdr << 4 | pres
    h1 = h2 = reserve = ascu = 0
    word = struct.pack('>2BH6BHB2H',ver,so,length,coding,subtype,
                       rfu,mix,h1,h2,rfu,reserve,rfu,ascu)
    #for traits in word:
    #    print '%x'%ord(traits)
    return word

def unpack_oc(data):
    if len(data) < 6:
        return False
    ver, oc, length = struct.unpack_from('>2BH', data)
    if ver != 1 or oc != 0xfd or length != len(data):
        return False
    return True

def strip_oncemore(data):
    head = 0
    tail = len(data) - 1
    while True:
        if data[head] == '\x02':
            head += 1
        else:
            break
    while True:
        if data[tail] == '\x03':
            tail -= 1
        else:
            break
    #print '[dbg] head', head, 'tail ', tail
    return data[head:tail+1]
        
def unpack_data(data):
    if len(data) < 13:
        return False
    ver, dat, length, id, a2, sid, stx, text, etx =\
         struct.unpack_from('>2BHLBHB%dsB'%(len(data) - 13), data)
    if ver != 1 or dat != 0 or length != len(data) or stx != 2 or etx != 3:
        return False
    # set global session
    global session
    session = struct.pack('>LBH', id, a2, sid)
    #print '[dbg] session set, length ', len(session)
    text = strip_oncemore(text)
    display_info(text)
    return True
    
def parse_oc(data):
    return unpack_oc(data)

def display_info(data):
    i = 0
    ascii_mode = True   #False for gb2312 mode
    text = ''
    while i < len(data):
        if data[i] == '\x1b':
            # control
            if data[i+1] == '\x0f':
                # ascii
                ascii_mode = True
                i += 2
            elif data[i+1] == '\x0e':
                # gb2312
                ascii_mode = False
                i += 2
            elif data[i+1] == '\x09':
                # print a dot
                text = text + '<dot>'
                i += 2
            elif data[i+1] == '\x0b':
                # skip next 3 letters
                i += 5
            elif data[i+1] == '\x4d':
                # unknown
                ascii_mode = True
                i += 2
            elif data[i+1] == '\x62':
                # unknown
                ascii_mode = True
                i += 2
            else:
                # unknown
                i += 2
        else:
            if ascii_mode:
                # display as usual
                if data[i] == '\x1c':
                    text = text + '<1c>'
                elif data[i] == '\x1d':
                    text = text + '<1d>'
                elif data[i] == '\x0d':
                    text = text + '\n'
                else:
                    text = text + data[i]
                i += 1
            else:
                # gb2312 mode, convert chinese
                text = text + et2gb(data[i:i+2])
                i += 2
    #print 'responds'
    #print 'first bytes %x %x %x'%(ord(text[0]), ord(text[1]), ord(text[2]))
    print text
    return

def et2gb(word):
    first = ord(word[0])
    second = ord(word[1])
    if first < 0x30:
        first += 142
    else:
        first += 128
    second += 128
    # pain!
    if word == b'\x27\x23':
        return b'\xb1\xb1'
    return struct.pack('2B', first, second)

def gb2et(word):
    first = ord(word[0])
    second = ord(word[1])
    if first < 179:
        first -= 142
    else:
        first -= 128
    second -= 128
    # pain!
    if word == b'\xb1\xb1':
        return b'\x27\x23'
    return struct.pack('2B', first, second)

def parse_text(cmd):
    # fixed header
    text = b'\x1b\x0b\x20\x20\x00\x0f\x1e'
    # start with ascii mode
    ascii_mode = True
    i = 0
    while i < len(cmd):
        if ascii_mode:
            if ord(cmd[i]) > 127:
                # switch to gb mode
                ascii_mode = False
                text = text + b'\x1b\x0e'
                text = text + gb2et(cmd[i:i+2])
                i += 2
            else:
                text = text + cmd[i]
                i += 1
        else:
            if ord(cmd[i]) < 128:
                # switch to ascii mode
                ascii_mode = True
                text = text + b'\x1b\x0f'
                text = text + cmd[i]
                i += 1
            else:
                text = text + gb2et(cmd[i:i+2])
                i += 2
    # there shall be a space at the tail
    # switch back to ascii
    if ascii_mode == False:
        text = text + b'\x1b\x0f'
        ascii_mode = True
    text = text + ' '
    return text

def pack_cmd(cmd):
    ver = 1
    data = 0
    stx = 2
    etx = 3
    text = parse_text(cmd)
    length = len(text) + 13 # need calculate
    global session
    #print '[dbg] session length ', len(session)
    word = struct.pack('>2BH7sB%dsB'%(len(text)),ver,data,length,session,stx,text,etx)
    #for traits in word:
    #    print '%x'%ord(traits)
    return word

def talk(socket, text):
    sendcount = socket.send(pack_cmd(text))
    unpack_data(peekdata(socket))

def main():
    print 'connecting to server...'
    socket, errno = conn(serverip, serverport)
    if errno == 0:
        print 'connect success!'
    else:
        print 'connect failed, errno is ', errno
        sys.exit()
    if login(socket, loginuser, loginpass):
        print 'login success!'
    else:
        print 'login failed!'
        sys.exit()
    if hello(socket):
        pass
    else:
        print 'say hello failed!'
        sys.exit()

    #accept user input
    while True:
        newline = raw_input('>')
        talk(socket, newline)

main()
