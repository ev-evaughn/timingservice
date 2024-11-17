# The main program file for timingservice

import datetime
import db
from dotenv import load_dotenv, find_dotenv
import json
import os
import re
import subprocess
import sys
import zmq

load_dotenv(find_dotenv())

alarmProc = None
UTC = os.environ.get("UTC")

def app(name : str, port : str) -> None:
  global alarmProc

  try:
    repContext = zmq.Context()
    repSocket  = repContext.socket(zmq.REP)
    repSocket.bind("tcp://*:" + port)

  except Exception as e:
    print("Exception raised setting up zmq REP socket: ", e)
    return
  
  try:
    alarmProc = subprocess.Popen(
        ["python", "alarm.py"], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE
    )

  except Exception as e:
    print("Exception raised starting alarm.py: ", e)
    return

  print(name + " running ...")
  while True:
    inMsg = None
    try:
      inMsg = repSocket.recv_json()

    except Exception as e:
      print("Exception raised receiving: ", e)
      repSocket.send_json({
          "type":"error", 
          "payload":{
              "status":"FAILED", 
              "msg":"Json formatting error: " + str(e)
          }
      })
      continue

    outMsg = None
    try:
      outMsg = wrapper(inMsg)

    except Exception as e:
      print("Exception raised processing: ", e)
      repSocket.send_json({
        "type":"error",
        "payload":{
          "status":"FAILED",
          "msg":"Processing failled: " + str(e)
        }
      })
      continue

    try:
      repSocket.send_json(outMsg)
    except Exception as e:
      print("Exception raised sending: ", e)

def wrapper(request : object) -> object:
  requestType = request.get("type")
  if requestType == "echo":
    return request
  
  elif requestType == "set address":
    try:
      return setAddress(request)
    except Exception as e:
      return failed("set address", str(e))
    
  elif requestType == "get address":
    try:
      return getAddress(request)
    except Exception as e:
      return failed("get address", str(e))
  
  elif requestType == "set timezone":
    try:
      return setTimezone(request)
    except Exception as e:
      return failed("set timezone", str(e))
    
  elif requestType == "get timezone":
    try:
      return getTimezone(request)
    except Exception as e:
      return failed("get timezone", str(e))
  
  elif requestType == "set timer":
    try:
      return setTimer(request)
    except Exception as e:
      return failed("set timer", str(e))

  elif requestType == "set alarm":
    try:
      return setAlarm(request)
    except Exception as e:
      return failed("set alarm", str(e))

  elif requestType == "cancel":
    try:
      return cancel(request)
    except Exception as e:
      return failed("cancel", str(e))

  elif requestType == "del":
    try:
      return delete(request)
    except Exception as e:
      return failed("del", str(e))

  elif requestType == "get":
    try:
      return get(request)
    except Exception as e:
      return failed("get", str(e))

  elif requestType == "get ids":
    try:
      return getIds(request)
    except Exception as e:
      return failed("get ids", str(e))

  elif requestType == "get active":
    try:
      return getActive(request)
    except Exception as e:
      return failed("get active", str(e))

  elif requestType == "get history":
    try:
      return getHistory(request)
    except Exception as e:
      return failed("get history", str(e))
    
  else:
    return failed(requestType, "Request \"type\" not recognized.")
  
def failed(type : str, error : str) -> object:
  return {"type":type, "payload":{"status":"FAILED", "msg":error}}

def success(type: str) -> object:
  return {"type":type, "payload":{"status":"OK", "msg":None}}

def getAddress(req : object) -> object:
  raise Exception("not implemented.")

def setAddress(req : object) -> object:
  payload = req.get("payload")
  secret = req.get("from")
  if payload and secret:
    address = payload.get("address")
    if address:
      sql = f'UPDATE timingserviceUsers SET address = "{address}" WHERE ' + \
            f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}");'
      res = db.query(sql)
      
      if not res:
        return  {
                  "type":"set address",
                  "payload":{
                    "status":"OK",
                    "msg":None
                  }
                }
      else:
        raise Exception(f"DB error: {str(res)}.")
    else:
      raise Exception(f"Address missing.")
  else:
    raise Exception(f"Either payload or secret missing.")
  
def getTimezone(req : object) -> object:
  raise Exception("Not implemented.")

def setTimezone(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    timezone = payload.get("timezone")
    if timezone:
      sql = f'UPDATE timingserviceUsers SET timezone = {timezone} WHERE ' + \
            f'userID = (SELECT userID FROM timingserviceUsers WHERE ' + \
            f'secret = "{secret}");'
      res = db.query(sql)

      if not res:
        return  {
                  "type":"set timezone",
                  "payload":{
                    "status":"OK",
                    "msg":None
                  }
                }
      else:
        raise Exception(f'DB error: {str(res)}.')
      
    else:
      raise Exception(f'"timezone" missing.')
    
  else:
    raise Exception(f'"secret" or "payload" missing.')

def setTimer(req : object) -> object:
  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    name = payload.get("name")
    time = payload.get("time")
    payload = payload.get("payload")
    if name and time and payload:
      match = re.search(
          "^(?P<hour>\d{1,2})?:" + \
          "(?P<min>\d{1,2})?:" + \
          "(?P<sec>\d{1,2})?$", time)
      if match:
        matches = match.groupdict()
        hour = matches.get("hour") if matches.get("hour") else "0"
        min = matches.get("min") if matches.get("min") else "0"
        sec = matches.get("sec") if matches.get("sec") else "0"
        time = datetime.timedelta(
          seconds=int(hour),
          minutes=int(min),
          hours=int(sec)
        )
        time = time + datetime.datetime.now()
        sql = f'INSERT INTO timingserviceTimers ' + \
              f'(userID, timerName, time, payload) VALUES (' + \
              f'(SELECT userID FROM timingserviceUsers WHERE ' + \
                  f'secret = "{secret}"), ' + \
              f'"{name}", "{str(time)}", \'{json.dumps(payload)}\');'
        
        sql2 =  f'SELECT timerID FROM timingserviceTimers WHERE ' + \
                f'userID = (SELECT userID FROM timingserviceUsers ' + \
                f'WHERE secret = "{secret}") and timerName = "{name}";'

        try:
          res = db.query(sql)
          if not res:
            res = db.query(sql2)
            if res:
              return  {
                        "type":"set timer",
                        "payload":{
                          "status":"OK",
                          "msg":None,
                          "id":res[0]
                        }
                      }
            else:
              raise Exception("Failed to retrieve id from DB.")
          else:
            raise Exception(f"DB error: {str(res)}")
        
        except Exception as e:
          raise Exception(f"DB query error: {str(e)}")
      else:
        raise Exception(f'regex match failed on "time".')
    else:
      raise Exception(f'"name" or "time" or "payload" missing.')
  else:
    raise Exception(f'"secret" or "payload" missing.')

def setAlarm(req : object) -> object:
  global UTC

  secret = req.get("from")
  payload = req.get("payload")
  if secret and payload:
    name = payload.get("name")
    date = payload.get("date")
    time = payload.get("time")
    return None

  raise Exception("Not implemented.")

def cancel(req : object) -> object:
  raise Exception("Not implemented.")

def delete(req: object) -> object:
  raise Exception("Not implemented.")

def get(req: object) -> object:
  raise Exception("Not implemented.")

def getIds(req : object) -> object:
  raise Exception("Not implemented.")

def getActive(req : object) -> object:
  raise Exception("Not implemented.")

def getHistory(req : object) -> object:
  raise Exception("Not implemented.")

if __name__ == "__main__":
  args = sys.argv
  if len(args) != 2:
    print(f"Usage: python main.py PORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1])
    
    except Exception as e:
      print("Exception raised trying to start program: ", e)