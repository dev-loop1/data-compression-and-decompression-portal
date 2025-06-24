def rle_compress(data: bytes) -> bytes:

    if not data:
        return b''

    encoded = bytearray()
    i = 0
    while i < len(data):
        current_byte = data[i]
        count = 1
        i += 1
        while i < len(data) and data[i] == current_byte and count < 255:
            count += 1
            i += 1
        encoded.append(count)
        encoded.append(current_byte)
    return bytes(encoded)

def rle_decompress(data: bytes) -> bytes:
    if not data:
        return b''
        
    decoded = bytearray()
    i = 0
    while i < len(data):
        count = data[i]
        value = data[i+1]
        decoded.extend([value] * count)
        i += 2
    return bytes(decoded)