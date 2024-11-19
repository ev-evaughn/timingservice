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

def app() -> None:
  #time.sleep(5)

  #dbThread = threading.Thread(target=readFromDatabase)
  inThread = threading.Thread(target=readFromStdin)
  alarmThread = threading.Thread(target=sendAlarms)
  
  #dbThread.start()
  inThread.start()
  alarmThread.start()

  #dbThread.join()
  inThread.join()
  alarmThread.join()

def sendAlarm(alarm):
  global socket, alarms, alarms_lock

  id = alarm.get("timerID")
  name = alarm.get("timerName")
  payload = alarm.get("payload")
  address = alarm.get("address")

  context = zmq.Context()
  socket = context.socket(zmq.REQ)

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
        id = msg.get("id")
        if id:
          sql = f'UPDATE timingserviceTimers SET ack = "{now}" WHERE ' + \
              f'timerID = {id};'
          res = None
          try:
            res = db.query(sql)
          except Exception as e:
            print(f'Alarm send DB error: {str(e)}', file=sys.stderr)

          if res:
            print(f'Alarm send db error: {str(res)}', file=sys.stderr)
          else:
            print('Asking for lock 1')
            with alarms_lock:
              if id in alarms.keys():
                alarms.pop(id)

def sendAlarms():
  global alarms, threads, alarms_lock, threads_lock

  while True:
    #print("sending", file=sys.stderr)
    #with alarms_lock:
     #   print(str(alarms), file=sys.stderr)

    now = None
    toSend = []

    try:
      now = datetime.datetime.now()
    except Exception as e:
      print(f"Alarm send datetime error: {str(e)}", file=sys.stderr)

    try:
      #print('Askin for lock 3', file=sys.stderr)
      with alarms_lock:
        #print(f'lock 3 aquired: {str(alarms_lock.locked())}', file=sys.stderr)
        for alarm in alarms.values():
          #print(alarm, file=sys.stderr)
          #print(type(alarm), file=sys.stderr)
          #time.sleep(3)
          time = None
          try:
            time = datetime.datetime.strptime(alarm.get("time"), '%Y-%m-%d %H:%M:%S')
          except:
            try:
              time = datetime.datetime.strptime(alarm.get("time"), '%Y-%m-%d %H:%M:%S.%f')
            except:
              raise Exception("unable to match time format")
          if time <= now:
            print("Adding alarm to send list", file=sys.stderr)
            toSend.append(alarm)
      #print(f'lock 3 aquired: {str(alarms_lock.locked())}', file=sys.stderr)

    except Exception as e:
        print(f'Alarm send lock error: {str(e)}', file=sys.stderr)

    #time.sleep(3)
    if toSend:
      for alarm in toSend:
        sendAlarm(alarm)  
        


def readFromStdin():
  global alarms, alarms_lock

  while True:
    try:
      try:
        fd, _, _ = select.select([sys.stdin], [], [], 3)
        #print(f'fd: {str(fd)}, type: {str(type(fd))}', file=sys.stderr)
        if fd:
          try:
            #msg = fd[0].readline()
            msg = input()
            #print(f'From alarm msg: {msg}', file=sys.stderr)
            try:
              alarm = json.loads(msg)
              try:
                print(f'alarm: {str(alarm)}', file=sys.stderr)
                id = alarm.get("timerID")
                ack = alarm.get("ack")
                if id:
                  if ack:
                    print('Asking for lock 4', file=sys.stderr)
                    with alarms_lock:
                      if id in alarms.keys():
                        alarms.pop(id)
                  else:
                    try:
                      pass
                      #alarm["time"] = datetime.strptime(alarm["time"], '%Y-%m-%d %H:%M:%S.%f')
                    except Exception as e:
                      print(f'Alarm stdin str to time error: {str(e)}', file=sys.stderr)
                    print('Asking for lock 5', file=sys.stderr)
                    with alarms_lock:
                      alarms[id] = alarm
                else:
                  print('Alarm stdin no id', file=sys.stderr)
              except Exception as e:
                print(f'Alarm stdin process alarm exception: {str(e)}', file=sys.stderr)
            except Exception as e:
              print(f'Alarm stdin json exception: {str(e)}', file=sys.stderr)
          except Exception as e:
            print(f'Alarm stdin read error: {str(e)}', file=sys.stderr)
        else:
          print('Alarm stdin nothing read in', file=sys.stderr)
      except Exception as e:
        print(f'Alarm stdin select error: {str(e)}', file=sys.stderr)
    except Exception as e:
      print(f'Alarm stdin loop error: {str(e)}', file=sys.stderr)

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
        #print(sql2, file=sys.stderr)
        res = db.query(sql.format(later))
        #print(f'from db: {str(res)}')
      except Exception as e:
        print(f"Alarm DB read from DB error: {str(e)}", file=sys.stderr)

    if res:
      try:
        print('Asking for lock 6')
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
        print('Asking for lock 7')
        with alarms_lock:
          for r in res:
            id = r.get("timerID")
            if id in alarms.keys():
              alarms.pop(id)
      except Exception as e:
        print(f'Alarm DB rm update error: {str(e)}', file=sys.stderr)

    try:
      #pass
      #print('DB search going to sleep', file=sys.stderr)
      time.sleep(300)
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
