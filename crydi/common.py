import struct
import numpy as np
from enum import Enum, unique

# =================================================================================
# Auxiliar variables
# =================================================================================
NUM_TYPE = {
    1: np.uint8,
    2: np.uint16,
    4: np.uint32,
    8: np.uint64,
}

@unique
class ByteFormat(Enum):
    BigEndian    = 0
    LittleEndian = 1
# =================================================================================

# =================================================================================
# Operations on words
# =================================================================================
def shift_left(x, n):
    num_type = type(x)
    return num_type(x << num_type(n))

def shift_right(x, n):
    num_type = type(x)
    return num_type(x >> num_type(n))

def rotate_left(x, n):
    num_type = type(x)
    return num_type(shift_left(x, n) | shift_right(x, 32 - n))

def rotate_right(x, n):
    num_type = type(x)
    return num_type(shift_right(x, n) | shift_left(x, 32 - n))

def little_endian(x):
    num_type = type(x)
    x = struct.pack('>I', x)
    x = int.from_bytes(x, 'little')
    return num_type(x)
# =================================================================================

# =================================================================================
# Utility functions for words
# =================================================================================
def valid_word_size(word_size):
    one_count = 0
    while word_size != 0:
        one_count += (word_size & 1)
        word_size >>= 1

    return one_count == 1
# =================================================================================

# =================================================================================
# WordsArray store words of word_size, maybe last word is less than word_size
# =================================================================================
class WordsArray:
    def __init__(self, word_size):
        self.word_size   = word_size
        self.words_array = []

    def __len__(self):
        return len(self.words_array)

    def __repr__(self):
        return self.words_array.__repr__()

    def __getitem__(self, index):
        return self.words_array[index]
    
    def __setitem__(self, index, value):
        self.words_array[index] = value

    def append(self, word, byte_format=ByteFormat.BigEndian):
        if byte_format == ByteFormat.LittleEndian:
            word = little_endian(word)

        self.words_array.append(word)
# =================================================================================


# =================================================================================
# Encode string into bytes using an encoding (default: utf-8)
# =================================================================================
def encode(input_str, encoding='utf-8'):
    bytes_array = input_str.encode(encoding)
    return [np.uint8(byte) for byte in bytes_array]
# =================================================================================

# =================================================================================
# Conver to bytes from hex string
# =================================================================================
def fromhex(hex_str):
    bytes_array = bytes.fromhex(hex_str)
    return [np.uint8(byte) for byte in bytes_array]
# =================================================================================

# =================================================================================
# Receive an array of bytes, and creates the padding so the total length 
# is congruent to rule_size[0] mod rule_size[1] (in bytes)
# =================================================================================
def perform_padding(bytes_array, start_byte=0x80, fill_byte=0x00, rule_size=(56, 64)):
    bytes_array.append(np.uint8(start_byte))

    while len(bytes_array) % rule_size[1] != rule_size[0]:
        bytes_array.append(np.uint8(fill_byte))

    return bytes_array
# =================================================================================

# =================================================================================
# Transform bytes into words of word_size (in bytes)
# =================================================================================
def bytes_to_words(bytes_array, word_size=4, byte_format=ByteFormat.BigEndian):
    if not valid_word_size(word_size) or word_size > 8:
        raise RuntimeError(f'Too big or incorrect word size ({word_size})')

    if len(bytes_array) % word_size != 0:
        raise RuntimeError(f'Word size with current number of bytes_array')

    num_type = NUM_TYPE[word_size]
    size  = 0
    word  = None
    words_array = WordsArray(word_size = word_size)

    for byte in bytes_array:
        word  = (word or num_type(0)) | num_type(byte)
        size += 1
        if size % word_size == 0:
            words_array.append(word, byte_format)
            size = 0
            word = None
        else:
            word = word << num_type(8)

    return words_array
# =================================================================================

# =================================================================================
# Append the length to the words
# =================================================================================
def append_length(words_array, length, byte_format=ByteFormat.BigEndian):
    length = int(length).to_bytes(8, 'big')
    length = bytes_to_words(length, word_size=4, byte_format=ByteFormat.BigEndian)

    if byte_format == ByteFormat.LittleEndian:
        words_array.append(length[1])
        words_array.append(length[0])
    else:
        words_array.append(length[0])
        words_array.append(length[1])

    return words_array
# =================================================================================

# =================================================================================
# Perform padding, append length and transform to little if neccessary
# =================================================================================
def prepare_data(input_data, hex_input, word_size, byte_format, encoding='utf-8'):
    input_data   = fromhex(input_data) if hex_input else encode(input_data, encoding)
    input_length = len(input_data) * 8

    input_data = perform_padding(input_data, start_byte=0x80, fill_byte=0x00, rule_size=(56, 64))
    input_data = bytes_to_words(input_data, word_size, byte_format)
    input_data = append_length(input_data, input_length, byte_format)

    return input_data
# =================================================================================
