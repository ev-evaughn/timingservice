import select
import signal
import subprocess
import sys

command = None

def sigHandle(signum, frame):
    global command

    if command:
        command.kill()
signal.signal(signal.SIGTERM, sigHandle)

def handleSoon(input : str) -> str:
    return input

def handleCommand(input : str) -> str:
    return input

def db():
    global command
    
    try:
        print('db running ...', file=sys.stderr)
    
        command = subprocess.Popen(["python", "src/command.py"], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               bufsize=1, 
                               text=True)
    
        while True:
            rfds, wfds, _ = select.select(
                    [sys.stdin, command.stdout, command.stderr], 
                    [sys.stdout, sys.stderr, command.stdin], 
                    [])
            if sys.stdin in rfds and sys.stdout in wfds:
                print(handleSoon(sys.stdin.readline()), file=sys.stdout)
            if command.stdout in rfds and command.stdin in wfds:
                print(handleCommand(command.stdout.readline()), file=command.stdin)
            if command.stderr in rfds and sys.stderr in wfds:
                print(command.stderr.readline(), file=sys.stderr, end='')
    
    except Exception as e:
        print(f'db exception: {str(e)}', file=sys.stderr)

if __name__ == "__main__":
    db()
