import datetime
import json
import threading
import select
import signal
import subprocess
import sys

alarmProc = None
alarms = {}
alarms_lock = threading.Lock()

def sigHandle(signum, frame):
    global alarmProc

    if alarmProc:
        alarmProc.send_signal(signal.SIGTERM)
    sys.exit()
signal.signal(signal.SIGTERM, sigHandle)

def handleDB(input : str) -> None:
    global alarms, alarms_lock

    try:
        #print(input, file=sys.stderr)
        alarm = json.loads(input)
        id = alarm.get("timerID")
        ack = alarm.get("ack")
        with alarms_lock:
            if ack and id in alarms.keys():
                alarms.pop(id)
            elif not ack and not id in alarms.keys():
                alarms[id] = alarm
                #print(f'id: {str(id)}, ack: {str(ack)}, alarm: {str(alarm)}, alarms: {str(alarms)}', file=sys.stderr)
    except Exception as e:
        print(f'soon handleDB exception: {str(e)}', file=sys.stderr)

def handleAlarm(input : str) -> str:
    global alarms, alarms_lock

    try:
        print(f'soon handleAlarm input: {input}', file=sys.stderr)
        ack = json.loads(input)
        id = ack.get("id")
        with alarms_lock:
            if id in alarms.keys():
                alarms.pop(id)
        return input
    except Exception as e:
        print(f'soon handleAlarm exception: {str(e)}', file=sys.stderr)
        return ''

def send():
    global alarms, alarmProc, alarms_lock

    while True:
        try:
            now = datetime.datetime.now()
            with alarms_lock:
                toRM = []
                for id, alarm in alarms.items():
                    time = None
                    #print(f'soon send alarm: {str(alarm)}, id: {str(id)}', file=sys.stderr)
                    try:
                        time = datetime.datetime.strptime(alarm.get("time"), '%Y-%m-%d %H:%M:%S.%f')
                    except:
                        try:
                            time = datetime.datetime.strptime(alarm.get("time"), '%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            print(f'soon datetime exception: {str(e)}', file=sys.stderr)
                            toRM.append(id)
                    if time and time <= now:
                        #print(f'From soon to alarm: {json.dumps(alarm)}', file=sys.stderr)
                        print(json.dumps(alarm), file=alarmProc.stdin)
                        alarmProc.stdin.flush()
                for r in toRM:
                    alarms.pop(r)

        except Exception as e:
            print(f'soon send exception: {str(e)}', file=sys.stderr)

def soon():
    global alarms, alarmProc

    try:
        alarmProc = subprocess.Popen(["python", "src/alarm.py"], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               bufsize=1)
    
        sendThread = threading.Thread(target=send)
        sendThread.start()
        print('soon running ...', file=sys.stderr)
        while True:
            rfds, wfds, _ = select.select([sys.stdin, alarmProc.stdout, alarmProc.stderr], [sys.stdout, sys.stderr], [])
            if sys.stdin in rfds:
                handleDB(sys.stdin.readline())
            if alarmProc.stdout in rfds and sys.stdout in wfds:
                print(handleAlarm(alarmProc.stdout.readline()), file=sys.stdout)
                sys.stdout.flush()
            if alarmProc.stderr in rfds and sys.stderr in wfds:
                print(alarmProc.stderr.readline(), file=sys.stderr, end='')

    except Exception as e:
        print(f'soon exception: {str(e)}', file=sys.stderr)
        sendThread.join()

if __name__ == "__main__":
    soon()
