import crydi.md4 as md4
import crydi.md5 as md5
import crydi.sha1 as sha1
import crydi.sha256 as sha256 
import crydi.common as common
import numpy as np

def digest(input_data, hash_fn, key, hex_input=False, hex_key=True, bsize=64):
    if not key:
        raise RuntimeError('Not given key!')

    if hash_fn == 'MD4':
        hash_fn = md4
    elif hash_fn == 'MD5':
        hash_fn = md5
    elif hash_fn == 'SHA-1':
        hash_fn = sha1
    elif hash_fn == 'SHA-256':
        hash_fn = sha256
    else: 
        raise RuntimeError(f'Unknown hash function {hash_fn}')

    if not hex_key:
        key = common.utf8_to_hex(key)

    if len(key) > (bsize * 2):
        key = hash_fn.digest(key, hex_input=True)

    key += '0' * (bsize * 2 - len(key))
    key = common.hex_to_uint32(common.segmentize_data(key))

    i32 = np.uint32(int('36' * 4, 16))
    o32 = np.uint32(int('5c' * 4, 16))

    kipad = ''.join(f'{k ^ i32:08x}' for k in key)
    kopad = ''.join(f'{k ^ o32:08x}' for k in key)

    if not hex_input:
        input_data = common.utf8_to_hex(input_data)

    output = hash_fn.digest(kipad + input_data, hex_input=True)
    output = hash_fn.digest(kopad + output, hex_input=True)

    return output

if __name__ == '__main__':
    assert(digest('Hi There', 'MD5', '0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b')
           == '9294727a3638bb1c13f48ef8158bfc9d')
    assert(digest('54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a65204b6579202d2048617368204b6579204669727374',
                  'SHA-256', 'aa' * 131, hex_input=True)
           == '60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54')

    print('OK!')
