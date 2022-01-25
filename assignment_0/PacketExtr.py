import sys

def main():
    while True:
        # Get header (ie `Size: `)
        header_b = sys.stdin.buffer.read1(6)
        if header_b == b'':
            break

        # Get the size
        size_b = b''
        byte = sys.stdin.buffer.read1(1)
        while byte != b'B':
            size_b += byte
            byte = sys.stdin.buffer.read1(1)

        # Output data
        size = int(size_b)
        data = sys.stdin.buffer.read1(size)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        
if __name__ == "__main__":
    main()
