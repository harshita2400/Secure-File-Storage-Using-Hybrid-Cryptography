from stego_service import extract_key_from_image

key = extract_key_from_image("../stego/stego_test.txt.png", 56)
print(key)