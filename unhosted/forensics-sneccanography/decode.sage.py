

# This file was *autogenerated* from the file decode.sage
from sage.all_cmdline import *   # import sage library

_sage_const_0 = Integer(0); _sage_const_1 = Integer(1); _sage_const_7 = Integer(7); _sage_const_6 = Integer(6); _sage_const_10 = Integer(10); _sage_const_13 = Integer(13); _sage_const_94 = Integer(94); _sage_const_51 = Integer(51); _sage_const_118 = Integer(118); _sage_const_9 = Integer(9); _sage_const_30 = Integer(30); _sage_const_12 = Integer(12); _sage_const_101 = Integer(101); _sage_const_60 = Integer(60); _sage_const_82 = Integer(82); _sage_const_63 = Integer(63); _sage_const_31 = Integer(31); _sage_const_121 = Integer(121); _sage_const_95 = Integer(95); _sage_const_120 = Integer(120); _sage_const_117 = Integer(117); _sage_const_124 = Integer(124); _sage_const_67 = Integer(67); _sage_const_42 = Integer(42); _sage_const_105 = Integer(105); _sage_const_70 = Integer(70); _sage_const_77 = Integer(77); _sage_const_59 = Integer(59); _sage_const_56 = Integer(56); _sage_const_108 = Integer(108); _sage_const_85 = Integer(85); _sage_const_32 = Integer(32); _sage_const_109 = Integer(109); _sage_const_5 = Integer(5); _sage_const_24 = Integer(24); _sage_const_20 = Integer(20); _sage_const_55 = Integer(55); _sage_const_50 = Integer(50); _sage_const_4 = Integer(4); _sage_const_80 = Integer(80); _sage_const_75 = Integer(75); _sage_const_22 = Integer(22); _sage_const_34 = Integer(34); _sage_const_104 = Integer(104); _sage_const_65 = Integer(65); _sage_const_11 = Integer(11); _sage_const_2 = Integer(2); _sage_const_103 = Integer(103); _sage_const_3 = Integer(3); _sage_const_52 = Integer(52); _sage_const_123 = Integer(123); _sage_const_73 = Integer(73); _sage_const_43 = Integer(43); _sage_const_40 = Integer(40); _sage_const_47 = Integer(47); _sage_const_61 = Integer(61); _sage_const_29 = Integer(29); _sage_const_49 = Integer(49); _sage_const_41 = Integer(41); _sage_const_48 = Integer(48); _sage_const_92 = Integer(92); _sage_const_90 = Integer(90); _sage_const_76 = Integer(76); _sage_const_91 = Integer(91); _sage_const_122 = Integer(122); _sage_const_78 = Integer(78); _sage_const_74 = Integer(74); _sage_const_110 = Integer(110); _sage_const_54 = Integer(54); _sage_const_16 = Integer(16); _sage_const_28 = Integer(28); _sage_const_45 = Integer(45); _sage_const_113 = Integer(113); _sage_const_66 = Integer(66); _sage_const_69 = Integer(69); _sage_const_126 = Integer(126); _sage_const_53 = Integer(53); _sage_const_83 = Integer(83); _sage_const_87 = Integer(87); _sage_const_116 = Integer(116); _sage_const_21 = Integer(21); _sage_const_38 = Integer(38); _sage_const_62 = Integer(62); _sage_const_19 = Integer(19); _sage_const_8 = Integer(8); _sage_const_14 = Integer(14); _sage_const_128 = Integer(128); _sage_const_64 = Integer(64)
from PIL import Image

im = Image.open('snek2.png')

w, h = im.size
pixels = im.load()

evals = []
for i in range(h):
    evals.append([])
    x = _sage_const_0 
    for j in range(w):
         x += (pixels[j,i][_sage_const_0 ] & _sage_const_1 ) << (j % _sage_const_7 )
         if j % _sage_const_7  == _sage_const_6 :
            evals[i].append(x)
            x = _sage_const_0 

expec = [_sage_const_10 , _sage_const_13 , _sage_const_94 , _sage_const_51 , _sage_const_0 , _sage_const_118 , _sage_const_9 , _sage_const_30 , _sage_const_12 , _sage_const_101 , _sage_const_60 , _sage_const_82 , _sage_const_63 , _sage_const_31 , _sage_const_121 , _sage_const_95 , _sage_const_13 , _sage_const_120 , _sage_const_117 , _sage_const_124 , _sage_const_67 , _sage_const_42 , _sage_const_105 , _sage_const_70 , _sage_const_77 , _sage_const_59 , _sage_const_56 , _sage_const_108 , _sage_const_85 , _sage_const_32 , _sage_const_109 , _sage_const_5 , _sage_const_24 , _sage_const_20 , _sage_const_55 , _sage_const_6 , _sage_const_50 , _sage_const_101 , _sage_const_32 , _sage_const_10 , _sage_const_121 , _sage_const_4 , _sage_const_80 , _sage_const_75 , _sage_const_22 , _sage_const_34 , _sage_const_104 , _sage_const_65 , _sage_const_11 , _sage_const_2 , _sage_const_59 , _sage_const_103 , _sage_const_3 , _sage_const_52 , _sage_const_123 , _sage_const_60 , _sage_const_12 , _sage_const_31 , _sage_const_121 , _sage_const_73 , _sage_const_109 , _sage_const_43 , _sage_const_43 , _sage_const_40 , _sage_const_47 , _sage_const_61 , _sage_const_63 , _sage_const_29 , _sage_const_49 , _sage_const_51 , _sage_const_41 , _sage_const_48 , _sage_const_92 , _sage_const_90 , _sage_const_101 , _sage_const_76 , _sage_const_22 , _sage_const_91 , _sage_const_122 , _sage_const_76 , _sage_const_78 , _sage_const_24 , _sage_const_74 , _sage_const_73 , _sage_const_110 , _sage_const_32 , _sage_const_118 , _sage_const_56 , _sage_const_73 , _sage_const_54 , _sage_const_16 , _sage_const_28 , _sage_const_56 , _sage_const_45 , _sage_const_61 , _sage_const_113 , _sage_const_92 , _sage_const_66 , _sage_const_69 , _sage_const_63 , _sage_const_104 , _sage_const_40 , _sage_const_126 , _sage_const_53 , _sage_const_83 , _sage_const_87 , _sage_const_116 , _sage_const_61 , _sage_const_42 , _sage_const_21 , _sage_const_24 , _sage_const_38 , _sage_const_110 , _sage_const_121 , _sage_const_62 , _sage_const_110 , _sage_const_40 , _sage_const_19 , _sage_const_56 , _sage_const_31 , _sage_const_59 , _sage_const_8 , _sage_const_14 , _sage_const_45 , _sage_const_109 , _sage_const_92 , _sage_const_124 , _sage_const_82 ]

F = GF(_sage_const_128 , repr='int')
C = codes.GeneralizedReedSolomonCode([F(Integer(x).bits()) for x in range(_sage_const_128 )], _sage_const_64 )
D = codes.decoders.GRSBerlekampWelchDecoder(C)

full_decode = []
for codeword in evals:
    try:
        decoded = [x for x in D.decode_to_message(vector(([F(x.bits()) for x in codeword])))]

        full_decode += decoded
    except:
        break

print(len(full_decode))

for i in range(_sage_const_0 ,len(full_decode), _sage_const_128 ):
    decoded = [x for x in D.decode_to_message(vector(full_decode[i:i+_sage_const_128 ]))]
    print(''.join([chr(int(str(x))) for x in decoded]), end='')

