import os


def get_file_size(path: str):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for sub_path, dirs, files in os.walk(path):
        for file in files:
            total += os.path.getsize(os.path.join(sub_path, file))
    return total


def format_file_size(size: int):
    prefixes = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    for i in range(len(prefixes) - 1):
        if size < 1024:
            return f'{round(size, 2)} {prefixes[i]}B'
        size /= 1024
    return f'{round(size, 2)} {prefixes[-1]}B'
