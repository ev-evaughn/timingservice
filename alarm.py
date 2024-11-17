import datetime
import db
import json
import threading
import select
import sys
import time
import zmq

alarms = {}
alarms_lock = threading.Lock()
threads = []
threads_lock = threading.Lock()

context = zmq.Context()
socket = context.socket(zmq.REQ)

def app() -> None:
  dbThread = threading.Thread(target=readFromDatabase)
  inThread = threading.Thread(target=readFromStdin)
  alarmThread = threading.Thread(target=sendAlarms)
  
  with threads_lock:
    dbThread.start()
    inThread.start()
    alarmThread.start()
    threads = [dbThread, inThread, alarmThread]

  while True:
    print("main sleep", file=sys.stderr)
    time.sleep(10)
    with threads_lock:
      for thread in threads:
        if not thread.is_alive():
          thread.join(1)

def sendAlarm(alarm):
  global socket, alarms, alarms_lock

  id = alarm.get("timerID")
  name = alarm.get("timerName")
  payload = alarm.get("payload")
  address = alarm.get("address")

  print(f'trigger id: {str(id)}')
  try:
    socket.connect(address)
  except Exception as e:
    print(f'Alarm send connect error: {str(e)}', file=sys.stderr)

  try:
    socket.send_json({"id":id, "name":name, "payload":payload})
  except Exception as e:
    print(f'Alarm send error: {str(e)}', file=sys.stderr)

  msg = None
  try:
    msg = socket.recv_json()
  except Exception as e:
    print(f'Alarm recv error: {str(e)}', file=sys.stderr)

  if msg:
    id = msg.get("id")
    if id:
      now = None
      try:
        now = str(datetime.datetime.now())
      except Exception as e:
        print(f'Alarm send datetime error: {str(e)}', file=sys.stderr)

      if now:
        id = now.get("timerID")
        if id:
          sql = f'UPDATE timingserviceTimers SET ack = "{now}" WHERE ' + \
              f'timerID = {now.get("timerID")};'
          res = None
          try:
            res = db.query(sql)
          except Exception as e:
            print(f'Alarm send DB error: {str(e)}', file=sys.stderr)

          if res:
            print(f'Alarm send db error: {str(res)}', file=sys.stderr)
          else:
            with alarms_lock:
              alarms.pop(id)

def sendAlarms():
  global alarms, threads, alarms_lock, threads_lock

  while True:
    #print("sending", file=sys.stderr)
    now = None
    toSend = []

    try:
      now = str(datetime.datetime.now())
    except Exception as e:
      print(f"Alarm send datetime error: {str(e)}", file=sys.stderr)

    try:
      with alarms_lock:
        for alarm in alarms.values():
          print(alarm, file=sys.stderr)
          print(type(alarm), file=sys.stderr)
          time.sleep(3)
          return
          #if alarm.get("time") >= now:
          #  print("Adding alarm to send list", file=sys.stderr)
          #  toSend.append(alarm)
    except Exception as e:
        print(f'Alarm send lock error: {str(e)}', file=sys.stderr)

    if toSend:
      for alarm in toSend:
        with threads_lock:
          thread = threading.Thread(target=sendAlarm, args=(alarm,))
          thread.start()
          threads.append(thread)
        


def readFromStdin():
  global alarms, alarms_lock

  while True:
    print('Select starting', file=sys.stderr)
    rlist, _, _ = select.select([sys.stdin], [], [])
    for fd in rlist:
      msg = fd.readline()
      if msg:
        alarm = None
        try:
          alarm = json.loads(msg)
        except Exception as e:
          print(f'Alarms stdin json error: {str(e)}', file=sys.stderr)

        if alarm:
          id = alarm.get("timerID")
          if id:
            if alarm.get("ack"):
              with alarms_lock:
                if id in alarms.keys():
                  alarms.pop(id)
            else:
              with alarms_lock:
                if id not in alarms.keys():
                  alarms[id] = alarm

def readFromDatabase():
  global alarms, alarms_lock

  sql = 'SELECT timerID, timerName, time, payload, address FROM timingserviceTimers JOIN timingserviceUsers ON timingserviceTimers.userID = timingserviceUsers.userID WHERE time <= "{}" AND ack IS NULL;'
  while True:
    now = None
    later = None
    res = None

    try:
      now = datetime.datetime.now()
      later = now + datetime.timedelta(minutes=10)
    except Exception as e:
      print(f"Alarm DB datetime error: {str(e)}", file=sys.stderr)

    if now and later:
      try:
        sql2 = sql.format(later)
        print(sql2, file=sys.stderr)
        res = db.query(sql.format(later))
        print(f'from db: {str(res)}')
      except Exception as e:
        print(f"Alarm DB read from DB error: {str(e)}", file=sys.stderr)

    if res:
      try:
        with alarms_lock:
          for r in res:
            id = r.get("timerID")
            if id not in alarms.keys():
              alarms[id] = r
      except Exception as e:
        print(f'Alarm DB update error: {str(e)}', file=sys.stderr)

    res = None
    try:
      res = db.query('SELECT timerID FROM timingserviceTimers WHERE ack IS NOT NULL')
    except Exception as e:
      print(f'Alarm DB read ack error: {str(e)}', file=sys.stderr)

    if res:
      try:
        with alarms_lock:
          for r in res:
            id = r.get("timerID")
            if id in alarms.keys():
              alarms.pop(id)
      except Exception as e:
        print(f'Alarm DB rm update error: {str(e)}', file=sys.stderr)

    try:
      pass
      #print('DB search going to sleep', file=sys.stderr)
      time.sleep(10)#300)
    except Exception as e:
      print(f'Alarm DB sleep error: {str(e)}', file=sys.stderr)

# Start program
if __name__ == "__main__":
  args = sys.argv
  if len(args) != 1:
    print("Usage: python alarm.py", file=sys.stderr)

  else:
    try:
      app()

    except Exception as e:
      print(f"Exception starting alarm: {str(e)}", file=sys.stderr)