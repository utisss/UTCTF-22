# \[Forensics\] - Sounds Familiar

#### Points = 200

## Prompt

You have one new message. Main menu. To listen to your messages press one.

#### Hints

1. Pay attention to how the numbers are clustered.

## Provided Files

- [Strange Sounds](./super_strange.wav) - link to files


## Write Up

<u>DTMF Tones</u>

- if you look up dialing sounds you will probably find out that they are called DTMF tones.
- knowing that you can use an online [decoder](http://www.dialabc.com/sound/detect/index.html)
- after grouping the digits the way they're dialed you should end up with this:
`100 88 82 106 100 71 90 55 78 87 86 106 99 109 86 48 88 50 89 120 81 68 108 102 90 71 57 102 98 109 57 48 88 122 86 111 81 72 74 108 102 81 61 61`

<u>Ascii</u>

- since all the digits are in the range \[0, 127\] you can probably guess they're ascii.
- there are many tools that will can convert these numbers to ascii or you can do it easily in python using the `chr()` function.
- result: dXRjdGZ7NWVjcmV0X2YxQDlfZG9fbm90XzVoQHJlfQ==

<u>Base64</u>

- the resulting string can be decoded from base64 in python.
- you can also use [CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true)&input=ZFhSamRHWjdOV1ZqY21WMFgyWXhRRGxmWkc5ZmJtOTBYelZvUUhKbGZRPT0)

## Flag

utctf{5ecret_f1@9_do_not_5h@re}
