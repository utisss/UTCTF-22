import random
from PIL import Image

im = Image.open('snek2.png')
w,h = im.size
pixels = im.load()
for _ in range(10000):
    j = random.randrange(w)
    i = random.randrange(h)
    k = random.randrange(3)
    r,g,b = pixels[j,i]
    pixels[j,i] = (random.randrange(256), random.randrange(256), random.randrange(256))

im.save('snek3.png')
