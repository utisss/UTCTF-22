from random import shuffle, choice
import os
import uuid
from subprocess import Popen, PIPE, STDOUT
import signal

def gen_binary():
    ORDER = list(range(1,9))
    shuffle(ORDER)
    LR_AMOUNT = choice(list(range(1,256)))
    RR_AMOUNT = choice(list(range(1,256)))
    LRG_SIZE = choice(list([2,4,8,16,32,64,128,256]))
    RRG_SIZE = choice(list([2,4,8,16,32,64,128,256]))
    RG_SIZE = choice(list([2,4,8,16,32,64,128,256]))
    path = "/tmp/" + str(uuid.uuid4())

    cmd = f"gcc -no-pie -o {path}"
    cmd += f" -DLR_AMOUNT={LR_AMOUNT}"
    cmd += f" -DRR_AMOUNT={RR_AMOUNT}"
    cmd += f" -DLRG_SIZE={LRG_SIZE}"
    cmd += f" -DRRG_SIZE={RRG_SIZE}"
    cmd += f" -DRG_SIZE={RG_SIZE}"
    for i in range(1,9):
        cmd += f" -DPERMUTATION{i}='permute{ORDER[i-1]}(buf);'"
    cmd += " /template.c"

    os.system(cmd)
    return path

def trial():
    path = gen_binary()
    with Popen(["xxd", path], stdout=PIPE) as proc:
        print(proc.stdout.read().decode('ascii'))
    print()

    def interrupt(signum, frame):
        raise Exception("timed out")
    signal.signal(signal.SIGALRM, interrupt)

    user_in = None
    signal.alarm(60)
    good_exit_code = choice(list(range(0,256)))
    try:
        print("Binary should exit with code",good_exit_code)
        print("You have 60 seconds to provide input: ")
        x = os.read(0, 513)
        user_in = x
    except:
        print("Too slow!")
        os.system("rm %s" % path)
        exit()

    signal.alarm(0)
    p = Popen([path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    output = p.communicate(input=user_in)[0]
    print("Process exited with return code %d" % p.returncode)
    if(p.returncode != good_exit_code):
        exit(0)


print("You will be given 10 randomly generated binaries.")
print("You have 60 seconds to solve each one.")
print("Solve the binary by making it exit with the given exit code")
print("Press enter when you're ready for the first binary.")

x = input()

for i in range(10):
    trial()

print("Congrats!")
print("utflag{you_mix_me_right_round_baby_right_round135799835}")
