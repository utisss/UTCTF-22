msg = """Hello! I will send you the flag in a second. Something funny happened though! I picked up my keyboard, but the keys were in weird places.
I don't know what happened, but it's okay since I stare at the keyboard anyways :)

|Also I've had a crush on you for years, do you want to go out with me?|
Anyways, here is the flag (hopefully): utflag{SubStiTuTIoN_cIPhEr_I_hArDLy_kNoW_hEr}
"""

keycodes = []

cnt = -1
for x in msg:
    if x.isupper():
        keycodes += ["shift"]
        keycodes += [x.lower()]
    elif x.islower() or x == ' ' or x == '.' or x == ',' or x == '\'' or x == '\n':
        keycodes += [x]
    elif x == '?':
        keycodes += ["shift"]
        keycodes += ["/"]
    elif x == ':':
        keycodes += ["shift"]
        keycodes += [";"]
    elif x == '!':
        keycodes += ["shift"]
        keycodes += ["1"]
    elif x == ')':
        keycodes += ["shift"]
        keycodes += ["0"]
    elif x == '(':
        keycodes += ["shift"]
        keycodes += ["9"]
    elif x == '_':
        keycodes += ["shift"]
        keycodes += ["-"]
    elif x == '{':
        keycodes += ["shift"]
        keycodes += ["["]
    elif x == '}':
        keycodes += ["shift"]
        keycodes += ["]"]
    elif x == '|':
        if cnt == -1:
            cnt = 0
        else:
            for _ in range(cnt-1):
                keycodes += ["backspace"]
    else:
        print("need to do ", x)

    if cnt != -1:
        cnt += 1

m = {}
for x in keycodes:
    m[x] = ''

s = 'abcdefghijklmnopqrstuvwxyz1234567890-=[];,./'
s = [x for x in s]

import random
for x in m:
    c = s[random.randrange(len(s))]
    m[x] = c
    print(x, ": ", c)
    s.remove(c)

for x in keycodes:
    print(m[x], end='')
