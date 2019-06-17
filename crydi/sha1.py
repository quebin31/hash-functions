import numpy as np
import crydi.common as common

# =================================================================================
# Auxiliar variables
# =================================================================================
K = np.array([ 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6 ], dtype=np.uint32)

# =================================================================================
# Auxiliar functions
# =================================================================================
def F(b, c, d):
    return np.uint32((b & c) | (~b & d))

def G(b, c, d):
    return np.uint32(b ^ c ^ d)

def H(b, c, d):
    return np.uint32((b & c) | (b & d) | (c & d))

def expand_word(block, i):
    value = np.uint32(block[i - 3] ^ block[i - 8] ^ block[i - 14] ^ block[i - 16])
    return common.rotate_left(value, 1)
# =================================================================================

def digest(input_data, hex_input=False, IV=(None, None, None, None, None)):
    input_data = common.prepare_data(input_data, hex_input, little_endian=False)
    HA = np.uint32(IV[0] or 0x67452301)
    HB = np.uint32(IV[1] or 0xefcdab89)
    HC = np.uint32(IV[2] or 0x98badcfe)
    HD = np.uint32(IV[3] or 0x10325476)
    HE = np.uint32(IV[4] or 0xc3d2e1f0)

    # Iterate over each 512-bit block
    for i in range(len(input_data) // 16):
        extended_block = input_data[16 * i:16 * (i + 1)]
        for i in range(16, 80):
            extended_block.append(expand_word(extended_block, i))

        A = HA
        B = HB
        C = HC
        D = HD
        E = HE

        for j in range(80):
            if 0 <= j <= 19:
                V = F(B, C, D)
            elif 20 <= j <= 39:
                V = G(B, C, D)
            elif 40 <= j <= 59:
                V = H(B, C, D)
            else:
                V = G(B, C, D)

            V = np.uint32(common.rotate_left(A, 5) + V + E + K[j // 20] + extended_block[j])
            E = D
            D = C
            C = common.rotate_left(B, 30)
            B = A
            A = V

        HA = HA + A
        HB = HB + B
        HC = HC + C
        HD = HD + D
        HE = HE + E

    digest = [f'{HA:08x}', f'{HB:08x}', f'{HC:08x}',  f'{HD:08x}', f'{HE:08x}']
    digest = ''.join(f'{chunk}' for chunk in digest)
    return digest

if __name__ == '__main__':
    assert(digest('') == 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
    assert(digest('abc') == 'a9993e364706816aba3e25717850c26c9cd0d89d')
    assert(digest('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq') 
           == '84983e441c3bd26ebaae4aa1f95129e5e54670f1')
    assert(digest('abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu')
           == 'a49b2446a02c645bf419f995b67091253a04a259')
    print('OK!')
