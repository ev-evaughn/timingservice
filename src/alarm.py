import sys

def alarm():
    print('alarm running ...', file=sys.stderr)

    while True:
        pass

if __name__ == "__main__":
    alarm()
