a = [611419388, 949497417, 635006987, 487100496, 86189592, 846838527, 843866628, 884202049, 777085122, 369148275, 223107226, 78165507, 843983729, 830379085, 787770396, 301687547, 787770396, 830379085, 843983729, 78165507, 223107226, 369148275, 777085122, 884202049, 843866628, 846838527, 86189592, 487100496, 635006987, 949497417, 611419388, 405294199, 843701403, 852467167, 900572428, 983913047, 202927707, 332606583, 929467881, 38272706, 59045202, 494544793, 488348897, 863991991, 115669622, 152908102, 819130268, 769231203, 129800068, 524122617, 973960715, 227060963, 990419157, 972738310, 201501115, 307740310, 682892844, 990541751, 387599355, 925070104, 794853766, 126924931, 424592664, 400451889, 829654705, 946211592, 220286226, 570949625, 400898356, 579203127, 909370543, 909370543, 579203127, 400898356, 570949625, 220286226, 946211592, 829654705, 400451889, 424592664, 126924931, 794853766, 925070104, 387599355, 990541751, 682892844, 307740310, 201501115, 972738310, 990419157, 227060963, 973960715, 524122617, 129800068, 769231203, 819130268, 152908102, 115669622, 863991991, 488348897, 494544793, 59045202, 38272706, 929467881, 332606583, 202927707, 983913047, 900572428, 852467167, 843701403, 405294199]
b = [770256445, 321703391, 795371579, 399997652, 317430326, 352970811, 770146704, 575567943, 393993204, 463947364, 758576190, 119430337, 108002642, 691303269, 653733047, 450083674, 718014106, 359303638, 874692167, 25405222, 786720934, 859222166, 250646695, 186774280, 713109724, 536999564, 745315411, 536999564, 713109724, 186774280, 250646695, 859222166, 786720934, 25405222, 874692167, 359303638, 718014106, 450083674, 653733047, 691303269, 108002642, 119430337, 758576190, 463947364, 393993204, 575567943, 770146704, 352970811, 317430326, 399997652, 795371579, 321703391, 770256445, 130606453, 33519790, 272561942, 113131837, 149338964, 288304935, 467035348, 954167345, 381960298, 276898015, 598853067, 707470571, 918652223, 763677551, 712827305, 566086669, 794964330, 389423968, 708037815, 670968511, 339922625, 45348540, 668983521, 917695034, 893624186, 32170915, 947079738, 33432732, 45946169, 45946169, 33432732, 947079738, 32170915, 893624186, 917695034, 668983521, 45348540, 339922625, 670968511, 708037815, 389423968, 794964330, 566086669, 712827305, 763677551, 918652223, 707470571, 598853067, 276898015, 381960298, 954167345, 467035348, 288304935, 149338964, 113131837, 272561942, 33519790, 130606453]
r = [101, 10, 64, 7, 106, 49, 58, 15, 11, 18, 19, 85, 98, 2, 88, 48, 84, 69, 62, 6]
ans = "b211a2671936c02700fa6f4a40bcde15ad79caee561b8dde9f9473725b923d45"



N = 111
MOD = 10**9 + 7
Z_MOD = Integers(MOD)

def get_mat(x):
    transform = [[0] * N for _ in range(N)]
    for i in range(N):
        transform[i][i] = transform[i][(i+N-x)%N] = 1
    return transform

comb = [0]*N
for i in range(N):
    for j in range(N):
        comb[(i+j)%N] += a[i] * b[j]
        comb[(i+j)%N] %= MOD

comb = matrix(Z_MOD,[comb]).T
for x in r:
    comb = ~matrix(Z_MOD,get_mat(x)) * comb

shared = [x[0] for x in comb]
print(shared)

import hashlib
key = hashlib.sha256(str(shared).encode('utf-8')).hexdigest()
print(key)
print(key == ans)
