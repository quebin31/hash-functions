import numpy as np
import crydi.common as common

# =================================================================================
# Auxiliar variables
# =================================================================================
S = np.array([[3, 7, 11, 19], [3, 5, 9, 13], [3, 9, 11, 15]]) 

THIRD_ROUND = np.array([
    0,  8, 4, 12,
    2, 10, 6, 14,
    1,  9, 5, 13, 
    3, 11, 7, 15,
])

# =================================================================================
# Auxiliar functions
# =================================================================================
def F(x, y, z):
    return np.uint32((x & y) | (~x & z))

def G(x, y, z):
    return np.uint32((x & y) | (x & z) | (y & z))

def H(x, y, z):
    return np.uint32(x ^ y ^ z)
# =================================================================================

def digest(input_data, hex_input=False):
    input_data = common.prepare_data(input_data, hex_input, little_endian=True)
    A = np.uint32(0x67452301)
    B = np.uint32(0xefcdab89)
    C = np.uint32(0x98badcfe)
    D = np.uint32(0x10325476)

    # Iterate over each 512-bit block
    for i in range(len(input_data) // 16):
        OLD_A = A
        OLD_B = B
        OLD_C = C
        OLD_D = D

        for j in range(48):
            if 0 <= j <= 15:
                V = F(B, C, D)
                g = j
            elif 16 <= j <= 31:
                V = G(B, C, D) + np.uint32(0x5a827999)
                g = (4 * (j - 1) + j // 4) % 16
            elif 32 <= j <= 47:
                V = H(B, C, D) + np.uint32(0x6ed9eba1)
                g = THIRD_ROUND[j % 16]

            V = np.uint32(V + A + input_data[16*i + g])
            A = D 
            D = C
            C = B 
            B = common.rotate_left(V, S[j // 16][j % 4])

        A = A + OLD_A
        B = B + OLD_B
        C = C + OLD_C
        D = D + OLD_D

    digest = [f'{A:08x}', f'{B:08x}', f'{C:08x}',  f'{D:08x}']
    digest = common.big_to_little(digest)
    digest = ''.join(f'{digest[i]}' for i in range(0, 4))
    return digest

if __name__ == '__main__':
    assert(digest('') == '31d6cfe0d16ae931b73c59d7e0c089c0')
    assert(digest('a') == 'bde52cb31de33e46245e05fbdbd6fb24')
    assert(digest('abc') == 'a448017aaf21d8525fc10ae87aa6729d')
    assert(digest('message digest') == 'd9130a8164549fe818874806e1c7014b')
    assert(digest('abcdefghijklmnopqrstuvwxyz') == 'd79e1c308aa5bbcdeea8ed63df412da9')
    assert(digest('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') 
           == '043f8582f241db351ce627e153e7f0e4')
    assert(digest('12345678901234567890123456789012345678901234567890123456789012345678901234567890')
           == 'e33b4ddc9c38f2199c3e7b164fcc0536')

    print('OK!')
