import numpy as np
import crydi.common as common

# =================================================================================
# Auxiliar variables
# =================================================================================
BLOCK_SIZE = 64

S = np.array([[7, 12, 17, 22], [5, 9, 14, 20], [4, 11, 16, 23], [6, 10, 15, 21]])

T  = np.array([
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
], dtype=np.uint32)
# =================================================================================

# =================================================================================
# Auxiliar functions
# =================================================================================
def F(b, c, d):
    return np.uint32((b & c) | (~b & d))

def G(b, c, d):
    return np.uint32((b & d) | (c & ~d))

def H(b, c, d):
    return np.uint32(b ^ c ^ d)

def I(b, c, d):
    return np.uint32(c ^ (b | ~d))
# =================================================================================

def digest(input_data, hex_input=False, encoding='utf-8'):
    input_data = common.prepare_data(
        input_data  = input_data,
        hex_input   = hex_input,
        word_size   = 4,
        byte_format = common.ByteFormat.LittleEndian,
        encoding    = encoding
    )

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

        for j in range(64):
            if 0 <= j <= 15:
                V = F(B, C, D)
                g = j
            elif 16 <= j <= 31:
                V = G(B, C, D)
                g = (5 * j + 1) % 16
            elif 32 <= j <= 47:
                V = H(B, C, D)
                g = (3 * j + 5) % 16
            else:
                V = I(B, C, D)
                g = (7 * j) % 16

            V = np.uint32(V + A + T[j] + input_data[16*i + g])
            A = D 
            D = C
            C = B 
            B = np.uint32(B + common.rotate_left(V, S[j // 16][j % 4]))
    
        A = A + OLD_A
        B = B + OLD_B
        C = C + OLD_C
        D = D + OLD_D

    A = common.little_endian(A)
    B = common.little_endian(B)
    C = common.little_endian(C)
    D = common.little_endian(D)
    digest = [f'{A:08x}', f'{B:08x}', f'{C:08x}',  f'{D:08x}']
    digest = ''.join(f'{digest[i]}' for i in range(0, 4))
    return digest

if __name__ == '__main__':
    assert(digest('') == 'd41d8cd98f00b204e9800998ecf8427e')
    assert(digest('a') == '0cc175b9c0f1b6a831c399e269772661')
    assert(digest('abc') == '900150983cd24fb0d6963f7d28e17f72')
    assert(digest('message digest') == 'f96b697d7cb7938d525a2f31aaf161d0')
    assert(digest('abcdefghijklmnopqrstuvwxyz') == 'c3fcd3d76192e4007dfb496cca67e13b')
    assert(digest('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') 
           == 'd174ab98d277d9f5a5611c2c9f419d9f')
    assert(digest('12345678901234567890123456789012345678901234567890123456789012345678901234567890')
           == '57edf4a22be3c955ac49da2e2107b67a')
    assert(digest('ó') == '5ab838a6f466a5fe1ddbc08340cc21f1')
    print('OK!')
