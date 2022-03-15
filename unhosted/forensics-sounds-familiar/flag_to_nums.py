#! /usr/bin/python3

from base64 import b64encode as b64

flag = 'utctf{5ecret_f1@9_do_not_5h@re}'
b64_encoded = str(b64(flag.encode('ascii')), 'ascii')

print('base64: ' + b64_encoded)

print('digits are: ')
out = ''
for char in list(b64_encoded):
    num = ord(char)
    out = out + str(num) + ' '

print('\t' + out)
