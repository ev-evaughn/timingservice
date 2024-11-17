# The main program file for timingservice

import db
import subprocess
import sys
import zmq

repSocket = None
alarmProc = None

def app(name : str, port : str) -> None:
  global repSocket, alarmProc
  
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
              "msg":"Json formatting error" + str(e)
          }
      })
      continue

    repSocket.send_json(wrapper(inMsg))

def wrapper(request : object) -> object:
  requestType = request.get("type")
  if requestType == "echo":
    return request
  
  elif requestType == "set address":
    return setAddress(request)
  
  elif requestType == "set timezone":
    return setTimezone(request)
  
  elif requestType == "set timer":
    return setTimer(request)

  elif requestType == "set alarm":
    return setAlarm(request)

  elif requestType == "cancel":
    return cancel(request)

  elif requestType == "del":
    return delete(request)

  elif requestType == "get":
    return get(request)

  elif requestType == "get ids":
    return getIds(request)

  elif requestType == "get active":
    return getActive(request)

  elif requestType == "get history":
    return getHistory(request)

def setAddress(req : object) -> object:
  return None

def setTimezone(req : object) -> object:
  return None

def setTimer(req : object) -> object:
  return None

def setAlarm(req : object) -> object:
  return None

def cancel(req : object) -> object:
  return None

def delete(req: object) -> object:
  return None

def get(req: object) -> object:
  return None

def getIds(req : object) -> object:
  return None

def getActive(req : object) -> object:
  return None

def getHistory(req : object) -> object:
  return None

if __name__ == "__main__":
  args = sys.argv
  if len(args) != 2:
    print(f"Usage: python main.py PORT")

  else:
    try:
      app(sys.argv[0], sys.argv[1])
    
    except Exception as e:
      print("Exception raised trying to start program: ", e)