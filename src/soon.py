import select
import signal
import subprocess
import sys

alarm = None

def sigHandle(signum, frame):
    global alarm

    if alarm:
        alarm.kill()
signal.signal(signal.SIGTERM, sigHandle)


def handleDB(input : str) -> str:
    return input

def handleAlarm(input : str) -> str:
    return input

def soon():
    global alarm

    try:
        print('soon running ...', file=sys.stderr)
    
        alarm = subprocess.Popen(["python", "src/alarm.py"], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               bufsize=1)
    
        while True:
            rfds, wfds, _ = select.select([sys.stdin, alarm.stdout, alarm.stderr], [sys.stdout, sys.stderr, alarm.stdin], [])
            if sys.stdin in rfds and sys.stdout in wfds:
                print(handleDB(sys.stdin.readline()), file=sys.stdout)
            if alarm.stdout in rfds and alarm.stdin in wfds:
                print(handleAlarm(alarm.stdout.readline()), file=alarm.stdin)
            if alarm.stderr in rfds and sys.stderr in wfds:
                print(alarm.stderr.readline(), file=sys.stderr, end='')
    
    except Exception as e:
        print(f'soon exception: {str(e)}', file=sys.stderr)

if __name__ == "__main__":
    soon()
