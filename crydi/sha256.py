import numpy as np
import crydi.common as common

# =================================================================================
# Auxiliar variables
# =================================================================================
BLOCK_SIZE = 64

K = np.array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
])

# =================================================================================
# Auxiliar functions
# =================================================================================
def CH(x, y, z):
    return np.uint32((x & y) ^ (~x & z))

def MAJ(x, y, z):
    return np.uint32((x & y) ^ (x & z) ^ (y & z))

def BSIG0(x):
    return np.uint32(common.rotate_right(x, 2) ^ common.rotate_right(x, 13) ^ common.rotate_right(x, 22))

def BSIG1(x):
    return np.uint32(common.rotate_right(x, 6) ^ common.rotate_right(x, 11) ^ common.rotate_right(x, 25))

def SSIG0(x):
    return np.uint32(common.rotate_right(x, 7) ^ common.rotate_right(x, 18) ^ common.shift_right(x, 3))

def SSIG1(x):
    return np.uint32(common.rotate_right(x, 17) ^ common.rotate_right(x, 19) ^ common.shift_right(x, 10))

def expand_word(block, i):
    s0 = np.uint32(block[i - 16] + SSIG0(block[i - 15]))
    s1 = np.uint32(block[i -  7] + SSIG1(block[i -  2]))
    return np.uint32(s0 + s1)
# =================================================================================

def digest(input_data, hex_input=False, encoding='utf-8'):
    input_data = common.prepare_data(
        input_data  = input_data,
        hex_input   = hex_input,
        word_size   = 4,
        byte_format = common.ByteFormat.BigEndian,
        encoding    = encoding
    )

    HA = np.uint32(0x6a09e667)
    HB = np.uint32(0xbb67ae85)
    HC = np.uint32(0x3c6ef372)
    HD = np.uint32(0xa54ff53a)
    HE = np.uint32(0x510e527f)
    HF = np.uint32(0x9b05688c)
    HG = np.uint32(0x1f83d9ab)
    HH = np.uint32(0x5be0cd19)

    # Iterate over each 512-bit block
    for i in range(len(input_data) // 16):
        extended_block = input_data[16 * i:16 * (i + 1)]
        for i in range(16, 64):
            extended_block.append(expand_word(extended_block, i))

        A = HA
        B = HB
        C = HC
        D = HD
        E = HE
        F = HF
        G = HG
        H = HH

        for j in range(64):
            T1 = np.uint32(H + BSIG1(E) + CH(E, F, G) + K[j] + extended_block[j])
            T2 = np.uint32(BSIG0(A) + MAJ(A, B, C))
            H  = G
            G  = F
            F  = E
            E  = np.uint32(D + T1)
            D  = C
            C  = B 
            B  = A
            A  = np.uint32(T1 + T2)

        HA = HA + A
        HB = HB + B
        HC = HC + C
        HD = HD + D
        HE = HE + E
        HF = HF + F
        HG = HG + G
        HH = HH + H

    digest = [
        f'{HA:08x}', f'{HB:08x}', f'{HC:08x}', f'{HD:08x}', 
        f'{HE:08x}', f'{HF:08x}', f'{HG:08x}', f'{HH:08x}',
    ]
    digest = ''.join(f'{chunk}' for chunk in digest)
    return digest

if __name__ == '__main__':
    assert(digest('') ==
           'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
    assert(digest('abc') ==
           'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    assert(digest('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq') ==
           '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1')
    assert(digest('abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu')
           == 'cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1')
    assert(digest('ó')
           == 'aa2f86f8e3c3e2237b6c42bcb824f41402eed1c9b9a16bb80576c2002c4c01e3')
    print('OK!')


