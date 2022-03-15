from secret import secret
from PIL import Image
import galois

SZ = 128
GF = galois.GF(SZ)

def bin_rep(x):
    bits = []
    b = 1
    while(b < SZ):
        bits.append(1 if (x & b) else 0)
        b <<= 1
    return bits

def evaluate(c, x):
    y = GF(0)
    for k in range(len(c)):
        y += GF(c[k]) * (GF(x) ** k)
    return int(y)

def get_values(c):
    values = []
    for i in range(SZ):
        values.append(evaluate(c,i))
    return values

def get_bins(c):
    values = get_values(c)
    bins = []
    for v in values:
        bins += bin_rep(v)
    return bins

per_row = 64
secret = [ord(x) for x in secret]
secret += [0] * (per_row - len(secret) % per_row)

new_secret = []
for i in range(0, len(secret), per_row):
    new_secret += get_values(secret[i:i+per_row])
secret = new_secret

im = Image.open('snek.png')
w,h = im.size

mat = []

for i in range(len(secret) // per_row):
    mat.append(get_bins(secret[i*per_row:(i+1)*per_row]))

pixels = im.load()
for i in range(len(mat)):
    for j in range(w):
        r,g,b = pixels[j,i]
        r -= r & 1
        g -= g & 1
        b -= b & 1
        r += mat[i][j]
        g += mat[i][j]
        b += mat[i][j]
        pixels[j,i] = (r,g,b)


im.save('snek2.png')
