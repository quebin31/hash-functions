import crydi.md4 as md4
import crydi.md5 as md5
import crydi.sha1 as sha1
import crydi.sha256 as sha256 
import crydi.common as common

HASH_FN = {
    'MD4': md4,
    'MD5': md5,
    'SHA-1': sha1,
    'SHA-256': sha256,
}

def digest(input_data, hash_fn, key, hex_input=False, hex_key=True, encoding='utf-8'):
    if not key:
        raise RuntimeError('Not given key!')

    hash_fn    = HASH_FN[hash_fn]
    block_size = hash_fn.BLOCK_SIZE

    key = common.fromhex(key) if hex_key else common.encode(key, encoding)
    if len(key) > block_size:
        key = ''.join(f'{byte:02x}' for byte in key)
        key = hash_fn.digest(key, hex_input=True, encoding=encoding)
        key = common.fromhex(key)

    while len(key) != block_size:
        key.append(0x00)

    ipad = 0x36
    opad = 0x5c

    kipad = [k ^ ipad for k in key]
    kopad = [k ^ opad for k in key]

    if not hex_input:
        input_data = common.encode(input_data, encoding=encoding)
    else:
        input_data = common.fromhex(input_data)

    data   = ''.join(f'{byte:02x}' for byte in (kipad + input_data))
    output = hash_fn.digest(data, hex_input=True)

    data   = ''.join(f'{byte:02x}' for byte in kopad) + output
    output = hash_fn.digest(data, hex_input=True)

    return output

if __name__ == '__main__':
    assert(digest('Hi There', 'MD5', '0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b')
           == '9294727a3638bb1c13f48ef8158bfc9d')
    assert(digest('54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a65204b6579202d2048617368204b6579204669727374',
                  'SHA-256', 'aa' * 131, hex_input=True)
           == '60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54')

    print('OK!')
