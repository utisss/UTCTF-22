import base64
from pwn import *

ADDRESS = 'localhost'
PORT = 3000

BYTES = 146

def urlsafe_b64decode_nopad(data):
	pad = b'=' * (4 - (len(data) & 3))
	return base64.urlsafe_b64decode(data + pad)

c1 = connect(ADDRESS, PORT)
c2 = connect(ADDRESS, PORT)

z = ("A" * (BYTES - 1) + '\n').encode()
c1.send(z)
c2.send(z)
x1 = urlsafe_b64decode_nopad(c1.recvline()[len('flag: '):-1])
y1 = urlsafe_b64decode_nopad(c1.recvline()[len('out:  '):-1])
x2 = urlsafe_b64decode_nopad(c2.recvline()[len('flag: '):-1])
y2 = urlsafe_b64decode_nopad(c2.recvline()[len('out:  '):-1])
c1.close()
c2.close()

assert(y1[-40:-16] == x2[-40:-16])

print(''.join(chr(a^b^c) for a, b, c in zip(x2[:-40], y1[:-40], z)))

