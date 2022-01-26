import sys

BUF_SIZE = 10000

def process(size):
    size_read = 0
    while size_read < size:
        read = min(BUF_SIZE, size - size_read)
        bytes = sys.stdin.buffer.read1(read)
        sys.stdout.buffer.write(bytes)
        sys.stdout.buffer.flush()
        size_read += len(bytes)

def main():
    while True:
        # Get header (ie `Size: `)
        header = sys.stdin.buffer.read1(6)
        if header == b'':
            break

        # Get the size
        size_b = b''
        while True:
            byte = sys.stdin.buffer.read1(1)
            if byte == b'B':
                break
            size_b += byte

        # Output data
        size = int(size_b)
        process(size);
        
if __name__ == "__main__":
    main()
