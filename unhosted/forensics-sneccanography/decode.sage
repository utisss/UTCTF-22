from PIL import Image

im = Image.open('snek2.png')

w, h = im.size
pixels = im.load()

evals = []
for i in range(h):
    evals.append([])
    x = 0
    for j in range(w):
         x += (pixels[j,i][0] & 1) << (j % 7)
         if j % 7 == 6:
            evals[i].append(x)
            x = 0

expec = [10, 13, 94, 51, 0, 118, 9, 30, 12, 101, 60, 82, 63, 31, 121, 95, 13, 120, 117, 124, 67, 42, 105, 70, 77, 59, 56, 108, 85, 32, 109, 5, 24, 20, 55, 6, 50, 101, 32, 10, 121, 4, 80, 75, 22, 34, 104, 65, 11, 2, 59, 103, 3, 52, 123, 60, 12, 31, 121, 73, 109, 43, 43, 40, 47, 61, 63, 29, 49, 51, 41, 48, 92, 90, 101, 76, 22, 91, 122, 76, 78, 24, 74, 73, 110, 32, 118, 56, 73, 54, 16, 28, 56, 45, 61, 113, 92, 66, 69, 63, 104, 40, 126, 53, 83, 87, 116, 61, 42, 21, 24, 38, 110, 121, 62, 110, 40, 19, 56, 31, 59, 8, 14, 45, 109, 92, 124, 82]

F = GF(128, repr='int')
C = codes.GeneralizedReedSolomonCode([F(Integer(x).bits()) for x in range(128)], 64)
D = codes.decoders.GRSBerlekampWelchDecoder(C)

full_decode = []
for codeword in evals:
    try:
        decoded = [x for x in D.decode_to_message(vector(([F(x.bits()) for x in codeword])))]

        full_decode += decoded
    except:
        break

print(len(full_decode))

for i in range(0,len(full_decode), 128):
    decoded = [x for x in D.decode_to_message(vector(full_decode[i:i+128]))]
    print(''.join([chr(int(str(x))) for x in decoded]), end='')
