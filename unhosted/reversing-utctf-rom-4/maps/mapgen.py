import imageio as iio
import sys

img = iio.imread(sys.argv[1])

print(img.shape)

res = [0] * (18 * 5) #5 bytes per row

for i in range(18):
    for j in range(20):
        pix = 2 # 2-bit quantity
        if (img[i, j][:3] == [0, 0, 0]).all():
            pix = 1
        elif (img[i, j][:3] == [255, 255, 255]).all():
            pix = 0
        
        res[i * 5 + j // 4] |= pix << (2 * (j % 4))

print(", ".join(map(str, res)))