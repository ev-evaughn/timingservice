import sys

def command():
    try:
        print('command running ...', file=sys.stderr)

        while True:
            pass
    except Exception as e:
        print(f'command exception: {st(e)}', file=sys.stderr)

if __name__ == "__main__":
    command()
