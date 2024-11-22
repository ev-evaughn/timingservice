import commandHandle
import json
import select
import signal
import subprocess
import sys

command = None

def sigHandle(signum, frame):
    global command

    if command:
        command.send_signal(signal.SIGTERM)
    sys.exit()
signal.signal(signal.SIGTERM, sigHandle)

def handleCommand(input : str) -> str:
    try:
        #print(f'db input {input}', file=sys.stderr)
        msg = json.loads(input)
        rsp = commandHandle.wrapper(msg)
        return json.dumps(rsp)
    except Exception as e:
        print(f'db handleCommand exception: {str(e)}', file=sys.stderr)
        return ''

def handleAck(input : str) -> None:
    ack = json.loads(input)
    id = ack.get("id")
    secret = ack.get("from")
    commandHandle.ack(secret, id)

def db():
    global command
    
    try:
        command = subprocess.Popen(["python", "src/command.py"], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               bufsize=1, 
                               text=True)
    
        print('db running ...', file=sys.stderr)
        while True:
            rfds, wfds, _ = select.select(
                    [sys.stdin, command.stdout, command.stderr], 
                    [sys.stdout, sys.stderr, command.stdin], 
                    [])
            if sys.stdin in rfds:
                handleAck(sys.stdin.readline())
            if command.stdout in rfds and command.stdin in wfds:
                print(handleCommand(command.stdout.readline()), file=command.stdin)
                command.stdin.flush()
            if command.stderr in rfds and sys.stderr in wfds:
                print(command.stderr.readline(), file=sys.stderr, end='')
    
    except Exception as e:
        print(f'db exception: {str(e)}', file=sys.stderr)

if __name__ == "__main__":
    db()
