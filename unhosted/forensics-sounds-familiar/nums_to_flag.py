#! /usr/bin/python3

from base64 import b64decode as b64

nums = """100 88 82 106 100 71 90 55 78 87 86 106 99 109 86 48 88 50 89 120 81
    68 108 102 90 71 57 102 98 109 57 48 88 122 86 111 81 72 74 108 102 81 61
    61"""

b64_string = []

# convert from ascii to string
for num in nums.split():
    b64_string.append(chr(int(num)))

b64_string = ''.join(b64_string)

# decode base64
enc_bytes = bytes(b64_string, 'ascii')
dec_bytes = b64(enc_bytes)
flag = str(dec_bytes, 'ascii')

print(flag)
