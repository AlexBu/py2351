import socket

serverport = 350
serverip = "61.155.8.130"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("hello world", (serverip, serverport))
data, addr = s.recvfrom(1024)
print "recerived:", data