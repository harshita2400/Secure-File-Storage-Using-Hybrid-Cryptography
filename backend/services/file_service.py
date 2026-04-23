def split_file(file_bytes):
    size = len(file_bytes) // 3
    return (
        file_bytes[:size],
        file_bytes[size:2*size],
        file_bytes[2*size:]
    )