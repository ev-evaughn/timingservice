import dotenv
import os
import select
import signal
import subprocess
import sys
import zmq

def app(name : str) -> int:
    try:
        db = subprocess.Popen(
                ["python", "src/db.py"], 
                bufsize=1, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True)
        soon = subprocess.Popen(
                ["python", "src/soon.py"], 
                bufsize=1, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True)

        rlist = [db.stdout, db.stderr, soon.stdout, soon.stderr, sys.stdin]
        wlist = [db.stdin, soon.stdin, sys.stdout, sys.stderr]

        print(f'{name} running ...')
        while True:
            rfds, wfds, _ = select.select(rlist, wlist, [])
            if db.stdout in rfds and soon.stdin in wfds:
                print(db.stdout.readline(), file=soon.stdin, end='')
            if db.stderr in rfds and sys.stderr in wfds:
                print(db.stderr.readline(), file=sys.stderr, end='')
            if soon.stdout in rfds and db.stdin in wfds:
                print(soon.stdout.readline(), file=db.stdin, end='')
            if soon.stderr in rfds and sys.stderr in wfds:
                print(soon.stderr.readline(), file=sys.stderr, end='')
            if sys.stdin in rfds:
                if sys.stdin.readline() == "quit\n":
                    db.send_signal(signal.SIGTERM)
                    soon.send_signal(signal.SIGTERM)
                    break
        return 0

    except Exception as e:
        print(f'{name} exception: {str(e)}')
        return 1

if __name__ == "__main__":
    args = sys.argv
    dotenv.load_dotenv(dotenv.find_dotenv())

    if len(args) == 1:
        if os.environ.get("DBHOST") and \
                os.environ.get("DBUSER") and \
                os.environ.get("DBPASS") and \
                os.environ.get("DBNAME") and \
                os.environ.get("UTC") and \
                os.environ.get("BINDADDR"):
            app(sys.argv[0])
        else:
            print('.env missing variables')
    else:
        print('Usage: nohup python app.py')

