import heapq
import json
from collections import defaultdict

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        if not isinstance(other, HuffmanNode):
            return NotImplemented
        return self.freq < other.freq

def make_frequency_dict(data: bytes) -> dict:
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1
    return freq

def make_heap(frequency: dict) -> list:
    heap = []
    for key, value in frequency.items():
        node = HuffmanNode(str(key), value)
        heapq.heappush(heap, node)
    return heap

def merge_nodes(heap: list):
    if not heap:
        return None
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left, merged.right = node1, node2
        heapq.heappush(heap, merged)
    return heap[0]

def make_codes_helper(root: HuffmanNode, current_code: str, codes: dict):
    if root is None:
        return
    if root.char is not None:
        codes[root.char] = current_code
        return
    make_codes_helper(root.left, current_code + "0", codes)
    make_codes_helper(root.right, current_code + "1", codes)

def make_codes(root: HuffmanNode) -> dict:
    codes = {}
    if root is None:
        return codes
    if root.char is not None and not root.left and not root.right:
         codes[root.char] = "0"
    else:
        make_codes_helper(root, "", codes)
    return codes
    
def get_encoded_text(data: bytes, codes: dict) -> str:
    encoded_text = ""
    for byte in data:
        encoded_text += codes[str(byte)]
    return encoded_text

def pad_encoded_text(encoded_text: str) -> str:
    extra_padding = 8 - len(encoded_text) % 8
    if extra_padding == 8:
        extra_padding = 0
    padded_encoded_text = encoded_text + ('0' * extra_padding)
    padding_info = "{0:08b}".format(extra_padding)
    return padding_info + padded_encoded_text

def get_byte_array(padded_encoded_text: str) -> bytearray:
    if len(padded_encoded_text) % 8 != 0:
        raise ValueError("Encoded text length must be a multiple of 8")
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

def huffman_compress(data: bytes) -> bytes:
    if not data:
        return b''
    frequency = make_frequency_dict(data)
    heap = make_heap(frequency)
    root = merge_nodes(heap)
    codes = make_codes(root)
    encoded_text = get_encoded_text(data, codes)
    padded_encoded_text = pad_encoded_text(encoded_text)
    compressed_byte_array = get_byte_array(padded_encoded_text)
    freq_map_for_json = {str(k): v for k, v in frequency.items()}
    header = json.dumps(freq_map_for_json).encode('utf-8')
    header_len = len(header).to_bytes(4, 'big')
    return header_len + header + compressed_byte_array

def huffman_decompress(data: bytes) -> bytes:
    if not data:
        return b''
    header_len = int.from_bytes(data[:4], 'big')
    header = json.loads(data[4:4+header_len].decode('utf-8'))
    compressed_data = data[4+header_len:]
    frequency = {int(k): v for k, v in header.items()}
    
    if len(frequency) == 1:
        char_val = list(frequency.keys())[0]
        count = list(frequency.values())[0]
        return bytes([char_val] * count)

    heap = make_heap(frequency)
    root = merge_nodes(heap)
    codes = make_codes(root)
    codes_inverted = {v: k for k, v in codes.items()}
    encoded_bits = "".join(f"{byte:08b}" for byte in compressed_data)
    padding_info = encoded_bits[:8]
    extra_padding = int(padding_info, 2)
    encoded_bits = encoded_bits[8:]
    if extra_padding > 0:
        encoded_bits = encoded_bits[:-extra_padding]
    decoded_bytes = bytearray()
    current_code = ""
    for bit in encoded_bits:
        current_code += bit
        if current_code in codes_inverted:
            character = int(codes_inverted[current_code])
            decoded_bytes.append(character)
            current_code = ""
    return bytes(decoded_bytes)
