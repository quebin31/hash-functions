import re
import numpy as np

# =================================================================================
# Operations on words
# =================================================================================
def shift_left(x, n):
    return np.uint32(x << n)

def shift_right(x, n):
    return np.uint32(x >> n)

def rotate_left(x, n):
    return np.uint32(x << n) | np.uint32(x >> (32 - n))

def rotate_right(x, n):
    return np.uint32(x >> n) | np.uint32(x << (32 - n))

# =================================================================================
# data is in hex format, size is the size of each block in 4-bit words (hex digit),
# blocks is going to be an array with 32-bit words (8 hex digits) at least for its
# first n - 1 blocks, the last one can have less than 32 bits
# =================================================================================
def segmentize_data(data, block_size=8):
    block  = ''
    blocks = []

    for hex_digit in data:
        block += hex_digit
        if len(block) % block_size == 0:
            blocks.append(block)
            block = ''

    # Don't append an empty word
    if len(block) != 0:
        blocks.append(block)

    return blocks

# =================================================================================
# Receive an array of 32-bit words (@blocks) with maybe the last one less than 32 
# bits, and creates the padding so the total length is congruent to 448 mod 512
# =================================================================================
def perform_padding(blocks):
    # Get the latest block length, if blocks is empty, then it's zero
    try:
        last_block_len = len(blocks[-1]) 
    except Exception:
        last_block_len = 0

    # Append 1 to the last block and complete with 0 until it's length is 32 bits
    if last_block_len % 8 != 0:
        # It's an incomplete block (i.e. less than 32 bits)
        blocks[-1] += '8' + '0' * (7 - last_block_len)
    else:
        # The last block is complete, just append another one then
        blocks.append('8' + '0' * 7)

    # Fill with zeros until it's congruent with 448 mod 512 (bits)
    # As len(blocks) give us the number of blocks of 32 bits 
    # 448 mod 512 (bits) is equal to 14 mod 16 (32bits)
    while (len(blocks) % 16) != 14:
        blocks.append('0' * 8)

    return blocks

# =================================================================================
# Append input_length to the current blocks
# =================================================================================
def append_length(blocks, input_length, little_endian):
    # Expand length to fill 64 bits
    input_length = '0' * (16 - len(input_length)) + input_length
    input_length = segmentize_data(input_length)

    # Append the length
    if little_endian:
        blocks.append(input_length[1])
        blocks.append(input_length[0])
    else:
        blocks.append(input_length[0])
        blocks.append(input_length[1])

    return blocks

# =================================================================================
# Transform each word in blocks to little endian
# =================================================================================
def big_to_little(blocks): 
    def transform(block):
        temp = ''.join(block[i: i + 2] for i in range(len(block) - 2, -1, -2))
        return temp

    for (index, block) in enumerate(blocks):
        blocks[index] = transform(block)

    return blocks

# =================================================================================
# Self-explaining, ensure it's np.uint32
# =================================================================================
def hex_to_uint32(blocks):
    for (index, block) in enumerate(blocks):
        blocks[index] = np.uint32(int(block, 16))
    return blocks

# =================================================================================
# Is it a valid hex string?
# =================================================================================
def valid_hex(input_data):
    match = re.match('^([0-9]|[a-f]|[A-F])*$', input_data)
    return not (match is None)

def utf8_to_hex(input_data):
    return ''.join('{:x}'.format(ord(c)) for c in input_data)


# =================================================================================
# Perform padding, append length and transform to little if neccessary
# =================================================================================
def prepare_data(input_data, hex_input, little_endian):
    # Convert input_data to hex format
    if not hex_input:
        input_data = utf8_to_hex(input_data)
    else:
        if not valid_hex(input_data):
            raise RuntimeError('Invalid HEX')

    input_length = f'{np.uint64(len(input_data) * 4):x}'

    # Segmentize data and create padding 
    input_blocks = segmentize_data(input_data)
    input_blocks = perform_padding(input_blocks)

    if little_endian:
        input_blocks = big_to_little(input_blocks)

    input_blocks = append_length(input_blocks, input_length, little_endian)
    input_blocks = hex_to_uint32(input_blocks)

    return input_blocks
