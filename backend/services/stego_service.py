from PIL import Image

def hide_key_in_image(image_path, key, output_path):
    img = Image.open(image_path)
    pixels = list(img.getdata())

    # Convert key to binary
    binary_key = ''.join(format(byte, '08b') for byte in key)

    new_pixels = []
    data_index = 0

    for pixel in pixels:
        if data_index < len(binary_key):
            new_pixel = list(pixel)

            # Modify LSB of Red channel
            new_pixel[0] = (new_pixel[0] & ~1) | int(binary_key[data_index])

            data_index += 1
            new_pixels.append(tuple(new_pixel))
        else:
            new_pixels.append(pixel)

    img.putdata(new_pixels)
    img.save(output_path)



def extract_key_from_image(image_path, key_length):
    img = Image.open(image_path)
    pixels = list(img.getdata())

    binary_key = ""

    # Extract bits from Red channel LSB
    for pixel in pixels:
        binary_key += str(pixel[0] & 1)

        if len(binary_key) >= key_length * 8:
            break

    # Convert binary to bytes
    key_bytes = bytearray()

    for i in range(0, len(binary_key), 8):
        byte = binary_key[i:i+8]
        key_bytes.append(int(byte, 2))

    return bytes(key_bytes)